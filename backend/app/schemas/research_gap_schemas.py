from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class ResearchGapRequest(BaseModel):
    project_id: str = Field(..., description="The ID of the project")
    query: str = Field(..., description="The research question to find gaps for")
    literature_review_id: Optional[str] = Field(None, description="Optional ID of an existing literature review to base this on")

class GapEvidence(BaseModel):
    paper_id: str
    chunk_id: str
    page_number: int
    section: str
    text: str

class GapCandidate(BaseModel):
    gap_id: str
    title: str
    statement: str
    type: List[str]
    importance: str
    confidence: str
    evidence_summary: str
    supporting_papers: List[str]
    supporting_evidence: List[Dict[str, Any]]
    counter_evidence: List[Dict[str, Any]]
    limitations: List[str]
    why_it_matters: str
    potential_research_direction: str
    citations: List[Dict[str, Any]]

class ResearchGapResult(BaseModel):
    research_question: str
    literature_scope: str
    research_landscape: str
    identified_gaps: List[GapCandidate]
    contradictory_findings: List[str]
    overall_gap_summary: str
    citations: List[Dict[str, Any]]

class ResearchGapRecordResponse(BaseModel):
    id: str = Field(alias="_id")
    project_id: str
    literature_review_id: Optional[str]
    query: str
    paper_ids: List[str]
    result: ResearchGapResult
    status: str
    created_at: datetime
    updated_at: datetime

class ResearchGapHistoryItem(BaseModel):
    id: str
    project_id: str
    query: str
    gap_count: int
    status: str
    created_at: datetime
