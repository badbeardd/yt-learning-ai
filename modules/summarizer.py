import os
import requests

def summarize_transcript(text: str) -> str:
    """Summarize using a direct HTTP request (Bypassing Library Errors)."""
    
    # 1. Use the 'Router' URL (The new, correct address)
    # We use 'distilbart' because it is small (300MB) and won't crash the free tier.
    API_URL = "https://router.huggingface.co/models/sshleifer/distilbart-cnn-12-6"
    
    headers = {
        "Authorization": f"Bearer {os.getenv('HF_TOKEN')}",
        "Content-Type": "application/json"
    }

    # 2. Trim text to be safe
    safe_text = text[:3000]

    payload = {
        "inputs": safe_text,
        "parameters": {"do_sample": False} # Simple deterministic mode
    }

    try:
        # 3. Send Request directly
        response = requests.post(API_URL, headers=headers, json=payload, timeout=20)
        
        # 4. Check for success (200 OK)
        if response.status_code == 200:
            output = response.json()
            if isinstance(output, list) and len(output) > 0:
                return output[0].get('summary_text', "No summary returned.")
            else:
                return f"Unexpected success format: {output}"
        
        # 5. Handle Model Loading (Common on free tier)
        # If status is 503, it means the model is waking up.
        if response.status_code == 503:
            return "⚠️ Model is loading... Wait 30 seconds and try again."
            
        # 6. Print the REAL error if it fails
        return f"API Error {response.status_code}: {response.text}"

    except Exception as e:
        return f"Connection Failed: {str(e)}"
