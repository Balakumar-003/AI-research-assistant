from typing import TypedDict, List, Dict, Any, Optional
from langgraph.graph import StateGraph, END

class ResearchProposalState(TypedDict):
    user_id: str
    project_id: str
    research_question_id: str
    
    research_question: Dict[str, Any]
    research_gap: Dict[str, Any]
    literature_context: Dict[str, Any]
    
    proposal: Dict[str, Any]
    errors: List[str]

def load_context(state: ResearchProposalState) -> ResearchProposalState:
    # Mock data loading
    state["research_question"] = {"id": state["research_question_id"], "question": "Mock question"}
    state["research_gap"] = {"id": "mock_gap_id", "statement": "Mock gap statement"}
    state["proposal"] = {}
    return state

def generate_proposal(state: ResearchProposalState) -> ResearchProposalState:
    # Mock generation
    state["proposal"] = {
        "title": "Mock Research Proposal",
        "abstract": "This is a mock abstract.",
        "problem_statement": "Mock problem statement.",
        "motivation": "Mock motivation.",
        "objectives": ["Obj 1", "Obj 2"],
        "methodology": {"type": "experimental", "description": "Mock methodology"},
        "dataset_requirements": {"domain": "NLP", "size": "10k"},
        "dataset_recommendations": [{
            "name": "Dataset A",
            "domain": "NLP",
            "purpose": "Training",
            "relevance": 9,
            "availability": 9,
            "fit": 9,
            "overall_score": 9.0
        }],
        "preprocessing": ["Tokenization"],
        "baselines": [{"name": "Baseline 1"}],
        "proposed_approach": {"description": "Proposed approach details."},
        "experiments": [{
            "id": "E1",
            "objective": "Test method",
            "method": "Method A",
            "dataset": "Dataset A",
            "metrics": ["F1"]
        }],
        "evaluation_metrics": [{"name": "F1", "justification": "Standard"}],
        "ablation_studies": [],
        "statistical_analysis": {"method": "T-test"},
        "expected_outcomes": ["Improved F1"],
        "contributions": ["Novel method"],
        "limitations": ["Compute intensive"],
        "threats_to_validity": ["Selection bias"],
        "reproducibility_plan": {"code_release": True},
        "timeline": ["Week 1: Data", "Week 2: Train"],
        "citations": []
    }
    return state

def validate_proposal(state: ResearchProposalState) -> ResearchProposalState:
    # Mock validation
    if not state["proposal"].get("title"):
        state["errors"].append("Missing title")
    return state

def build_research_proposal_graph():
    workflow = StateGraph(ResearchProposalState)
    
    workflow.add_node("load_context", load_context)
    workflow.add_node("generate_proposal", generate_proposal)
    workflow.add_node("validate_proposal", validate_proposal)
    
    workflow.set_entry_point("load_context")
    workflow.add_edge("load_context", "generate_proposal")
    workflow.add_edge("generate_proposal", "validate_proposal")
    workflow.add_edge("validate_proposal", END)
    
    return workflow.compile()

research_proposal_graph = build_research_proposal_graph()
