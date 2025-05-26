# angle-render-worker

A background rendering service for the Angle AI editor/generator. This service handles the rendering of mathematical animations and visualizations using Manim, providing a scalable and isolated environment for processing rendering requests from the main Angle NextJS application.

## Features

- FastAPI-based REST API for handling rendering requests
- Manim integration for mathematical animations
- Docker containerization for easy deployment
- Supabase integration for data persistence

## Prerequisites

- Python 3.12+
- Docker (optional, for containerized deployment)
- FFmpeg
- Cairo and Pango development libraries

## Setup

### Local Development

1. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file with your configuration:
```bash
cp .env.example .env  # If .env.example exists
# Add your environment variables
```

4. Run the development server:
```bash
uvicorn src.app:app --reload
```

### Docker Deployment

1. Build the Docker image:
```bash
docker build -t angle-render-worker .
```

2. Run the container:
```bash
docker run -p 8000:8000 angle-render-worker
```

## API Endpoints

The service runs on port 8000 by default. API documentation is available at `/docs` when the server is running.

## Integration with Angle

This service is designed to work alongside the main Angle NextJS application. The main application should be configured to send rendering requests to this service's API endpoints.

## License

MIT
