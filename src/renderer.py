import os
import shutil
from subprocess import run
from dotenv import load_dotenv
from supabase import create_client, Client
from models import RenderRequest, RenderResponse

load_dotenv()

# Main Directory
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
STORAGE_DIR = os.environ.get('STORAGE_DIR', os.path.join(PROJECT_ROOT, 'storage'))
os.makedirs(STORAGE_DIR, exist_ok=True)

# Supabase Configuration
SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY')
SUPABASE_BUCKET = os.environ.get('SUPABASE_BUCKET')

supabase_client = None
if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
        print(f"Supabase client initialized")
    except Exception as e:
        print(f"Failed to initialize Supabase client: {e}")


# The RENDER Function
async def render(code: str, scene_name: str, job_id: str, project_id: str = None):
    job_dir = None
    try:
        data = RenderRequest(code=code, scene_name=scene_name, job_id=job_id, project_id=project_id)

        job_dir, media_dir, py_path = get_job_dirs(job_id)

        create_dir(data, job_dir, media_dir, py_path)
        
        run(["manim", "render", "--disable_caching", "--media_dir", media_dir, "--output_file", "final.mp4", py_path, data.scene_name], check=True)
        
        output_path = os.path.join(media_dir, "videos", "scene", "1080p60", "final.mp4")
        
        video_url = output_path

        if supabase_client:
            try:
                video_url = await upload_to_supabase(output_path, job_id, scene_name)
                print(f"Uploaded to Supabase: {video_url}")
            except Exception as e:
                print(f"Failed to upload to Supabase: {e}")
        else:
            print("Supabase client not available, using local path")
        
        cleanup_job_dir(job_dir)
        
        return video_url

    except Exception as e:
        if job_dir:
            cleanup_job_dir(job_dir)
        return {"Failed to render": str(e)}


# Upload to Supabase
async def upload_to_supabase(file_path: str, job_id: str, scene_name: str) -> str:
    """Upload a file to Supabase Storage and return the public URL"""
    if not supabase_client:
        raise ValueError("Supabase client not initialized. Check your environment variables.")
    
    file_name = f"video.mp4"
    
    with open(file_path, 'rb') as f:
        file_data = f.read()
    
    response = supabase_client.storage.from_(SUPABASE_BUCKET).upload(
        file_name,
        file_data,
        {'content-type': 'video/mp4'}
    )
    
    public_url = supabase_client.storage.from_(SUPABASE_BUCKET).get_public_url(file_name)
    
    return public_url


# Directory Management   
def get_job_dirs(job_id):
    job_dir = os.path.join(STORAGE_DIR, job_id)
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

