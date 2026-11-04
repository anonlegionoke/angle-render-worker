from dataclasses import dataclass

@dataclass
class RenderRequest:
    code: str
    prompt_id: str
    project_id: str
