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
import torch
import types

# Prevent Streamlit from trying to walk into torch.classes (which is broken in Windows)
if not hasattr(torch, '__path__'):
    torch.__path__ = types.SimpleNamespace(_path=[])
# Set up Streamlit app
import os
st.set_page_config(page_title="YouTube Learning Assistant", layout="wide")
st.title("📚 YouTube Learning Assistant")

# User inputs YouTube link
yt_url = st.text_input("Paste YouTube Video URL:")

if yt_url:
    with st.spinner("Fetching transcript..."):
        transcript_text = get_transcript_from_url(yt_url)

    if transcript_text:
        st.success("Transcript fetched!")
        st.subheader("📝 Transcript Summary")

        with st.spinner("Summarizing..."):
            summary = summarize_transcript(transcript_text)
            st.write(summary)

        with st.spinner("Building knowledge base for Q&A..."):
            vector_store = create_vector_store(transcript_text)

        st.subheader("💬 Ask Questions")
        user_query = st.text_input("Ask anything about the video content")

        if user_query:
            with st.spinner("Thinking..."):
                context_chunks = get_context_chunks(user_query, vector_store)
                response = get_chat_response(user_query, context_chunks)
                st.markdown(response)
    else:
        st.error("Transcript not found or unavailable for this video.")
