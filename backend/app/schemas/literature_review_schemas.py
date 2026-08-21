from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class LiteratureReviewRequest(BaseModel):
    project_id: str = Field(..., description="The ID of the project")
    query: str = Field(..., description="Research question to review")
    paper_ids: List[str] = Field(default_factory=list, description="List of specific paper IDs to use. If empty, all relevant papers are used.")
    max_papers: int = Field(20, description="Max number of papers to analyze")

class LiteratureReviewTheme(BaseModel):
    name: str
    description: str
    paper_ids: List[str]
    findings: List[str]
    agreements: List[str]
    disagreements: List[str]
    citations: List[Dict[str, Any]]

class LiteratureReviewResult(BaseModel):
    research_question: str
    scope: str
    relevant_papers: List[str]
    themes: List[LiteratureReviewTheme]
    trends: List[str]
    common_limitations: List[str]
    emerging_directions: List[str]
    overall_synthesis: str
    citations: List[Dict[str, Any]]

class LiteratureReviewRecordResponse(BaseModel):
    id: str = Field(alias="_id")
    project_id: str
    query: str
    paper_ids: List[str]
    relevant_paper_ids: List[str]
    result: LiteratureReviewResult
    status: str
    created_at: datetime
    updated_at: datetime

class LiteratureReviewHistoryItem(BaseModel):
    id: str
    project_id: str
    query: str
    paper_count: int
    status: str
    created_at: datetime
