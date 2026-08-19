from pydantic import BaseModel
from typing import List, Optional

class ChatRequest(BaseModel):
    question: str
    project_id: Optional[str] = None
    paper_id: Optional[str] = None
    top_k: int = 6

class Citation(BaseModel):
    source_index: int
    paper: str
    page: int
    section: str = ""

class UsageInfo(BaseModel):
    prompt_tokens: int = 0
    completion_tokens: int = 0

class ChatResponse(BaseModel):
    answer: str
    citations: List[Citation]
    usage: UsageInfo
