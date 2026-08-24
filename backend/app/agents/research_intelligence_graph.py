from typing import TypedDict, List, Dict, Any, Optional
from langgraph.graph import StateGraph, END

class ResearchIntelligenceState(TypedDict):
    goal_id: str
    topic: str
    objective: str
    
    workspace_context: Dict[str, Any]
    landscape: Dict[str, Any]
    knowledge_gaps: List[Dict[str, Any]]
    candidate_questions: List[Dict[str, Any]]
    candidate_methods: List[Dict[str, Any]]
    candidate_experiments: List[Dict[str, Any]]
    roadmap: List[Dict[str, Any]]
    next_best_actions: List[Dict[str, Any]]
    errors: List[str]

def context_analyzer(state: ResearchIntelligenceState) -> ResearchIntelligenceState:
    # Gather context from vector DB, proposals, etc.
    state["workspace_context"] = {"papers_count": 5, "experiments_run": 0}
    return state

def landscape_generator(state: ResearchIntelligenceState) -> ResearchIntelligenceState:
    state["landscape"] = {
        "major_areas": ["Area A", "Area B"],
        "dominant_methodologies": ["Method X"]
    }
    return state

def gap_analyzer(state: ResearchIntelligenceState) -> ResearchIntelligenceState:
    state["knowledge_gaps"] = [
        {"description": f"Lack of evidence regarding {state['topic']}", "confidence": "HIGH"}
    ]
    return state

def question_generator(state: ResearchIntelligenceState) -> ResearchIntelligenceState:
    state["candidate_questions"] = [
        {"question": f"How does {state['topic']} affect performance?", "type": "exploratory"}
    ]
    return state

def method_experiment_planner(state: ResearchIntelligenceState) -> ResearchIntelligenceState:
    state["candidate_methods"] = [{"method": "Method X", "rationale": "Standard baseline"}]
    state["candidate_experiments"] = [{"name": "Baseline Exp", "information_gain": 0.8}]
    return state

def roadmap_generator(state: ResearchIntelligenceState) -> ResearchIntelligenceState:
    state["roadmap"] = [{"phase": 1, "description": "Literature Review"}]
    state["next_best_actions"] = [
        {"action_type": "READ_PAPER", "description": "Review top 3 papers", "reason": "To build initial context", "requires_approval": False}
    ]
    return state

def build_research_intelligence_graph():
    workflow = StateGraph(ResearchIntelligenceState)
    
    workflow.add_node("context_analyzer", context_analyzer)
    workflow.add_node("landscape_generator", landscape_generator)
    workflow.add_node("gap_analyzer", gap_analyzer)
    workflow.add_node("question_generator", question_generator)
    workflow.add_node("method_experiment_planner", method_experiment_planner)
    workflow.add_node("roadmap_generator", roadmap_generator)
    
    workflow.set_entry_point("context_analyzer")
    workflow.add_edge("context_analyzer", "landscape_generator")
    workflow.add_edge("landscape_generator", "gap_analyzer")
    workflow.add_edge("gap_analyzer", "question_generator")
    workflow.add_edge("question_generator", "method_experiment_planner")
    workflow.add_edge("method_experiment_planner", "roadmap_generator")
    workflow.add_edge("roadmap_generator", END)
    
    return workflow.compile()

research_intelligence_graph = build_research_intelligence_graph()
