# Base Python image
FROM python:3.10-slim

# System deps for audio (PortAudio) and ALSA
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libportaudio2 portaudio19-dev libasound2 libasound2-dev && \
    rm -rf /var/lib/apt/lists/*

# Workdir
WORKDIR /app

# Copy project files
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Default command
CMD ["python", "-m", "src.orchestrator"]