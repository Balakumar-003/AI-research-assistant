from pymongo.database import Database
from fastapi import HTTPException, status
from app.agents.research_intelligence_graph import research_intelligence_graph, ResearchIntelligenceState
from app.models.research_goal_model import create_research_goal_document
from app.schemas.research_goal_schemas import ResearchGoalCreate
from bson.objectid import ObjectId

class ResearchIntelligenceService:
    @staticmethod
    def create_and_analyze_goal(db: Database, user_id: str, request: ResearchGoalCreate) -> dict:
        from app.services.paper_service import validate_object_id
        project_obj_id = validate_object_id(request.project_id)
        
        project = db.projects.find_one({"_id": project_obj_id, "user_id": user_id})
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
            
        doc = create_research_goal_document(
            user_id=user_id,
            project_id=request.project_id,
            topic=request.topic,
            objective=request.objective,
            problem_statement=request.problem_statement or ""
        )
        
        insert_res = db.research_goals.insert_one(doc)
        goal_id = str(insert_res.inserted_id)
        doc["_id"] = goal_id
        
        # Run intelligence graph asynchronously or synchronously
        import asyncio
        loop = asyncio.get_event_loop()
        final_state = loop.run_until_complete(
            ResearchIntelligenceService._run_intelligence_graph(goal_id, doc)
        )
        
        update_fields = {
            "landscape": final_state.get("landscape", {}),
            "knowledge_gaps": final_state.get("knowledge_gaps", []),
            "candidate_questions": final_state.get("candidate_questions", []),
            "candidate_methods": final_state.get("candidate_methods", []),
            "candidate_experiments": final_state.get("candidate_experiments", []),
            "roadmap": final_state.get("roadmap", []),
            "next_best_actions": final_state.get("next_best_actions", []),
            "status": "analyzed"
        }
        
        db.research_goals.update_one({"_id": insert_res.inserted_id}, {"$set": update_fields})
        doc.update(update_fields)
        
        return doc

    @staticmethod
    async def _run_intelligence_graph(goal_id: str, doc: dict) -> dict:
        initial_state: ResearchIntelligenceState = {
            "goal_id": goal_id,
            "topic": doc["topic"],
            "objective": doc["objective"],
            "workspace_context": {},
            "landscape": {},
            "knowledge_gaps": [],
            "candidate_questions": [],
            "candidate_methods": [],
            "candidate_experiments": [],
            "roadmap": [],
            "next_best_actions": [],
            "errors": []
        }
        
        return await research_intelligence_graph.ainvoke(initial_state)

    @staticmethod
    def get_goal(db: Database, user_id: str, goal_id: str) -> dict:
        from app.services.paper_service import validate_object_id
        obj_id = validate_object_id(goal_id)
        
        doc = db.research_goals.find_one({"_id": obj_id, "user_id": user_id})
        if not doc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Research goal not found")
            
        doc["_id"] = str(doc["_id"])
        return doc

research_intelligence_service = ResearchIntelligenceService()
