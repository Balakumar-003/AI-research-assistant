from typing import TypedDict, List, Dict, Any, Optional
from langgraph.graph import StateGraph, END
import json

class ResearchQuestionState(TypedDict):
    user_id: str
    project_id: str
    gap_ids: List[str]
    topic: Optional[str]
    
    research_gaps: List[Dict[str, Any]]
    literature_context: Dict[str, Any]
    
    candidate_questions: List[Dict[str, Any]]
    final_questions: List[Dict[str, Any]]
    errors: List[str]

def load_gaps_and_evidence(state: ResearchQuestionState) -> ResearchQuestionState:
    # In a real implementation, we would query the database for the gap details
    # For now, we mock the gap extraction.
    state["research_gaps"] = [{"id": gid, "statement": f"Gap for {gid}"} for gid in state["gap_ids"]]
    return state

def generate_candidate_questions(state: ResearchQuestionState) -> ResearchQuestionState:
    # Mock generation
    candidates = []
    for gap in state["research_gaps"]:
        candidates.append({
            "id": f"rq_{gap['id']}_1",
            "gap_id": gap["id"],
            "question": f"How does {gap['id']} impact the system?",
            "type": "exploratory",
            "scores": {
                "relevance": 9.0,
                "specificity": 8.0,
                "researchability": 9.0,
                "novelty": 7.0,
                "evidence_support": 8.0,
                "clarity": 9.0,
                "overall": 8.5
            },
            "hypothesis": {
                "required": False
            },
            "variables": {
                "independent": [],
                "dependent": [],
                "controls": [],
                "confounders": []
            },
            "objectives": ["Understand the impact"],
            "feasibility": {
                "data_availability": 8,
                "evaluation_availability": 8,
                "computational_feasibility": 9,
                "implementation_complexity": 7,
                "experimental_controllability": 8,
                "literature_support": 7
            },
            "research_directions": [],
            "supporting_evidence": [],
            "citations": []
        })
    state["candidate_questions"] = candidates
    return state

def finalize_questions(state: ResearchQuestionState) -> ResearchQuestionState:
    # Normally we'd filter, rank, and check overlap here
    state["final_questions"] = []
    for i, q in enumerate(state["candidate_questions"]):
        q["rank"] = i + 1
        state["final_questions"].append(q)
    return state

def build_research_question_graph():
    workflow = StateGraph(ResearchQuestionState)
    
    workflow.add_node("load_gaps_and_evidence", load_gaps_and_evidence)
    workflow.add_node("generate_candidate_questions", generate_candidate_questions)
    workflow.add_node("finalize_questions", finalize_questions)
    
    workflow.set_entry_point("load_gaps_and_evidence")
    workflow.add_edge("load_gaps_and_evidence", "generate_candidate_questions")
    workflow.add_edge("generate_candidate_questions", "finalize_questions")
    workflow.add_edge("finalize_questions", END)
    
    return workflow.compile()

research_question_graph = build_research_question_graph()
