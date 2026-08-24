from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class ExperimentCreate(BaseModel):
    project_id: str = Field(..., description="The ID of the project")
    proposal_id: str = Field(..., description="The ID of the proposal")
    research_question_id: str = Field(..., description="The ID of the research question")
    name: str = "Unnamed Experiment"
    objective: str = ""
    type: str = "evaluation"
    baseline: Dict[str, Any] = {}
    treatment: Dict[str, Any] = {}
    dataset: str = ""
    model: str = ""
    configuration: Dict[str, Any] = {}
    random_seed: int = 42

class MetricUpdate(BaseModel):
    metrics: Dict[str, float]
    status: str = "completed"
    error_message: Optional[str] = None

class ExperimentRunResponse(BaseModel):
    id: str = Field(alias="_id")
    experiment_id: str
    run_number: int
    random_seed: int
    status: str
    metrics: Dict[str, float]
    error_message: Optional[str]
    started_at: datetime
    completed_at: Optional[datetime]

class ExperimentResultResponse(BaseModel):
    id: str = Field(alias="_id")
    project_id: str
    proposal_id: str
    research_question_id: str
    name: str
    status: str
    runs: List[ExperimentRunResponse]
    analysis_results: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
