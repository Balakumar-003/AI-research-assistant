from pymongo.database import Database
from fastapi import HTTPException, status
from app.agents.experiment_analysis_graph import experiment_analysis_graph, ExperimentAnalysisState
from app.models.experiment_model import create_experiment_document, create_experiment_run_document
from app.schemas.experiment_schemas import ExperimentCreate, MetricUpdate
from bson.objectid import ObjectId

class ExperimentService:
    @staticmethod
    def queue_experiment(db: Database, user_id: str, request: ExperimentCreate) -> dict:
        from app.services.paper_service import validate_object_id
        project_obj_id = validate_object_id(request.project_id)
        
        # Verify project
        project = db.projects.find_one({"_id": project_obj_id, "user_id": user_id})
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
            
        doc = create_experiment_document(
            user_id=user_id,
            project_id=request.project_id,
            proposal_id=request.proposal_id,
            research_question_id=request.research_question_id,
            experiment_data=request.dict()
        )
        
        insert_res = db.experiments.insert_one(doc)
        doc["_id"] = str(insert_res.inserted_id)
        
        # Optionally, create initial run
        run_doc = create_experiment_run_document(
            experiment_id=doc["_id"],
            run_number=1,
            random_seed=request.random_seed
        )
        db.experiment_runs.insert_one(run_doc)
        
        return doc

    @staticmethod
    def get_experiment(db: Database, user_id: str, experiment_id: str) -> dict:
        from app.services.paper_service import validate_object_id
        obj_id = validate_object_id(experiment_id)
        
        doc = db.experiments.find_one({"_id": obj_id, "user_id": user_id})
        if not doc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Experiment not found")
            
        runs = list(db.experiment_runs.find({"experiment_id": experiment_id}))
        for r in runs:
            r["_id"] = str(r["_id"])
            
        doc["runs"] = runs
        doc["_id"] = str(doc["_id"])
        return doc
        
    @staticmethod
    def update_run_metrics(db: Database, user_id: str, experiment_id: str, run_id: str, update: MetricUpdate) -> dict:
        from app.services.paper_service import validate_object_id
        
        # Verify ownership
        ExperimentService.get_experiment(db, user_id, experiment_id)
        
        run_obj_id = validate_object_id(run_id)
        run_doc = db.experiment_runs.find_one({"_id": run_obj_id, "experiment_id": experiment_id})
        
        if not run_doc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Run not found")
            
        from datetime import datetime
        db.experiment_runs.update_one(
            {"_id": run_obj_id},
            {"$set": {
                "metrics": update.metrics,
                "status": update.status,
                "error_message": update.error_message,
                "completed_at": datetime.utcnow() if update.status in ["completed", "failed"] else None
            }}
        )
        
        return ExperimentService.get_experiment(db, user_id, experiment_id)

    @staticmethod
    async def analyze_experiment(db: Database, user_id: str, experiment_id: str) -> dict:
        from app.services.paper_service import validate_object_id
        obj_id = validate_object_id(experiment_id)
        
        exp = ExperimentService.get_experiment(db, user_id, experiment_id)
        
        initial_state: ExperimentAnalysisState = {
            "experiment_id": experiment_id,
            "runs": exp.get("runs", []),
            "baseline_metrics": {},
            "treatment_metrics": {},
            "statistical_analysis": {},
            "interpretation": "",
            "conclusion": "",
            "errors": []
        }
        
        final_state = await experiment_analysis_graph.ainvoke(initial_state)
        
        if final_state.get("errors"):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=" ".join(final_state["errors"]))
            
        analysis_results = {
            "baseline_metrics": final_state.get("baseline_metrics"),
            "treatment_metrics": final_state.get("treatment_metrics"),
            "statistical_analysis": final_state.get("statistical_analysis"),
            "interpretation": final_state.get("interpretation"),
            "conclusion": final_state.get("conclusion")
        }
        
        db.experiments.update_one(
            {"_id": obj_id},
            {"$set": {"analysis_results": analysis_results}}
        )
        
        exp["analysis_results"] = analysis_results
        return exp

experiment_service = ExperimentService()
