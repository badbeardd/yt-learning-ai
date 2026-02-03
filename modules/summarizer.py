import os
import requests
import time

def summarize_transcript(text: str) -> str:
    """
    Connects strictly to the new Hugging Face Router.
    """
    # 1. The ONLY correct URL (No old 'api-inference' links)
    API_URL = "https://router.huggingface.co/models/facebook/bart-large-cnn"
    
    token = os.getenv("HF_TOKEN")
    if not token:
        return "❌ Error: HF_TOKEN is missing. Check your Space Settings."

    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Payload: Simple and clean (No complex parameters to cause errors)
    # We strip the text to 3000 chars to fit the model's memory.
    payload = {
        "inputs": text[:3000],
        "parameters": {"do_sample": False}
    }

    try:
        # 3. Send the request
        response = requests.post(API_URL, headers=headers, json=payload, timeout=20)

        # Case A: Success
        if response.status_code == 200:
            output = response.json()
            # The API returns a list: [{'summary_text': '...'}]
            if isinstance(output, list) and len(output) > 0:
                return output[0].get('summary_text', "No summary returned.")
            return f"Unexpected success response: {output}"

        # Case B: Model is "Cold" (Loading) - VERY COMMON
        elif response.status_code == 503:
            return "⏳ Model is loading... (This is normal for free usage). Please wait 30 seconds and click 'Process Video' again."

        # Case C: Other Errors (Print exactly what happened)
        else:
            return f"❌ API Error ({response.status_code}): {response.text}"

    except Exception as e:
        return f"🛑 Connection Error: {str(e)}"
