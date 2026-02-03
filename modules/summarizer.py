import os
from huggingface_hub import InferenceClient

# 1. Connect to Hugging Face Free API
client = InferenceClient(token=os.getenv("HF_TOKEN"))

def summarize_transcript(text: str) -> str:
    """Summarize transcript using Hugging Face Free API (Zephyr-7B)."""
    
    # Trim text to prevent errors
    safe_text = text[:4000]

    messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant that summarizes videos."
        },
        {
            "role": "user", 
            "content": f"Summarize the following YouTube transcript into 5-7 concise bullet points:\n\nTRANSCRIPT:\n{safe_text}"
        }
    ]
    
    try:
        # 2. Use Zephyr-7B-Beta (Reliable Chat Model)
        # This model is specifically optimized for the 'chat_completion' endpoint
        response = client.chat_completion(
            messages=messages,
            model="HuggingFaceH4/zephyr-7b-beta", 
            max_tokens=500,
            temperature=0.5
        )
        
        # 3. Extract the answer
        return response.choices[0].message.content

    except Exception as e:
        return f"Error in summarization: {str(e)}"
