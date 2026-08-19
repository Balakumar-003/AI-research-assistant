from pydantic import BaseModel
from typing import Optional, List

class SearchRequest(BaseModel):
    query: str
    top_k: int = 5
    paper_id: Optional[str] = None

class SearchResultItem(BaseModel):
    faiss_id: int
    score: float
    chunk_id: str
    paper_id: str
    page_number: int
    section: str
    text: str

class SearchResponse(BaseModel):
    results: List[SearchResultItem]
    total_found: int
