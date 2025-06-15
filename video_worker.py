# video_worker.py
import os
import asyncio
from renderer import render

async def main():
    code_file = os.getenv("CODE_FILE", "user_code.py")
    prompt_id = os.getenv("PROMPT_ID")
    project_id = os.getenv("PROJECT_ID")

    with open(code_file, "r") as f:
        code = f.read()

    output_url = await render(code, prompt_id, project_id)

    with open("video_url.txt", "w") as f:
        f.write(output_url)

if __name__ == "__main__":
    asyncio.run(main())
