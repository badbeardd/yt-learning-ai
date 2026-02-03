import os
import requests

def summarize_transcript(text: str) -> str:
    """Summarize using the dedicated BART model via raw API request."""
    
    # 1. API Endpoint (Direct Link to the Model)
    api_url = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
    
    # 2. Authentication
    headers = {"Authorization": f"Bearer {os.getenv('HF_TOKEN')}"}
    
    # 3. Payload
    # We send the text and parameters as raw JSON. 
    # This bypasses the 'unexpected keyword' errors you were seeing.
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
        
        # 5. Handle "Model Loading" or other API errors
        if isinstance(output, dict) and "error" in output:
            return f"⚠️ API Status: {output['error']} (Try again in 20 seconds)"
            
        # 6. Success!
        # The API returns a list: [{'summary_text': '...'}]
        if isinstance(output, list) and len(output) > 0:
            return output[0].get('summary_text', "No summary returned.")
            
        return f"Unexpected API response: {output}"

    except Exception as e:
        return f"Connection Error: {str(e)}"
