import os
from huggingface_hub import InferenceClient

# 1. Connect to Hugging Face (uses the HF_TOKEN you just added)
client = InferenceClient(token=os.getenv("HF_TOKEN"))

def summarize_transcript(text: str) -> str:
    """Summarize transcript using Hugging Face Free API."""
    
    # 2. Safety: Trim text to ~4000 chars so we don't hit the free limit
    safe_text = text[:4000]

    prompt = f"""
    [INST] You are a helpful assistant. Summarize the following YouTube transcript into 5-7 concise bullet points.
    
    TRANSCRIPT:
    {safe_text}
    [/INST]
    """
    
    try:
        # 3. Use Mistral-7B (Fast & Free)
        response = client.text_generation(
            prompt,
            model="mistralai/Mistral-7B-Instruct-v0.3",
            max_new_tokens=500,
            temperature=0.5,
            return_full_text=False
        )
        return response.strip()

    except Exception as e:
        return f"Error in summarization (Free HF API): {str(e)}"
