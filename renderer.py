import os
import shutil
from subprocess import run
from dotenv import load_dotenv
from models import RenderRequest
from processor import generate_thumbnails
from supabase_config import supabase_client, SUPABASE_BUCKET

load_dotenv()

# Main Directory
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
STORAGE_DIR = os.environ.get('STORAGE_DIR', os.path.join(PROJECT_ROOT, 'storage'))
os.makedirs(STORAGE_DIR, exist_ok=True)

# The RENDER Function
async def render(code: str, prompt_id: str, project_id: str):
    job_dir = None
    try:
        data = RenderRequest(code=code, prompt_id=prompt_id, project_id=project_id)

        job_dir, media_dir, py_path = get_job_dirs(prompt_id)

        create_dir(data, job_dir, media_dir, py_path)
        
        run(["manim", "render", "--quality=l", "--fps=30", "--disable_caching", "--media_dir", media_dir, "--output_file", "final.mp4", py_path], check=True)
        
        output_path = os.path.join(media_dir, "videos", "scene", "480p30", "final.mp4")
        
        video_url = output_path

        if supabase_client:
            try:
                print(f"Uploading to Supabase: {video_url}")
                video_url = await upload_to_supabase(output_path, prompt_id)
                print(f"Uploaded to Supabase: {video_url}")
                supabase_client.from_("prompts").update({"status": "completed", "video_url": video_url}).eq("prompt_id",prompt_id).execute()
                print(f"Updated Prompts table with status completed: {video_url}")
                generate_thumbnails(video_url, prompt_id)
                print(f"Generated thumbnails: {video_url}")
            except Exception as e:
                print(f"Failed to upload to Supabase: {e}")
        else:
            print("Supabase client not available, using local path")
        
        cleanup_job_dir(job_dir)
        
        return video_url

    except Exception as e:
        if job_dir:
            cleanup_job_dir(job_dir)
        raise RuntimeError(f"Failed to render: {str(e)}")


# Upload to Supabase
async def upload_to_supabase(file_path: str, prompt_id: str) -> str:
    """Upload a file to Supabase Storage and return a signed URL"""
    if not supabase_client:
        raise ValueError("Supabase client not initialized. Check your environment variables.")

    file_name = f"video_{prompt_id}.mp4"

    with open(file_path, 'rb') as f:
        file_data = f.read()

    supabase_path = f"{prompt_id}/{file_name}"
    response = supabase_client.storage.from_(SUPABASE_BUCKET).upload(
        path=supabase_path,
        file=file_data,
        file_options={"content-type": "video/mp4"},
    )

    if isinstance(response, dict) and response.get("error"):
        raise RuntimeError(f"Failed to upload: {response['error']['message']}")

    signed_url_response = supabase_client.storage.from_(SUPABASE_BUCKET).create_signed_url(
        path=supabase_path,
        expires_in=604800  # 7 days
    )

    if isinstance(signed_url_response, dict) and signed_url_response.get("error"):
        raise RuntimeError(f"Failed to create signed URL: {signed_url_response['error']['message']}")

    return signed_url_response["signedURL"]


# Directory Management   
def get_job_dirs(prompt_id):
    job_dir = os.path.join(STORAGE_DIR, prompt_id)
    media_dir = os.path.join(job_dir, "media")
    py_path = os.path.join(job_dir, "scene.py")
    return job_dir, media_dir, py_path

def create_dir(data: RenderRequest, job_dir, media_dir, py_path):
    os.makedirs(job_dir, exist_ok=True)
    os.makedirs(media_dir, exist_ok=True)
    with open(py_path, "w") as f:
        f.write(data.code)

def cleanup_job_dir(job_dir):
    """Remove temp dir"""
    try:
        if os.path.exists(job_dir):
            shutil.rmtree(job_dir)
            return True
    except Exception as e:
        print(f"Error cleaning up job directory: {e}")
    return False

