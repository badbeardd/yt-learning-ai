import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs
import whisper
import yt_dlp
import os
import shutil

def extract_video_id(url: str) -> str:
    parsed_url = urlparse(url)
    if parsed_url.hostname == 'youtu.be':
        return parsed_url.path[1:]
    if parsed_url.hostname in ['www.youtube.com', 'youtube.com']:
        return parse_qs(parsed_url.query).get('v', [None])[0]
    return None

def download_audio(url, output_filename):
    # Check if FFmpeg is actually installed
    if not shutil.which("ffmpeg"):
        st.error("🚨 CRITICAL ERROR: FFmpeg is not installed on the server. The app cannot process audio.")
        st.info("Fix: Ensure 'packages.txt' exists in your repo root with the word 'ffmpeg' inside, then do a Factory Rebuild.")
        return None

    st.write(f"🎧 Attempting to download audio for fallback...")
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': output_filename.replace('.mp3', ''),
        'quiet': False, # Let us see logs if needed
        'nocheckcertificate': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
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

    # ---------- 1️⃣ Try YouTube captions (Fastest) ----------
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join(item['text'] for item in transcript)
    except Exception as e:
        st.warning(f"⚠️ Official Transcript API failed (likely IP block). Reason: {e}")
        st.info("🔄 Switching to Whisper (AI Transcription)...")

    # ---------- 2️⃣ Whisper fallback (Stronger) ----------
    audio_file = f"temp_{video_id}.mp3"
    try:
        downloaded_path = download_audio(url, audio_file)
        
        if not downloaded_path or not os.path.exists(downloaded_path):
            return None # Error already printed in download_audio

        st.success("✅ Audio downloaded! Starting AI transcription (this takes 30-60s)...")
        
        # Load model
        model = whisper.load_model("base")
        result = model.transcribe(downloaded_path)

        # Cleanup
        if os.path.exists(downloaded_path):
            os.remove(downloaded_path)
            
        return result["text"]

    except Exception as e:
        st.error(f"🛑 Whisper Transcription Failed: {str(e)}")
        if os.path.exists(audio_file):
            os.remove(audio_file)
        return None
