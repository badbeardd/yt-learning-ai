import socket
import streamlit as st
import requests
import re
from urllib.parse import urlparse, parse_qs
import os

# ==========================================
# 🛠️ DNS FIX (Keep to prevent recursion crash)
# ==========================================
_orig_getaddrinfo = socket.getaddrinfo

def new_getaddrinfo(*args, **kwargs):
    hostname_to_ip = {
        "www.youtube.com": "142.250.189.14",
        "youtube.com": "142.250.189.14",
        "m.youtube.com": "142.250.189.14",
        "www.google.com": "142.250.189.14"
    }
    host = args[0]
    if host in hostname_to_ip:
        return _orig_getaddrinfo(hostname_to_ip[host], *args[1:], **kwargs)
    return _orig_getaddrinfo(*args, **kwargs)

socket.getaddrinfo = new_getaddrinfo
# ==========================================

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

    st.info("🔄 Cloud IP blocked. Attempting to route via Invidious Network...")

    # List of public Invidious instances (Volunteer proxies)
    # We try them one by one until one works.
    instances = [
        "https://inv.tux.pizza",
        "https://invidious.jing.rocks",
        "https://vid.ufficiozero.org",
        "https://invidious.nerdvpn.de",
        "https://inv.zzls.xyz"
    ]

    for instance in instances:
        try:
            # 1. Ask Invidious for the video info to find caption tracks
            # Endpoint: /api/v1/videos/{video_id}
            api_url = f"{instance}/api/v1/videos/{video_id}"
            response = requests.get(api_url, timeout=5)
            
            if response.status_code != 200:
                continue

            data = response.json()
            captions = data.get("captions", [])
            
            # 2. Find an English caption track
            selected_caption = None
            for cap in captions:
                if "en" in cap["languageCode"]:
                    selected_caption = cap["url"] # This is a relative URL
                    break
            
            if not selected_caption:
                continue

            # 3. Download the actual text (VTT format)
            # The URL provided by Invidious is usually relative, so we prepend the instance URL
            full_cap_url = f"{instance}{selected_caption}"
            transcript_response = requests.get(full_cap_url, timeout=5)
            
            if transcript_response.status_code == 200:
                # 4. Clean the VTT format (remove timestamps like 00:00:01.000)
                raw_text = transcript_response.text
                # Simple regex to remove VTT timestamps and header
                clean_lines = []
                for line in raw_text.splitlines():
                    if "-->" in line or line == "WEBVTT" or not line.strip():
                        continue
                    clean_lines.append(line.strip())
                
                final_text = " ".join(clean_lines)
                st.success(f"✅ Success! Transcript fetched via {instance}")
                return final_text

        except Exception as e:
            print(f"Failed on {instance}: {e}")
            continue

    st.error("🛑 All Invidious proxies failed. YouTube is blocking this video strictly.")
    return None

# (Deleted download_audio entirely as it is useless on blocked IP)
