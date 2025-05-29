from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs

def extract_video_id(url: str) -> str:
    """Extract video ID from a YouTube URL."""
    parsed_url = urlparse(url)
    if parsed_url.hostname == 'youtu.be':
        return parsed_url.path[1:]
    if parsed_url.hostname in ['www.youtube.com', 'youtube.com']:
        return parse_qs(parsed_url.query).get('v', [None])[0]
    return None

def get_transcript_from_url(url: str) -> str:
    """Fetch transcript from YouTube video URL."""
    video_id = extract_video_id(url)
    if not video_id:
        return None
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return ' '.join([item['text'] for item in transcript])
    except Exception as e:
        print(f"Transcript Error: {e}")
        return None
