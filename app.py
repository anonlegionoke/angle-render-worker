from fastapi import FastAPI, HTTPException
from models import FrameRequest, RenderRequest, RenderResponse
from renderer import render
from processor import delete_all_thumbnails, generate_thumbnails
import uvicorn

app = FastAPI()

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/render", response_model=RenderResponse)
async def render_video(data: RenderRequest):
    try:
        video_url = await render(
            data.code, data.scene_name, data.job_id, data.project_id
        )
        return RenderResponse(video_url=video_url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/frames")
async def process_frames(data: FrameRequest):
    try:
        response = generate_thumbnails(data.videoUrl, data.promptId)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.delete("/frames")
async def clear_thumbnails(data: FrameRequest):
    try:
        delete_all_thumbnails(data.promptId)
        return {"message": "All thumbnails deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
