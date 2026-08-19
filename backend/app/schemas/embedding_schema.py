from pydantic import BaseModel

class EmbeddingStatsResponse(BaseModel):
    paper_id: str
    status: str
    embedding_count: int
    embedding_model: str
    embedding_dimension: int
