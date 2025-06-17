FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
    ffmpeg \
    libcairo2-dev \
    libpango1.0-dev \
    libgirepository1.0-dev \
    python3-gi \
    python3-cairocffi \
    texlive-full \
    git \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

COPY video_worker.py /app/video_worker.py
WORKDIR /app

CMD ["python", "video_worker.py"]
