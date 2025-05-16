from pydantic import BaseModel

class RenderRequest(BaseModel):
    code: str
    scene_name: str
    job_id: str
    project_id: str | None = None

class RenderResponse(BaseModel):
    video_url: str
