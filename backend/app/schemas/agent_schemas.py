from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class AgentRequest(BaseModel):
    question: str
    paper_ids: Optional[List[str]] = None
    project_id: Optional[str] = None

class AgentResponse(BaseModel):
    answer: str
    sources: List[Dict[str, Any]] = []
    tools_used: List[str] = []
    status: str = "completed"
