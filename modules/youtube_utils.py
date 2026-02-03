from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs
import whisper
import yt_dlp
import os

def extract_video_id(url: str) -> str:
    parsed_url = urlparse(url)
    if parsed_url.hostname == 'youtu.be':
        return parsed_url.path[1:]
    if parsed_url.hostname in ['www.youtube.com', 'youtube.com']:
        return parse_qs(parsed_url.query).get('v', [None])[0]
    return None

def download_audio(url, output_filename):
    """Downloads audio using yt-dlp (Reliable replacement for pytube)"""
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': output_filename.replace('.mp3', ''), # yt-dlp adds extension automatically
        'quiet': True
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return f"{output_filename.replace('.mp3', '')}.mp3"
    except Exception as e:
        print(f"yt-dlp failed: {e}")
        return None

def get_transcript_from_url(url: str) -> str:
    video_id = extract_video_id(url)
    if not video_id:
        return None

    # ---------- 1️⃣ Try YouTube captions (Fastest) ----------
    try:
        print(f"Fetching captions for {video_id}...")
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join(item['text'] for item in transcript)
    except Exception as e:
        print(f"YouTube captions failed: {e}. Switching to Whisper...")

    # ---------- 2️⃣ Whisper fallback (Stronger) ----------
    audio_file = f"temp_{video_id}.mp3"
    try:
        # Download using yt-dlp
        downloaded_path = download_audio(url, audio_file)
        
        if not downloaded_path or not os.path.exists(downloaded_path):
            return None

        print("Transcribing with Whisper...")
        # Load 'base' model (good balance of speed/accuracy for free tier)
        model = whisper.load_model("base")
        result = model.transcribe(downloaded_path)

        # Cleanup
        if os.path.exists(downloaded_path):
            os.remove(downloaded_path)
            
        return result["text"]

    except Exception as e:
        print(f"Whisper failed: {e}")
        # Cleanup in case of error
        if os.path.exists(audio_file):
            os.remove(audio_file)
        return None
