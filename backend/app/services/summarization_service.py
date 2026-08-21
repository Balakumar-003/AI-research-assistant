import logging
from typing import List, Dict, Any
from app.services.llm_service import llm_service
from app.services.citation_service import CitationManager

logger = logging.getLogger(__name__)

class SummarizationService:
    def __init__(self, citation_manager: CitationManager):
        self.citation_manager = citation_manager

    def _get_map_prompt(self, summary_type: str, focus_area: str, chunk_context: str) -> List[Dict[str, str]]:
        system_msg = "You are an AI Research Assistant. Your task is to extract key information from the provided text chunks."
        
        user_msg = f"""Please summarize the following research paper chunks.
Focus specifically on: {focus_area if focus_area else 'Key points relevant to a ' + summary_type + ' summary.'}

When extracting factual claims, you MUST append the citation ID inline to the text, e.g., [1] or [1, 2], based on the provided SOURCE_ID. Do not invent citations.

CHUNKS:
{chunk_context}
"""
        return [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg}
        ]

    def _get_reduce_prompt(self, summary_type: str, focus_area: str, intermediate_summaries: str) -> List[Dict[str, str]]:
        system_msg = "You are an AI Research Assistant. Your task is to synthesize multiple intermediate summaries into a cohesive final research summary."
        
        user_msg = f"""Please synthesize the following intermediate summaries into a final structured summary.
Summary Type: {summary_type}
Focus Area: {focus_area if focus_area else 'Comprehensive overview'}

When synthesizing the text, you MUST preserve all existing inline citations like [1] or [1, 2] that support the factual claims. DO NOT drop citations, and DO NOT invent new citations. 
Format your output using Markdown sections as appropriate for the requested summary type.

INTERMEDIATE SUMMARIES:
{intermediate_summaries}
"""
        return [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg}
        ]

    async def summarize(self, chunks: List[Dict[str, Any]], summary_type: str = "standard", focus_area: str = "") -> str:
        """
        Executes a Map-Reduce summarization over the provided chunks.
        """
        if not chunks:
            return "No content available to summarize."
            
        # 1. Register all chunks with CitationManager
        formatted_chunks = self.citation_manager.register_chunks(chunks)
        
        # 2. Batch chunks for Map stage
        batch_size = 10
        intermediate_summaries = []
        
        for i in range(0, len(formatted_chunks), batch_size):
            batch = formatted_chunks[i:i + batch_size]
            chunk_context = self.citation_manager.format_for_llm(batch)
            
            messages = self._get_map_prompt(summary_type, focus_area, chunk_context)
            try:
                response_text, _ = await llm_service.generate(messages)
                intermediate_summaries.append(response_text)
            except Exception as e:
                logger.error(f"Error in Map stage summarization: {e}")
                
        if not intermediate_summaries:
            return "Failed to generate intermediate summaries."
            
        # 3. Reduce stage
        if len(intermediate_summaries) == 1:
            # If only one batch, we still pass it through reduce to get final formatting
            combined_text = intermediate_summaries[0]
        else:
            combined_text = "\n\n---\n\n".join(intermediate_summaries)
            
        messages = self._get_reduce_prompt(summary_type, focus_area, combined_text)
        
        try:
            final_summary, _ = await llm_service.generate(messages)
            return final_summary
        except Exception as e:
            logger.error(f"Error in Reduce stage summarization: {e}")
            return "Failed to synthesize final summary."
