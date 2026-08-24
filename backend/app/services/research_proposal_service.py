from pymongo.database import Database
from fastapi import HTTPException, status
from app.agents.research_proposal_graph import research_proposal_graph, ResearchProposalState
from app.models.research_proposal_model import create_research_proposal_document
from app.schemas.research_proposal_schemas import ResearchProposalRequest

class ResearchProposalService:
    @staticmethod
    async def generate_proposal(db: Database, user_id: str, request: ResearchProposalRequest) -> dict:
        from app.services.paper_service import validate_object_id
        project_obj_id = validate_object_id(request.project_id)
        
        # Verify project
        project = db.projects.find_one({"_id": project_obj_id, "user_id": user_id})
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
            
        initial_state: ResearchProposalState = {
            "user_id": user_id,
            "project_id": request.project_id,
            "research_question_id": request.research_question_id,
            "research_question": {},
            "research_gap": {},
            "literature_context": {},
            "proposal": {},
            "errors": []
        }
        
        final_state = await research_proposal_graph.ainvoke(initial_state)
        
        if final_state.get("errors"):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=" ".join(final_state["errors"]))
            
        proposal_data = final_state.get("proposal")
        
        if not proposal_data:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to generate proposal.")
            
        doc = create_research_proposal_document(
            user_id=user_id,
            project_id=request.project_id,
            research_question_id=request.research_question_id,
            research_gap_id=final_state.get("research_gap", {}).get("id", ""),
            proposal_data=proposal_data,
            status="completed"
        )
        
        insert_res = db.research_proposals.insert_one(doc)
        doc["_id"] = str(insert_res.inserted_id)
        return doc

    @staticmethod
    def get_proposal(db: Database, user_id: str, proposal_id: str) -> dict:
        from app.services.paper_service import validate_object_id
        obj_id = validate_object_id(proposal_id)
        
        doc = db.research_proposals.find_one({"_id": obj_id, "user_id": user_id})
        if not doc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Research proposal not found")
            
        doc["_id"] = str(doc["_id"])
        return doc
        
    @staticmethod
    def list_proposals(db: Database, user_id: str, project_id: str) -> list:
        from app.services.paper_service import validate_object_id
        proj_obj_id = validate_object_id(project_id)
        
        docs = db.research_proposals.find({"project_id": project_id, "user_id": user_id}).sort("created_at", -1)
        result = []
        for r in docs:
            result.append({
                "id": str(r["_id"]),
                "project_id": r["project_id"],
                "research_question_id": r.get("research_question_id"),
                "title": r.get("proposal", {}).get("title"),
                "status": r.get("status", "completed"),
                "created_at": r["created_at"]
            })
        return result

research_proposal_service = ResearchProposalService()
