import json
from typing import Dict, Any, Literal
# pyrefly: ignore [missing-import]
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage, AIMessage
# pyrefly: ignore [missing-import]
from langgraph.graph import StateGraph, END
# pyrefly: ignore [missing-import]
from langgraph.prebuilt import ToolNode
import logging

from app.core.config import settings
from app.agents.state import ResearchAgentState
from app.agents.tools import AGENT_TOOLS, user_id_ctx

logger = logging.getLogger(__name__)

def build_agent_graph():
    # Initialize LLM
    llm = ChatOpenAI(
        model=settings.LLM_MODEL,
        temperature=settings.LLM_TEMPERATURE,
        api_key=settings.OPENAI_API_KEY
    )
    
    # Bind tools
    llm_with_tools = llm.bind_tools(AGENT_TOOLS)
    
    # Tool execution node
    tool_node = ToolNode(AGENT_TOOLS)

    def should_continue(state: ResearchAgentState) -> Literal["tools", "__end__"]:
        messages = state["messages"]
        last_message = messages[-1]
        
        # If there is no tool call, then we are done
        if not getattr(last_message, 'tool_calls', None):
            return "__end__"
            
        # Check iteration limit
        if state["iteration_count"] >= settings.MAX_AGENT_ITERATIONS:
            logger.warning(f"Agent reached max iterations ({settings.MAX_AGENT_ITERATIONS}). Stopping.")
            return "__end__"
            
        return "tools"

    async def call_model(state: ResearchAgentState) -> Dict[str, Any]:
        # Inject user context for tools
        user_id_ctx.set(state["user_id"])
        
        system_prompt = """You are an AI Research Assistant.
Your goal is to answer research questions accurately and with evidence.
You have access to a set of research tools, including tools for semantic search and for full-paper summarization.
Before using a tool, determine whether it is necessary.
Choose the most appropriate tool based on the user's request. If the user asks for a summary of an entire paper, use the `summarize_paper` tool.
After receiving a tool result, evaluate whether you have sufficient information.
If information is insufficient, you may use another tool.
Do not call tools unnecessarily.
Do not fabricate information.
For questions about uploaded papers, prioritize evidence from authorized documents.
If the available evidence is insufficient, clearly state that.
Stop when sufficient evidence has been collected.
You must respect user authorization.
Do not reveal hidden reasoning or chain-of-thought in your final answer.
Your final output should just be the clear answer to the user's question, containing citations if relevant.
When using information from the tool results, you MUST append the citation ID inline to your final answer text, e.g., [1] or [1, 2], based on the provided SOURCE_ID.
Do not invent citations. Only use the SOURCE_ID values provided in the tool results.
"""
        messages = state.get("messages", [])
        if not messages or not isinstance(messages[0], SystemMessage):
            messages = [SystemMessage(content=system_prompt)] + messages

        response = await llm_with_tools.ainvoke(messages)
        
        # Determine tools used
        tools_used = state.get("tools_used", [])
        if getattr(response, "tool_calls", None):
            for tc in response.tool_calls:
                tools_used.append(tc["name"])

        # Update state
        return {
            "messages": [response],
            "iteration_count": state.get("iteration_count", 0) + 1,
            "tools_used": tools_used,
            "final_answer": response.content if not getattr(response, "tool_calls", None) else None
        }

    # Define graph
    workflow = StateGraph(ResearchAgentState)
    
    workflow.add_node("agent", call_model)
    workflow.add_node("tools", tool_node)
    
    workflow.set_entry_point("agent")
    workflow.add_conditional_edges("agent", should_continue, {"tools": "tools", "__end__": END})
    workflow.add_edge("tools", "agent")
    
    return workflow.compile()

agent_graph = build_agent_graph()
