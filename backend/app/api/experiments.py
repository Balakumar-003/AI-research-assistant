from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Any
from app.services.auth_service import get_current_user
from app.database.connection import get_db
from pymongo.database import Database
from app.schemas.experiment_schemas import (
    ExperimentCreate,
    MetricUpdate,
    ExperimentResultResponse
)
from app.services.experiment_service import experiment_service

router = APIRouter(prefix="/workspaces/{workspace_id}/experiments", tags=["Experiments"])

@router.post("", response_model=ExperimentResultResponse)
def queue_experiment(
    workspace_id: str,
    request: ExperimentCreate,
    current_user: dict = Depends(get_current_user),
    db: Database = Depends(get_db)
):
    if request.project_id != workspace_id:
        request.project_id = workspace_id
    
    return experiment_service.queue_experiment(
        db=db,
        user_id=current_user["uid"],
        request=request
    )

@router.get("/{experiment_id}", response_model=ExperimentResultResponse)
def get_experiment(
    workspace_id: str,
    experiment_id: str,
    current_user: dict = Depends(get_current_user),
    db: Database = Depends(get_db)
):
    return experiment_service.get_experiment(
        db=db,
        user_id=current_user["uid"],
        experiment_id=experiment_id
    )

@router.patch("/{experiment_id}/runs/{run_id}", response_model=ExperimentResultResponse)
def update_run_metrics(
    workspace_id: str,
    experiment_id: str,
    run_id: str,
    update: MetricUpdate,
    current_user: dict = Depends(get_current_user),
    db: Database = Depends(get_db)
):
    return experiment_service.update_run_metrics(
        db=db,
        user_id=current_user["uid"],
        experiment_id=experiment_id,
        run_id=run_id,
        update=update
    )

@router.post("/{experiment_id}/analyze", response_model=ExperimentResultResponse)
async def analyze_experiment(
    workspace_id: str,
    experiment_id: str,
    current_user: dict = Depends(get_current_user),
    db: Database = Depends(get_db)
):
    return await experiment_service.analyze_experiment(
        db=db,
        user_id=current_user["uid"],
        experiment_id=experiment_id
    )
