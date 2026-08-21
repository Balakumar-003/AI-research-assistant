from pymongo.database import Database
from fastapi import HTTPException, status
from app.agents.comparison_graph import comparison_graph, ComparisonState
from app.services.citation_service import CitationManager
from app.models.comparison_model import create_comparison_document
from app.schemas.comparison_schemas import ComparisonRequest, ComparisonRecordResponse

class ComparisonService:
    @staticmethod
    async def run_comparison(db: Database, user_id: str, request: ComparisonRequest) -> dict:
        # Validate papers ownership and project
        from app.services.paper_service import validate_object_id
        
        project_obj_id = validate_object_id(request.project_id)
        
        # Verify project
        project = db.projects.find_one({"_id": project_obj_id, "user_id": user_id})
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
            
        # Verify papers
        for paper_id in request.paper_ids:
            paper_obj_id = validate_object_id(paper_id)
            paper = db.papers.find_one({"_id": paper_obj_id, "user_id": user_id, "project_id": request.project_id})
            if not paper:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, 
                    detail=f"Paper {paper_id} not found in this project."
                )
                
        # Initialize state
        cm = CitationManager()
        
        initial_state: ComparisonState = {
            "user_id": user_id,
            "project_id": request.project_id,
            "paper_ids": request.paper_ids,
            "dimensions": request.dimensions,
            "query": request.query,
            "citation_manager": cm,
            "retrieved_evidence": [],
            "grouped_evidence": {},
            "dimension_comparisons": [],
            "overall_analysis": "",
            "final_result": None,
            "errors": []
        }
        
        # Run graph
        final_state = await comparison_graph.ainvoke(initial_state)
        
        if final_state.get("errors"):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=" ".join(final_state["errors"]))
            
        final_result = final_state.get("final_result")
        
        if not final_result:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Comparison failed to generate a result.")
            
        # Save to DB
        doc = create_comparison_document(
            user_id=user_id,
            project_id=request.project_id,
            paper_ids=request.paper_ids,
            dimensions=final_state.get("dimensions", []),
            query=request.query,
            result=final_result
        )
        
        insert_res = db.comparisons.insert_one(doc)
        
        doc["_id"] = str(insert_res.inserted_id)
        return doc
        
    @staticmethod
    def get_comparison(db: Database, user_id: str, comparison_id: str) -> dict:
        from app.services.paper_service import validate_object_id
        comp_obj_id = validate_object_id(comparison_id)
        
        comp = db.comparisons.find_one({"_id": comp_obj_id, "user_id": user_id})
        if not comp:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comparison not found")
            
        comp["_id"] = str(comp["_id"])
        return comp
        
    @staticmethod
    def get_project_comparisons(db: Database, user_id: str, project_id: str) -> list:
        from app.services.paper_service import validate_object_id
        proj_obj_id = validate_object_id(project_id)
        
        comps = db.comparisons.find({"project_id": project_id, "user_id": user_id}).sort("created_at", -1)
        result = []
        for c in comps:
            result.append({
                "id": str(c["_id"]),
                "project_id": c["project_id"],
                "paper_ids": c["paper_ids"],
                "dimensions": c["dimensions"],
                "created_at": c["created_at"]
            })
        return result

comparison_service = ComparisonService()
