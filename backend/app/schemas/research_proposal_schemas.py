from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class ResearchProposalRequest(BaseModel):
    project_id: str = Field(..., description="The ID of the project")
    research_question_id: str = Field(..., description="ID of the selected research question")

class Experiment(BaseModel):
    id: str
    objective: str
    method: str
    dataset: str
    metrics: List[str]

class DatasetRecommendation(BaseModel):
    name: str
    domain: str
    purpose: str
    relevance: int
    availability: int
    fit: int
    overall_score: float

class ProposalData(BaseModel):
    title: str
    abstract: str
    problem_statement: str
    motivation: str
    objectives: List[str]
    methodology: Dict[str, Any]
    dataset_requirements: Dict[str, Any]
    dataset_recommendations: List[DatasetRecommendation]
    preprocessing: List[str]
    baselines: List[Dict[str, Any]]
    proposed_approach: Dict[str, Any]
    experiments: List[Experiment]
    evaluation_metrics: List[Dict[str, Any]]
    ablation_studies: List[Dict[str, Any]]
    statistical_analysis: Dict[str, Any]
    expected_outcomes: List[str]
    contributions: List[str]
    limitations: List[str]
    threats_to_validity: List[str]
    reproducibility_plan: Dict[str, Any]
    timeline: List[str]
    citations: List[Dict[str, Any]]

class ResearchProposalResponse(BaseModel):
    id: str = Field(alias="_id")
    project_id: str
    research_question_id: str
    research_gap_id: str
    proposal: ProposalData
    status: str
    created_at: datetime
    updated_at: datetime
