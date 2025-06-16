from pydantic import BaseModel
from typing import Optional

class RenderRequest(BaseModel):
    code: str
    prompt_id: str
    project_id: str

class RenderResponse(BaseModel):
    video_url: str

class FrameRequest(BaseModel):
    videoUrl: Optional[str] = None
    promptId: Optional[str] = None