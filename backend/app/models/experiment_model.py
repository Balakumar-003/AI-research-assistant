from datetime import datetime
from typing import List, Optional, Dict, Any

def create_experiment_document(
    user_id: str,
    project_id: str,
    proposal_id: str,
    research_question_id: str,
    experiment_data: Dict[str, Any],
    status: str = "queued"
) -> dict:
    now = datetime.utcnow()
    return {
        "user_id": user_id,
        "project_id": project_id,
        "proposal_id": proposal_id,
        "research_question_id": research_question_id,
        "name": experiment_data.get("name", "Unnamed Experiment"),
        "objective": experiment_data.get("objective", ""),
        "type": experiment_data.get("type", "evaluation"),
        "baseline": experiment_data.get("baseline", {}),
        "treatment": experiment_data.get("treatment", {}),
        "dataset": experiment_data.get("dataset", ""),
        "model": experiment_data.get("model", ""),
        "configuration": experiment_data.get("configuration", {}),
        "status": status,
        "runs": [],
        "analysis_results": None,
        "created_at": now,
        "updated_at": now
    }

def create_experiment_run_document(
    experiment_id: str,
    run_number: int,
    random_seed: int,
    status: str = "running"
) -> dict:
    return {
        "experiment_id": experiment_id,
        "run_number": run_number,
        "random_seed": random_seed,
        "status": status,
        "metrics": {},
        "logs": [],
        "artifacts": [],
        "error_message": None,
        "started_at": datetime.utcnow(),
        "completed_at": None
    }
