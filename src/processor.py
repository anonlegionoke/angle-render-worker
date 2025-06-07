import os
import shutil
import requests
import subprocess
from supabase_config import supabase_client, SUPABASE_FRAMES_BUCKET

THUMBNAILS_DIR = os.path.join(os.getcwd(), 'public', 'thumbnails', )
TMP_DIR = os.path.join(os.getcwd(), 'tmp')

def ensure_directories():
    os.makedirs(THUMBNAILS_DIR, exist_ok=True)
    os.makedirs(TMP_DIR, exist_ok=True)

def get_video_duration(file_path):
    cmd = [
        'ffprobe', '-v', 'error', '-show_entries',
        'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1',
        file_path
    ]
    output = subprocess.check_output(cmd).decode().strip()
    return float(output)

def generate_thumbnails(video_url: str, prompt_id: str) -> list[str]:
    ensure_directories()
    signed_urls = []
    video_id = prompt_id
    input_path = os.path.join(TMP_DIR, f"{video_id}.mp4")
    output_dir = os.path.join(THUMBNAILS_DIR, video_id)

    try:
        if not video_url:
            raise ValueError("Missing video URL")

        response = requests.get(video_url, stream=True)
        if response.status_code != 200:
            raise RuntimeError("Failed to download video")

        with open(input_path, 'wb') as f:
            shutil.copyfileobj(response.raw, f)

        duration = get_video_duration(input_path)
        frame_count = max(1, int(duration // 2))
        
        os.makedirs(output_dir, exist_ok=True)

        output_pattern = os.path.join(output_dir, f"thumb_{video_id}_%02d.jpg")
        cmd = [
            'ffmpeg', '-i', input_path,
            '-vf', f'fps={frame_count / duration:.2f}',
            '-vframes', str(frame_count),
            output_pattern
        ]
        subprocess.run(cmd, check=True)

        for i in range(frame_count):
            filename = f"thumb_{video_id}_{str(i + 1).zfill(2)}.jpg"
            local_path = os.path.join(THUMBNAILS_DIR, video_id, filename)

            with open(local_path, "rb") as f:
                file_data = f.read()

            supabase_path = f"{video_id}/{filename}"
            upload_response = supabase_client.storage.from_(SUPABASE_FRAMES_BUCKET).upload(
                path=supabase_path,
                file=file_data,
                file_options={"content-type": "image/jpeg"}
            )

            if isinstance(upload_response, dict) and upload_response.get("error"):
                print(f"Failed to upload {filename}: {upload_response['error']['message']}")
                continue

            signed_url_response = supabase_client.storage.from_(SUPABASE_FRAMES_BUCKET).create_signed_url(
                path=supabase_path,
                expires_in=604800  # 7 days
            )

            if isinstance(signed_url_response, dict) and signed_url_response.get("error"):
                print(f"Failed to create signed URL for {filename}: {signed_url_response['error']['message']}")
                continue

            signed_urls.append(signed_url_response["signedURL"])

            os.remove(local_path)

        return signed_urls

    except Exception as e:
        print(f"Error during thumbnail generation: {str(e)}")
        raise
    finally:
        # Clean up temp files and directories
        if os.path.exists(input_path):
            os.remove(input_path)
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)

def delete_all_thumbnails(prompt_id: str) -> int:
    ensure_directories()
    deleted_count = 0

    try:
        files = supabase_client.storage.from_(SUPABASE_FRAMES_BUCKET).list(prompt_id)
        
        for file in files:
            try:
                supabase_client.storage.from_(SUPABASE_FRAMES_BUCKET).remove([f"{prompt_id}/{file['name']}"])
                deleted_count += 1
            except Exception as e:
                print(f"Failed to delete file {file['name']} from Supabase: {e}")
    except Exception as e:
        print(f"Failed to list or delete files from Supabase for prompt_id {prompt_id}: {e}")

    return deleted_count