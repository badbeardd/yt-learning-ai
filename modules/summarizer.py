import os
from huggingface_hub import InferenceClient

# 1. Connect to Hugging Face
client = InferenceClient(token=os.getenv("HF_TOKEN"))

def summarize_transcript(text: str) -> str:
    """Summarize using DistilBART (Lighter, Faster, More Stable)."""
    
    # 2. Trim text (Keep it under 3000 chars for speed)
    safe_text = text[:3000]

    try:
        # 3. Use 'sshleifer/distilbart-cnn-12-6'
        # This model is much smaller (300MB vs 1.6GB) so it rarely times out.
        # We pass NO extra parameters to avoid "keyword" errors.
        summary_result = client.summarization(
            safe_text,
            model="sshleifer/distilbart-cnn-12-6"
        )
        
        # 4. Success
        return summary_result[0]['summary_text']

    except Exception as e:
        return f"Summarization failed: {str(e)}"
