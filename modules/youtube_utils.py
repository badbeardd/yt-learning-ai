import streamlit as st
import requests
from urllib.parse import urlparse, parse_qs

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

    st.info("🔄 Fetching transcript via RapidAPI (Solid API)...")

    # 1. Your Credentials (From your screenshot)
    url = "https://youtube-transcript3.p.rapidapi.com/api/transcript"
    
    querystring = {"videoId": video_id}

    headers = {
        "x-rapidapi-key": "4c87c54e7bmsh37692be715c85a9p116869jsn8282bbb7c1a1",
        "x-rapidapi-host": "youtube-transcript3.p.rapidapi.com"
    }

    # 2. Call the External API
    try:
        response = requests.get(url, headers=headers, params=querystring, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            
            # The API returns: { "title": "...", "lines": [ {"text": "...", "start": ...} ] }
            if "lines" in data:
                full_text = " ".join([item['text'] for item in data['lines']])
                st.success("✅ Success! Transcript fetched.")
                return full_text
            else:
                st.error("❌ API returned no lines. Video might not have captions.")
                return None

        elif response.status_code == 403:
            st.error("❌ API Key Error. Subscription might not be active yet.")
            return None
        else:
            st.error(f"❌ API Error: {response.status_code} - {response.text}")
            return None

    except Exception as e:
        st.error(f"🛑 Connection Failed: {str(e)}")
        return None
