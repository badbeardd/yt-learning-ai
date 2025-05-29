from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("TOGETHER_API_KEY"),
    base_url="https://api.together.xyz/v1"
)

def summarize_transcript(text: str) -> str:
    """Summarize transcript using Together API and Mixtral."""
    prompt = f"Summarize the following video transcript in 5-7 concise bullet points:\n\n{text[:3000]}"
    
    try:
        response = client.chat.completions.create(
            model="mistralai/Mixtral-8x7B-Instruct-v0.1",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error in summarization: {e}"
