import os
import uuid
import shutil
import requests
import subprocess

THUMBNAILS_DIR = os.path.join(os.getcwd(), 'public', 'thumbnails')
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

def generate_thumbnails(video_url: str) -> list[str]:
    ensure_directories()

    if not video_url:
        raise ValueError("Missing video URL")

    video_id = str(uuid.uuid4())
    input_path = os.path.join(TMP_DIR, f"{video_id}.mp4")

    response = requests.get(video_url, stream=True)
    if response.status_code != 200:
        raise RuntimeError("Failed to download video")

    with open(input_path, 'wb') as f:
        shutil.copyfileobj(response.raw, f)

    duration = get_video_duration(input_path)
    frame_count = max(1, int(duration // 2))

    output_pattern = os.path.join(THUMBNAILS_DIR, f"thumb_{video_id}_%02d.jpg")
    cmd = [
        'ffmpeg', '-i', input_path,
        '-vf', f'fps={frame_count / duration:.2f}',
        '-vframes', str(frame_count),
        output_pattern
    ]

    subprocess.run(cmd, check=True)

    os.remove(input_path)

    thumbnails = [
        f"/thumbnails/thumb_{video_id}_{str(i + 1).zfill(2)}.jpg"
        for i in range(frame_count)
    ]

    return thumbnails

def delete_all_thumbnails() -> int:
    ensure_directories()
    deleted_count = 0

    if os.path.exists(THUMBNAILS_DIR):
        for filename in os.listdir(THUMBNAILS_DIR):
            filepath = os.path.join(THUMBNAILS_DIR, filename)
            try:
                os.remove(filepath)
                deleted_count += 1
            except Exception as e:
                print(f"Failed to delete {filename}: {e}")

    return deleted_count
