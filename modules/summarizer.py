import os
import requests

def summarize_transcript(text: str) -> str:
    """Summarize using the dedicated BART model via raw API request."""
    
    # 1. NEW API Endpoint (Updated to 'router.huggingface.co')
    # The old 'api-inference' URL is deprecated. This is the new standard.
    api_url = "https://router.huggingface.co/models/facebook/bart-large-cnn"
    
    # 2. Authentication
    headers = {"Authorization": f"Bearer {os.getenv('HF_TOKEN')}"}
    
    # 3. Payload
    payload = {
        "inputs": text[:3000], # Keep text short enough for the model
        "parameters": {
            "min_length": 60,
            "max_length": 300,
            "do_sample": False
        }
    }

    try:
        # 4. Make the Request
        response = requests.post(api_url, headers=headers, json=payload)
        output = response.json()
        
        # 5. Handle "Model Loading" 
        # (If the model is asleep, it returns an error saying "loading". We catch that.)
        if isinstance(output, dict) and "error" in output:
            return f"⚠️ API Status: {output['error']} (Wait 30s and try again - Model is waking up)"
            
        # 6. Success!
        if isinstance(output, list) and len(output) > 0:
            return output[0].get('summary_text', "No summary returned.")
            
        return f"Unexpected API response: {output}"

    except Exception as e:
        return f"Connection Error: {str(e)}"
