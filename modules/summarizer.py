import os
from openai import OpenAI

# 1. Setup Client for Groq (Free & Fast)
client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

def summarize_transcript(text: str) -> str:
    """Summarize using Groq (Llama 3)."""
    
    # 2. Safety: Groq handles ~6000 chars easily
    safe_text = text[:6000]

    try:
        # 3. Call Llama 3 (Smartest open model)
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that summarizes videos."},
                {"role": "user", "content": f"Summarize this transcript in 5-7 concise bullet points:\n\n{safe_text}"}
            ],
            temperature=0.5,
            max_tokens=500
        )
        
        # 4. Return the summary
        return response.choices[0].message.content

    except Exception as e:
        return f"Summarization Error: {str(e)}"
