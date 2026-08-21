from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class ComparisonRequest(BaseModel):
    project_id: str = Field(..., description="The ID of the project")
    paper_ids: List[str] = Field(..., description="List of paper IDs to compare")
    dimensions: List[str] = Field(default_factory=list, description="Dimensions to compare on, e.g. 'Methodology', 'Results'")
    query: Optional[str] = Field(None, description="Custom natural language query for comparison")

class ComparisonEvidence(BaseModel):
    text: str
    page: Optional[int]
    chunk_id: str

class PaperComparisonResult(BaseModel):
    paper_id: str
    summary: str
    citations: List[Dict[str, Any]] = []

class DimensionComparison(BaseModel):
    dimension: str
    papers: List[PaperComparisonResult]
    similarities: List[str] = []
    differences: List[str] = []
    analysis: str = ""
    citations: List[Dict[str, Any]] = []

class ComparisonResult(BaseModel):
    comparisons: List[DimensionComparison]
    overall_analysis: str = ""
    limitations: List[str] = []

class ComparisonRecordResponse(BaseModel):
    id: str = Field(alias="_id")
    project_id: str
    paper_ids: List[str]
    dimensions: List[str]
    query: Optional[str]
    result: ComparisonResult
    created_at: datetime
    updated_at: datetime

class ComparisonHistoryItem(BaseModel):
    id: str
    project_id: str
    paper_ids: List[str]
    dimensions: List[str]
    created_at: datetime
