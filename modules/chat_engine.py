from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("TOGETHER_API_KEY"),
    base_url="https://api.together.xyz/v1"
)

def get_chat_response(user_question: str, context_chunks: list) -> str:
    """Generate response using Together API and Mixtral."""
    context = "\n".join(context_chunks)
    
    prompt = f"""Based on the following transcript excerpts, answer the user's question accurately and clearly.

Transcript:
{context}

Question: {user_question}
Answer:"""
    
    try:
        response = client.chat.completions.create(
            model="mistralai/Mixtral-8x7B-Instruct-v0.1",
            messages=[
                {"role": "system", "content": "You are an expert assistant who explains YouTube video content."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Chat generation error: {e}"
