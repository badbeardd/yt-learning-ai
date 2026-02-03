import os
import requests
import time

def summarize_transcript(text: str) -> str:
    """
    Robust Summarizer: Tries multiple API URLs and Models to find one that works.
    """
    token = os.getenv("HF_TOKEN")
    if not token:
        return "❌ Error: HF_TOKEN is missing from Secrets."

    headers = {"Authorization": f"Bearer {token}"}
    safe_text = text[:3000] # Keep text short enough for free tier

    # LIST OF ENDPOINTS TO TRY (If one fails, we try the next)
    # We try the 'Router' (New System) and 'API-Inference' (Old System)
    # We also try two different models: BART (Standard) and DistilBART (Lightweight)
    endpoints = [
        "https://router.huggingface.co/models/facebook/bart-large-cnn",
        "https://api-inference.huggingface.co/models/facebook/bart-large-cnn",
        "https://router.huggingface.co/models/sshleifer/distilbart-cnn-12-6",
        "https://api-inference.huggingface.co/models/sshleifer/distilbart-cnn-12-6"
    ]

    for api_url in endpoints:
        try:
            # Send Request
            payload = {
                "inputs": safe_text,
                "parameters": {"do_sample": False, "min_length": 50, "max_length": 250}
            }
            response = requests.post(api_url, headers=headers, json=payload, timeout=20)

            # Case 1: Success (200 OK)
            if response.status_code == 200:
                output = response.json()
                if isinstance(output, list) and len(output) > 0:
                    return output[0].get('summary_text', "No summary returned.")
            
            # Case 2: Model Loading (503)
            # If the model is asleep, we MUST wait and try the SAME URL again.
            elif response.status_code == 503:
                return "⚠️ Model is loading... Please wait 30 seconds and click 'Process Video' again."

            # Case 3: 404 Not Found (Try next URL)
            elif response.status_code == 404:
                continue # Skip to the next URL in the list

            # Case 4: Other Error (Auth, etc)
            else:
                return f"❌ API Error ({response.status_code}): {response.text}"

        except Exception as e:
            continue # If connection fails, try next URL

    return "❌ Failed to connect to any Hugging Face model. Please check your HF_TOKEN."
