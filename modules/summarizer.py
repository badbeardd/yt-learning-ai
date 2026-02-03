import os
from huggingface_hub import InferenceClient

# 1. Connect to Hugging Face Free API
client = InferenceClient(token=os.getenv("HF_TOKEN"))

def summarize_transcript(text: str) -> str:
    """Summarize transcript using Hugging Face Free API (Chat Mode)."""
    
    # Trim text to prevent errors
    safe_text = text[:4000]

    # 2. Define the Message (Chat Format)
    # The API requires a list of messages, not just a string prompt.
    messages = [
        {
            "role": "user", 
            "content": f"Summarize the following YouTube transcript into 5-7 concise bullet points:\n\nTRANSCRIPT:\n{safe_text}"
        }
    ]
    
    try:
        # 3. Call the Chat Completion API
        response = client.chat_completion(
            messages=messages,
            model="mistralai/Mistral-7B-Instruct-v0.3", 
            max_tokens=500,
            temperature=0.5
        )
        
        # 4. Extract the answer
        return response.choices[0].message.content

    except Exception as e:
        return f"Error in summarization: {str(e)}"
