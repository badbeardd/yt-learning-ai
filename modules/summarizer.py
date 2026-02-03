import os
from huggingface_hub import InferenceClient

# 1. Connect to Hugging Face
client = InferenceClient(token=os.getenv("HF_TOKEN"))

def summarize_transcript(text: str) -> str:
    """Summarize using the dedicated BART Summarization model."""
    
    # 2. Trim text (BART has a smaller limit, so we keep it safe at 3000 chars)
    safe_text = text[:3000]

    try:
        # 3. Use the 'summarization' task directly
        # We are NOT using 'chat_completion' anymore. 
        # We use a model specifically built to summarize text.
        summary_result = client.summarization(
            safe_text,
            model="facebook/bart-large-cnn",
            parameters={"min_length": 60, "max_length": 300}
        )
        
        # The API returns a list: [{'summary_text': '...'}]
        return summary_result[0]['summary_text']

    except Exception as e:
        return f"Error in summarization: {str(e)}"
