# 🎓 YouTube Learning Assistant

An AI-powered Streamlit web app that learns from YouTube videos by extracting transcripts, summarizing content, and enabling intelligent Q&A — with multilingual support!

---

## 🚀 Features

- 🔗 **YouTube Transcript Extraction** – Paste any video URL and extract the transcript.
- 🧠 **AI Summarization** – Get concise bullet-point summaries using Together AI's Mixtral.
- 💬 **Conversational Q&A** – Ask questions based on video content using vector-based retrieval.
- 🌍 **Multilingual Support** – Translate summaries and answers into Hindi, Bengali, Tamil, Spanish, French, and more.
- ⚡ Built with `Streamlit`, `FAISS`, `sentence-transformers`, and `Together API`.

---

## 🛠️ Tech Stack

- `Streamlit` – Frontend UI
- `youtube-transcript-api` – Transcript extraction
- `sentence-transformers` – Embeddings
- `FAISS` – Vector search for RAG
- `Together AI` – LLM backend (Mixtral 8x7B)
- `deep-translator` – Multilingual translation

---

## 🧪 How to Run

1. **Clone the repo**  
```bash
git clone https://github.com/badbeardd/yt-learning-ai.git
cd yt-learning-ai
