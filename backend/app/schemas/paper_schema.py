from pydantic import BaseModel
from datetime import datetime

class PaperResponse(BaseModel):
    id: str
    filename: str
    project_id: str
    uploaded_at: datetime
