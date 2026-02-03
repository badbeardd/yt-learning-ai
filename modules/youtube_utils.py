import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs
import whisper
import yt_dlp
import os
import shutil
import socket

# FORCE IPv4 (Fixes the "[Errno -5] No address" network error)
def force_ipv4():
    old_getaddrinfo = socket.getaddrinfo
    def new_getaddrinfo(*args, **kwargs):
        responses = old_getaddrinfo(*args, **kwargs)
        return [response for response in responses if response[0] == socket.AF_INET]
    socket.getaddrinfo = new_getaddrinfo

force_ipv4()

def extract_video_id(url: str) -> str:
    parsed_url = urlparse(url)
    if parsed_url.hostname == 'youtu.be':
        return parsed_url.path[1:]
    if parsed_url.hostname in ['www.youtube.com', 'youtube.com']:
        return parse_qs(parsed_url.query).get('v', [None])[0]
    return None

def download_audio(url, output_filename):
    st.write("🎧 Attempting to download audio (IPv4 Forced)...")
    
    # 1. Force IPv4 and use a solid user agent to avoid bot detection
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': output_filename.replace('.mp3', ''),
        'quiet': False,
        'force_ipv4': True,  # <--- THIS FIXES THE RED ERROR
        'socket_timeout': 15,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    
    # 2. Check for cookies (optional but good)
    if os.path.exists("cookies.txt"):
        ydl_opts['cookiefile'] = "cookies.txt"

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
        # Tries to access the static method safely
        if hasattr(YouTubeTranscriptApi, 'get_transcript'):
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
        else:
            # Fallback for weird library versions
            transcript = YouTubeTranscriptApi().get_transcript(video_id)
            
        return " ".join(item['text'] for item in transcript)
    except Exception as e:
        st.warning(f"⚠️ API Transcript failed. Switching to AI fallback...")
        print(f"API Error: {e}")

    # ---------- 2️⃣ Whisper fallback (Stronger) ----------
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
