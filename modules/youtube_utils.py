import socket
import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs
import whisper
import yt_dlp
import os
import shutil

# 🛠️ DNS FIX
hostname_to_ip = {
    "www.youtube.com": "142.250.189.14",
    "youtube.com": "142.250.189.14",
    "m.youtube.com": "142.250.189.14",
    "www.google.com": "142.250.189.14"
}
socket.getaddrinfo = lambda *args, **kwargs: socket.getaddrinfo(hostname_to_ip.get(args[0], args[0]), *args[1:], **kwargs) if args[0] in hostname_to_ip else socket.getaddrinfo(*args, **kwargs)

def find_cookies():
    """Locate the cookies.txt file"""
    if os.path.exists("cookies.txt"): return os.path.abspath("cookies.txt")
    if os.path.exists("../cookies.txt"): return os.path.abspath("../cookies.txt")
    return None

def extract_video_id(url: str) -> str:
    parsed_url = urlparse(url)
    if parsed_url.hostname == 'youtu.be': return parsed_url.path[1:]
    if parsed_url.hostname in ['www.youtube.com', 'youtube.com']: return parse_qs(parsed_url.query).get('v', [None])[0]
    return None

def get_transcript_from_url(url: str) -> str:
    video_id = extract_video_id(url)
    if not video_id:
        st.error("Invalid YouTube URL")
        return None

    cookie_file = find_cookies()
    
    # ---------- 1️⃣ Try YouTube Captions (WITH COOKIES NOW!) ----------
    try:
        # 🟢 NEW: We pass the cookies here! This often bypasses the block instantly.
        if cookie_file:
            transcript = YouTubeTranscriptApi.get_transcript(video_id, cookies=cookie_file)
        else:
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            
        return " ".join(item['text'] for item in transcript)
        
    except Exception as e:
        print(f"Transcript Error: {e}") # Log it for debugging
        st.warning(f"⚠️ Text Transcript failed ({str(e)}). Switching to Audio Fallback...")

    # ---------- 2️⃣ Whisper Fallback (Audio Download) ----------
    # This is the "Hard Mode" that keeps failing, but we keep it as a backup
    return download_and_transcribe_audio(url, video_id, cookie_file)

def download_and_transcribe_audio(url, video_id, cookie_file):
    audio_file = f"temp_{video_id}.mp3"
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': audio_file.replace('.mp3', ''),
        'quiet': False,
        'force_ipv4': True,
        'socket_timeout': 15,
        'extractor_args': {'youtube': {'player_client': ['android']}}, # Android Mode
        'postprocessors': [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': '192'}],
    }

    if cookie_file: ydl_opts['cookiefile'] = cookie_file

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            
        st.success("✅ Audio downloaded! Starting Whisper transcription...")
        model = whisper.load_model("base")
        result = model.transcribe(audio_file)
        
        if os.path.exists(audio_file): os.remove(audio_file)
        return result["text"]

    except Exception as e:
        st.error(f"🛑 All methods failed: {str(e)}")
        if os.path.exists(audio_file): os.remove(audio_file)
        return None
