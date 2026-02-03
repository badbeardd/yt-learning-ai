from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs
import whisper
from pytube import YouTube
import os

def extract_video_id(url: str) -> str:
    parsed_url = urlparse(url)
    if parsed_url.hostname == 'youtu.be':
        return parsed_url.path[1:]
    if parsed_url.hostname in ['www.youtube.com', 'youtube.com']:
        return parse_qs(parsed_url.query).get('v', [None])[0]
    return None


def get_transcript_from_url(url: str) -> str:
    video_id = extract_video_id(url)
    if not video_id:
        return None

    # ---------- 1️⃣ Try YouTube captions ----------
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join(item['text'] for item in transcript)
    except Exception as e:
        print("YouTube captions failed:", e)

    # ---------- 2️⃣ Whisper fallback ----------
    try:
        yt = YouTube(url)
        audio = yt.streams.filter(only_audio=True).first()
        audio_path = audio.download(filename=f"{video_id}.mp4")

        model = whisper.load_model("base")
        result = model.transcribe(audio_path)

        os.remove(audio_path)
        return result["text"]

    except Exception as e:
        print("Whisper failed:", e)
        return None
