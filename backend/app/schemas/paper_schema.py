from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class PaperResponse(BaseModel):
    id: str
    filename: str
    project_id: str
    status: str
    page_count: Optional[int]
    uploaded_at: datetime

class ProcessPaperResponse(BaseModel):
    message: str
    paper_id: str
    status: str
    page_count: Optional[int]

class ProcessingStatusResponse(BaseModel):
    paper_id: str
    status: str
    page_count: Optional[int]

class PageItem(BaseModel):
    page_number: int
    text: str
    has_text: bool

class PaginatedContentResponse(BaseModel):
    paper_id: str
    pages: List[PageItem]
    total_pages: int
    current_page: int
    limit: int
