from pydantic import BaseModel
from typing import List, Optional

class ChunkResponse(BaseModel):
    chunk_id: str
    paper_id: str
    chunk_index: int
    page_start: int
    page_end: int
    text: str

class PaginatedChunksResponse(BaseModel):
    paper_id: str
    total: int
    chunks: List[ChunkResponse]

class ChunkingStatsResponse(BaseModel):
    message: str
    paper_id: str
    chunk_count: int
    chunk_size: int
    chunk_overlap: int
    status: str
