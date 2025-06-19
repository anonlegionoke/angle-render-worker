# angle-render-worker

A background rendering system for the Angle AI editor/generator, now powered by GitHub Actions. This service handles the rendering of mathematical animations and visualizations using Manim, running in a reproducible Docker environment, and is triggered via the GitHub API for scalable, isolated processing.

## Architecture

- **GitHub Actions-based:** Rendering jobs are executed as GitHub Actions workflows, triggered via the GitHub API.
- **Dockerized Environment:** Uses a prebuilt Docker image with Manim, FFmpeg, texlive-full, and other dependencies for fast, consistent rendering.
- **Supabase Integration:** Outputs (videos, thumbnails) are uploaded to Supabase Storage for persistence and sharing.
- **Triggering Jobs:** The main Angle NextJS application triggers rendering by calling the GitHub API to dispatch the workflow, passing user code and metadata as inputs.

## Features

- GitHub Actions workflow for isolated, scalable rendering
- Manim integration for mathematical animations
- Docker containerization for reproducible builds
- Supabase integration for video and thumbnail storage

## Prerequisites

- GitHub account and repository access
- Python 3.10+ (for local development/testing)
- Docker (for building/testing the image locally)
- FFmpeg, Cairo, and Pango libraries (preinstalled in Docker)
- Supabase project and credentials

## How It Works

1. **Triggering a Render:**
   - The Angle NextJS app (or any client) calls the GitHub API to dispatch the `Angle Render Worker` workflow, providing:
     - `code_url`: URL to the user Python code file
     - `prompt_id`: Unique prompt identifier
     - `project_id`: Project identifier
2. **Workflow Execution:**
   - The workflow runs in a Docker container with all dependencies preinstalled.
   - Downloads the user code, runs the rendering logic (`video_worker.py`), and uploads the resulting video and thumbnails to Supabase.
3. **Results:**
   - The workflow writes the output video URL to `video_url.txt` and updates Supabase with the results.

## GitHub Actions Workflow

The workflow file is located at `.github/workflows/render.yml`. It defines the job steps, including container setup, code download, rendering, and uploading results to Supabase.

## Integration with Angle

This service is designed to work as a background service for the main Angle NextJS application. The main Angle NextJS application should be configured to trigger the GitHub Actions workflow via the GitHub API, passing the required inputs. Results are stored in Supabase and can be accessed by the main application.

Check Repo - https://github.com/anonlegionoke/angle

## License

MIT
