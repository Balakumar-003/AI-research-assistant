import pytest
import json
from unittest.mock import AsyncMock, patch
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

from app.agents.state import ResearchAgentState
from app.agents.graph import build_agent_graph

@pytest.mark.asyncio
@patch("app.agents.tools.vector_store")
@patch("app.agents.tools.embedding_provider")
async def test_search_paper_tool(mock_embedding, mock_vector_store):
    from app.agents.tools import search_paper
    
    mock_embedding.embed_query.return_value = [0.1]
    mock_vector_store.search = AsyncMock(return_value=[
        {"score": 0.9, "chunk_id": "c1", "paper_id": "p1", "text": "Paper details"}
    ])
    
    # Run tool (requires injecting user_id to context)
    from app.agents.tools import user_id_ctx
    user_id_ctx.set("user1")
    
    result = await search_paper.ainvoke({"query": "details", "paper_id": "p1"})
    
    parsed = json.loads(result)
    assert parsed["success"] is True
    assert len(parsed["results"]) == 1
    assert parsed["results"][0]["chunk_id"] == "c1"

@pytest.mark.asyncio
@patch("app.agents.graph.ChatOpenAI")
async def test_agent_graph_stops_without_tools(mock_llm_class):
    # Setup mock LLM that returns a normal string answer (no tools)
    mock_llm_instance = AsyncMock()
    mock_llm_instance.bind_tools.return_value = mock_llm_instance
    mock_llm_instance.ainvoke.return_value = AIMessage(content="Direct answer.")
    mock_llm_class.return_value = mock_llm_instance
    
    from app.agents.graph import build_agent_graph
    # Re-compile to pick up the patch
    agent_graph = build_agent_graph()
    
    state = {
        "question": "What is AI?",
        "user_id": "u1",
        "project_id": "pr1",
        "paper_ids": ["p1"],
        "messages": [HumanMessage(content="What is AI?")],
        "iteration_count": 0
    }
    
    final_state = await agent_graph.ainvoke(state)
    
    assert final_state["final_answer"] == "Direct answer."
    assert final_state["iteration_count"] == 1
    assert len(final_state["tools_used"]) == 0

@pytest.mark.asyncio
@patch("app.agents.graph.ChatOpenAI")
async def test_agent_graph_max_iterations(mock_llm_class):
    # Setup mock LLM that always returns a tool call to simulate an infinite loop
    mock_llm_instance = AsyncMock()
    mock_llm_instance.bind_tools.return_value = mock_llm_instance
    mock_llm_instance.ainvoke.return_value = AIMessage(
        content="",
        tool_calls=[{"name": "search_paper", "args": {"query": "test", "paper_id": "p1"}, "id": "call_123"}]
    )
    mock_llm_class.return_value = mock_llm_instance
    
    from app.agents.graph import build_agent_graph
    from app.core.config import settings
    
    agent_graph = build_agent_graph()
    
    state = {
        "question": "Keep searching?",
        "user_id": "u1",
        "project_id": "pr1",
        "paper_ids": ["p1"],
        "messages": [HumanMessage(content="Keep searching?")],
        "iteration_count": settings.MAX_AGENT_ITERATIONS - 1 # One step away from limit
    }
    
    # It will run the agent node, iteration goes to MAX, then should_continue should return __end__
    # But wait, should_continue runs AFTER agent node. 
    # If the LLM generates a tool call, and iteration_count >= MAX, should_continue returns __end__.
    # The actual graph will terminate without executing the tool.
    
    final_state = await agent_graph.ainvoke(state)
    
    assert final_state["iteration_count"] == settings.MAX_AGENT_ITERATIONS
    assert final_state["final_answer"] is None # It stopped midway
