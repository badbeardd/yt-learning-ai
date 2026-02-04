import sys
import types
import torch

sys.modules['torch.classes'] = types.ModuleType('torch.classes')
torch.classes = sys.modules['torch.classes']

import streamlit as st
from modules.youtube_utils import get_transcript_from_url
from modules.summarizer import summarize_transcript
from modules.vector_store import create_vector_store, get_context_chunks
from modules.chat_engine import get_chat_response
from modules.translation import translate_text

# ----------------------------
# App Config
# ----------------------------
st.set_page_config(page_title="YouTube Learning Assistant", layout="wide")
st.title("📚 YouTube Learning Assistant")

# ----------------------------
# State Init
# ----------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "vector_store" not in st.session_state:
    st.session_state.vector_store = None

if "video_ready" not in st.session_state:
    st.session_state.video_ready = False

if "transcript_text" not in st.session_state:
    st.session_state.transcript_text = None

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
lang = st.selectbox("🌐 Choose output language", list(lang_options.keys()))
lang_code = lang_options[lang]

# ----------------------------
# Video Processing
# ----------------------------
yt_url = st.text_input("Paste YouTube Video URL:")
submit = st.button("🔍 Process Video")

if submit and yt_url:
    st.session_state.chat_history = []
    st.session_state.video_ready = False

    with st.spinner("Fetching transcript..."):
        transcript_text = get_transcript_from_url(yt_url)

    if transcript_text:
        st.session_state.transcript_text = transcript_text

        with st.spinner("Summarizing..."):
            summary = summarize_transcript(transcript_text)
            st.write(translate_text(summary, lang_code))

        with st.spinner("Building knowledge base..."):
            st.session_state.vector_store = create_vector_store(transcript_text)
            st.session_state.video_ready = True
    else:
        st.error("Transcript not found.")

# ----------------------------
# Conversational Q&A
# ----------------------------
if st.session_state.video_ready:
    st.subheader("💬 Ask Questions")
    user_query = st.text_input("Ask anything about the video")

    if user_query:
        with st.spinner("Thinking..."):

            if st.session_state.chat_history:
                last = st.session_state.chat_history[-1]
                augmented_query = (
                    last["question"] + " " + last["answer"] + " " + user_query
                )
            else:
                augmented_query = user_query

            context_chunks = get_context_chunks(
                augmented_query,
                st.session_state.vector_store
            )

            response = get_chat_response(
                user_question=user_query,
                context_chunks=context_chunks,
                chat_history=st.session_state.chat_history
            )

            st.session_state.chat_history.append(
                {"question": user_query, "answer": response}
            )

            st.markdown(translate_text(response, lang_code))
