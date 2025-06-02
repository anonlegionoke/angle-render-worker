# src/app.py
from fastapi import FastAPI, HTTPException
from models import RenderRequest, RenderResponse
from renderer import render

app = FastAPI()

@app.post("/render", response_model=RenderResponse)
async def render_video(data: RenderRequest):
    try:
        video_url = await render(
            data.code, data.scene_name, data.job_id, data.project_id
        )
        return RenderResponse(video_url=video_url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/process_frames")
async def process_frames(data: RenderRequest):
    try:
        video_url = await render(
            data.code, data.scene_name, data.job_id, data.project_id
        )
        return RenderResponse(video_url=video_url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))