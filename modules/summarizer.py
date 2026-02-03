import os
import requests

def summarize_transcript(text: str) -> str:
    API_URL = "https://router.huggingface.co/hf-inference/models/facebook/bart-large-cnn"
    
    token = os.getenv("HF_TOKEN")
    if not token:
        return "❌ Error: HF_TOKEN is missing. Check your Space Settings."

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    payload = {
        "inputs": text[:3000],
        "parameters": {
            "do_sample": False
        }
    }

    try:
        response = requests.post(
            API_URL,
            headers=headers,
            json=payload,
            timeout=30
        )

        if response.status_code == 200:
            output = response.json()
            if isinstance(output, list) and len(output) > 0:
                return output[0].get("summary_text", "No summary returned.")
            return f"Unexpected response: {output}"

        elif response.status_code == 503:
            return "⏳ Model is loading. Wait ~30 seconds and retry."

        else:
            return f"❌ API Error ({response.status_code}): {response.text}"

    except Exception as e:
        return f"🛑 Connection Error: {str(e)}"
