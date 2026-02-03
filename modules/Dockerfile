FROM python:3.10-slim

# Install system dependencies (FFmpeg for Whisper)
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first (better caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy app source
COPY . .

# Expose Hugging Face required port
EXPOSE 7860

# Run Streamlit on Hugging Face
CMD ["streamlit", "run", "app.py", "--server.port=7860", "--server.address=0.0.0.0"]
