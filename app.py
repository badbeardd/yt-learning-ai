import sys
import types
import torch

# Patch torch.classes to prevent Streamlit from inspecting it
sys.modules['torch.classes'] = types.ModuleType('torch.classes')
torch.classes = sys.modules['torch.classes']

import streamlit as st
from modules.youtube_utils import get_transcript_from_url
from modules.summarizer import summarize_transcript
from modules.vector_store import create_vector_store, get_context_chunks
from modules.chat_engine import get_chat_response
from modules.translation import translate_text

# ----------------------------
# Streamlit App Configuration
# ----------------------------
st.set_page_config(page_title="YouTube Learning Assistant", layout="wide")
st.title("📚 YouTube Learning Assistant")

# ----------------------------
# Initialize Chat Memory
# ----------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ----------------------------
# Language Selector
# ----------------------------
lang_options = {
    "English": "en",
    "Hindi": "hi",
    "Bengali": "bn",
    "Tamil": "ta",
    "Spanish": "es",
    "French": "fr"
}
lang = st.selectbox("🌐 Choose output language", options=list(lang_options.keys()))
lang_code = lang_options[lang]

# ----------------------------
# YouTube URL Input
# ----------------------------
yt_url = st.text_input("Paste YouTube Video URL:")
submit = st.button("🔍 Process Video")
if submit:
    st.session_state.chat_history = []


if yt_url and submit:
    with st.spinner("Fetching transcript..."):
        transcript_text = get_transcript_from_url(yt_url)

    if transcript_text:
        st.success("Transcript fetched!")

        # ----------------------------
        # Transcript Summary
        # ----------------------------
        st.subheader("📝 Transcript Summary")
        with st.spinner("Summarizing..."):
            summary = summarize_transcript(transcript_text)
            translated_summary = translate_text(summary, lang_code)
            st.write(translated_summary)

        # ----------------------------
        # Vector Store Creation
        # ----------------------------
        with st.spinner("Building knowledge base for Q&A..."):
            vector_store = create_vector_store(transcript_text)

        # ----------------------------
        # Conversational Q&A
        # ----------------------------
        st.subheader("💬 Ask Questions")
        user_query = st.text_input("Ask anything about the video content")

        if user_query:
            with st.spinner("Thinking..."):

                # 🔑 Follow-up–aware retrieval
                if st.session_state.chat_history:
                    augmented_query = (
                        st.session_state.chat_history[-1]["question"]
                        + " "
                        + user_query
                    )
                else:
                    augmented_query = user_query

                context_chunks = get_context_chunks(
                    augmented_query, vector_store
                )

                response = get_chat_response(
                    user_question=user_query,
                    context_chunks=context_chunks,
                    chat_history=st.session_state.chat_history
                )

                # Store conversation
                st.session_state.chat_history.append(
                    {"question": user_query, "answer": response}
                )

                translated_response = translate_text(response, lang_code)
                st.markdown(translated_response)

    else:
        st.error("Transcript not found or unavailable for this video.")
