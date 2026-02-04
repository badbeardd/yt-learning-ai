# from openai import OpenAI
# import os
# from dotenv import load_dotenv

# load_dotenv()

# client = OpenAI(
#     api_key=os.getenv("TOGETHER_API_KEY"),
#     base_url="https://api.together.xyz/v1"
# )

# def get_chat_response(user_question: str, context_chunks: list) -> str:
#     """Generate response using Together API and Mixtral."""
#     context = "\n".join(context_chunks)
    
#     prompt = f"""Based on the following transcript excerpts, answer the user's question accurately and clearly.

# Transcript:
# {context}

# Question: {user_question}
# Answer:"""
    
#     try:
#         response = client.chat.completions.create(
#             model="mistralai/Mixtral-8x7B-Instruct-v0.1",
#             messages=[
#                 {"role": "system", "content": "You are an expert assistant who explains YouTube video content."},
#                 {"role": "user", "content": prompt}
#             ],
#             temperature=0.5
#         )
#         return response.choices[0].message.content.strip()
#     except Exception as e:
#         return f"Chat generation error: {e}"

from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

# ✅ Use GROQ only (one provider, one key)
client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

def get_chat_response(
    user_question: str,
    context_chunks: list,
    chat_history: list
) -> str:
    """Generate conversational response using Groq."""

    # 1️⃣ Build transcript context
    context = "\n".join(context_chunks)

    # 2️⃣ Build conversation history (last 5 turns)
    history_text = ""
    for turn in chat_history[-5:]:
        history_text += (
            f"User: {turn['question']}\n"
            f"Assistant: {turn['answer']}\n"
        )

    # 3️⃣ Final prompt (history + retrieval + question)
    prompt = f"""
You are an expert assistant helping users understand a YouTube video.

Conversation so far:
{history_text}

Relevant transcript excerpts:
{context}

Current question:
{user_question}

Answer clearly and concisely, considering the conversation context.
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",  # or mixtral-8x7b-32768
            messages=[
                {"role": "system", "content": "You explain YouTube video content accurately."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=600
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"Chat generation error: {e}"

