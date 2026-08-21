import re
import logging
from typing import List, Dict, Any, Tuple

logger = logging.getLogger(__name__)

class CitationManager:
    def __init__(self):
        self.sources: Dict[str, Dict[str, Any]] = {}  # Map of unique source key to source data
        self.citations: Dict[int, str] = {}           # Map of citation ID to unique source key
        self.next_citation_id = 1
        
    def _generate_source_key(self, chunk: Dict[str, Any]) -> str:
        """Generate a unique key for a chunk to handle deduplication."""
        paper_id = chunk.get("paper_id", "")
        chunk_id = chunk.get("chunk_id", "")
        faiss_id = chunk.get("faiss_id", "")
        return f"{paper_id}:{chunk_id}:{faiss_id}"

    def register_chunks(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Register retrieved chunks and assign deterministic citation IDs."""
        formatted_chunks = []
        for chunk in chunks:
            source_key = self._generate_source_key(chunk)
            
            if source_key not in self.sources:
                self.sources[source_key] = {
                    "paper_id": chunk.get("paper_id"),
                    "chunk_id": chunk.get("chunk_id"),
                    "page_start": chunk.get("page_number"),
                    "page_end": chunk.get("page_number"),
                    "score": chunk.get("score"),
                    "text": chunk.get("text", "")
                }
                
                # Assign citation ID
                citation_id = self.next_citation_id
                self.citations[citation_id] = source_key
                self.sources[source_key]["citation_id"] = citation_id
                self.next_citation_id += 1
            else:
                citation_id = self.sources[source_key]["citation_id"]

            # Return a formatted version for the LLM
            formatted_chunks.append({
                "citation_id": citation_id,
                "text": chunk.get("text", ""),
                "paper_id": chunk.get("paper_id"),
                "page": chunk.get("page_number")
            })
            
        return formatted_chunks
        
    def format_for_llm(self, formatted_chunks: List[Dict[str, Any]]) -> str:
        """Format chunks into a string for the LLM context."""
        context = ""
        for fc in formatted_chunks:
            context += f"SOURCE_ID: {fc['citation_id']}\n"
            context += f"PAPER_ID: {fc['paper_id']}\n"
            if fc['page']:
                context += f"PAGE: {fc['page']}\n"
            context += f"TEXT:\n{fc['text']}\n\n"
        return context

    def validate_citations(self, text: str) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Extract citations like [1] from text, validate them against registered sources,
        strip invalid ones, and return the cleaned text and the actual valid sources used.
        """
        # Find all [N] or [N, M] patterns
        valid_sources_used = {}
        
        def replace_citation(match):
            inner = match.group(1)
            # Find all numbers in the bracket
            ids = re.findall(r'\d+', inner)
            valid_ids = []
            for id_str in ids:
                try:
                    cid = int(id_str)
                    if cid in self.citations:
                        valid_ids.append(cid)
                        valid_sources_used[cid] = self.sources[self.citations[cid]]
                except ValueError:
                    pass
            
            if not valid_ids:
                return ""
                
            # Reconstruct the citation
            return "".join([f"[{vid}]" for vid in valid_ids])

        # Match [1], [1, 2], [1,2,3], [1][2] etc.
        cleaned_text = re.sub(r'\[([\d\s,]+)\]', replace_citation, text)
        
        # Format the final valid sources list to return
        final_sources = []
        for cid, source in valid_sources_used.items():
            final_sources.append({
                "citation_id": str(cid),
                "paper_id": source.get("paper_id"),
                "chunk_id": source.get("chunk_id"),
                "page_start": source.get("page_start"),
                "page_end": source.get("page_end"),
                "score": source.get("score")
            })
            
        # Clean up any leftover empty brackets
        cleaned_text = re.sub(r'\[\]', '', cleaned_text)
        
        # Clean up space before punctuation left when stripping citations
        cleaned_text = re.sub(r'\s+([.,;:?!])', r'\1', cleaned_text)
        
        return cleaned_text.strip(), final_sources
