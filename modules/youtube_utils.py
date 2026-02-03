import socket
import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs
import whisper
import yt_dlp
import os
import shutil

# ==========================================
# 🛠️ DNS FIX + FILE SYSTEM DEBUGGER
# ==========================================
hostname_to_ip = {
    "www.youtube.com": "142.250.189.14",
    "youtube.com": "142.250.189.14",
    "m.youtube.com": "142.250.189.14",
    "www.google.com": "142.250.189.14"
}

_orig_getaddrinfo = socket.getaddrinfo

def new_getaddrinfo(*args, **kwargs):
    host = args[0]
    if host in hostname_to_ip:
        return _orig_getaddrinfo(hostname_to_ip[host], *args[1:], **kwargs)
    return _orig_getaddrinfo(*args, **kwargs)

socket.getaddrinfo = new_getaddrinfo

def find_cookies():
    """Searches for cookies.txt in current and parent directories"""
    # 1. Look in current directory
    if os.path.exists("cookies.txt"):
        return os.path.abspath("cookies.txt")
    
    # 2. Look in root directory (up one level)
    parent_path = os.path.join(os.getcwd(), "..", "cookies.txt")
    if os.path.exists(parent_path):
        return os.path.abspath(parent_path)
        
    # 3. Look in app root (common in Streamlit)
    app_root = os.path.join(os.path.dirname(__file__), "..", "cookies.txt")
    if os.path.exists(app_root):
        return os.path.abspath(app_root)
        
    return None

# ==========================================

def extract_video_id(url: str) -> str:
    parsed_url = urlparse(url)
    if parsed_url.hostname == 'youtu.be':
        return parsed_url.path[1:]
    if parsed_url.hostname in ['www.youtube.com', 'youtube.com']:
        return parse_qs(parsed_url.query).get('v', [None])[0]
    return None

def download_audio(url, output_filename):
    st.write("🔍 Searching for cookies.txt...")
    
    cookie_file = find_cookies()
    
    # UPDATED: Use 'best' instead of 'bestaudio' to fix "Format not available"
    ydl_opts = {
        'format': 'best',  # <--- CHANGED: Download best video+audio (more reliable)
        'outtmpl': output_filename.replace('.mp3', ''),
        'quiet': False,
        'force_ipv4': True,
        'socket_timeout': 15,
        #'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    
    if cookie_file:
        st.success(f"🍪 Cookies found at: {cookie_file}")
        ydl_opts['cookiefile'] = cookie_file
    else:
        st.error("❌ 'cookies.txt' NOT FOUND!")

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return f"{output_filename.replace('.mp3', '')}.mp3"
    except Exception as e:
        st.error(f"🛑 Download Failed: {str(e)}")
        return None

def get_transcript_from_url(url: str) -> str:
    video_id = extract_video_id(url)
    if not video_id:
        st.error("Invalid YouTube URL")
        return None

    # ---------- 1️⃣ Try YouTube captions ----------
    try:
        if hasattr(YouTubeTranscriptApi, 'get_transcript'):
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
        else:
            transcript = YouTubeTranscriptApi().get_transcript(video_id)
        return " ".join(item['text'] for item in transcript)
    except Exception as e:
        st.warning(f"⚠️ API Transcript failed. Switching to AI fallback...")

    # ---------- 2️⃣ Whisper fallback ----------
    audio_file = f"temp_{video_id}.mp3"
    try:
        downloaded_path = download_audio(url, audio_file)
        
        if not downloaded_path or not os.path.exists(downloaded_path):
            return None

        st.success("✅ Audio downloaded! Starting Whisper transcription...")
        model = whisper.load_model("base")
        result = model.transcribe(downloaded_path)

        if os.path.exists(downloaded_path):
            os.remove(downloaded_path)
            
        return result["text"]

    except Exception as e:
        st.error(f"🛑 Whisper Failed: {str(e)}")
        if os.path.exists(audio_file):
            os.remove(audio_file)
        return None
