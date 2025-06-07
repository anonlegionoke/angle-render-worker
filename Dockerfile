FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libcairo2-dev \
    libpango1.0-dev \
    pkg-config \
    python3-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create necessary directories
RUN mkdir -p public/thumbnails tmp

# Set environment variables
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

# Use the same command as railway.toml for consistency
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
