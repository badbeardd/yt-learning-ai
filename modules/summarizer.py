import os
from huggingface_hub import InferenceClient

# 1. Connect to Hugging Face
client = InferenceClient(token=os.getenv("HF_TOKEN"))

def summarize_transcript(text: str) -> str:
    """Summarize using the dedicated BART Summarization model."""
    
    # 2. Trim text to fit the model's limit
    safe_text = text[:3000]

    try:
        # 3. CORRECTED CALL: Pass arguments directly, not inside 'parameters={}'
        summary_result = client.summarization(
            safe_text,
            model="facebook/bart-large-cnn",
            min_length=60,
            max_length=300
        )
        
        # The API returns a list: [{'summary_text': '...'}]
        return summary_result[0]['summary_text']

    except Exception as e:
        return f"Error in summarization: {str(e)}"
