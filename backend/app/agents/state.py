from typing import TypedDict, List, Dict, Any, Optional

class ResearchAgentState(TypedDict):
    # Core inputs
    question: str
    user_id: str
    project_id: Optional[str]
    paper_ids: Optional[List[str]]
    
    # LangGraph message state (for LLM context)
    messages: List[Dict[str, Any]]
    
    # Execution state
    iteration_count: int
    
    # Final output
    final_answer: Optional[str]
    sources: List[Dict[str, Any]]
    tools_used: List[str]
