FROM python:3.12-slim

# Install required system packages
RUN apt-get update && apt-get install -y \
    pkg-config \
    libcairo2-dev \
    libpango1.0-dev \
    python3-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy app code
COPY . .

# Expose port and set default run command
EXPOSE 8000
CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000"]
