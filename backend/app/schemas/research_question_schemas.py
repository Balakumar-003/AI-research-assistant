from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class ResearchQuestionRequest(BaseModel):
    project_id: str = Field(..., description="The ID of the project")
    gap_ids: List[str] = Field(..., description="List of gap IDs to base the questions on")
    topic: Optional[str] = Field(None, description="Optional topic for the research questions")

class Hypothesis(BaseModel):
    required: bool
    h0: Optional[str] = None
    h1: Optional[str] = None

class Variables(BaseModel):
    independent: List[str] = []
    dependent: List[str] = []
    controls: List[str] = []
    confounders: List[str] = []

class Scores(BaseModel):
    relevance: float
    specificity: float
    researchability: float
    novelty: float
    evidence_support: float
    clarity: float
    overall: float

class Feasibility(BaseModel):
    data_availability: int
    evaluation_availability: int
    computational_feasibility: int
    implementation_complexity: int
    experimental_controllability: int
    literature_support: int

class GeneratedResearchQuestion(BaseModel):
    id: str
    rank: int
    question: str
    type: str
    gap_id: str
    scores: Scores
    hypothesis: Hypothesis
    variables: Variables
    objectives: List[str]
    feasibility: Feasibility
    research_directions: List[Dict[str, Any]]
    supporting_evidence: List[Dict[str, Any]]
    citations: List[Dict[str, Any]]
    is_primary: bool = False

class ResearchQuestionRecordResponse(BaseModel):
    id: str = Field(alias="_id")
    project_id: str
    gap_ids: List[str]
    topic: Optional[str]
    research_questions: List[GeneratedResearchQuestion]
    status: str
    created_at: datetime
    updated_at: datetime

class ResearchQuestionHistoryItem(BaseModel):
    id: str
    project_id: str
    topic: Optional[str]
    question_count: int
    status: str
    created_at: datetime
