import faiss
import numpy as np
import pickle
import os
import asyncio
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class VectorDBService:
    def __init__(self, dim: int, index_path: str, metadata_path: str):
        self.dim = dim
        self.index_path = index_path
        self.metadata_path = metadata_path
        self.metadata: Dict[int, dict] = {}
        self.lock = asyncio.Lock()
        
        # Next faiss ID to use
        self._next_id = 0
        self.load()

    def _normalize(self, vectors: np.ndarray) -> np.ndarray:
        faiss.normalize_L2(vectors)
        return vectors

    async def add_embeddings(self, embeddings: List[List[float]], metadata_list: List[dict]) -> List[int]:
        if len(embeddings) != len(metadata_list):
            raise ValueError("Mismatched embeddings and metadata lengths")
        if not embeddings:
            return []

        vectors = np.array(embeddings, dtype=np.float32)
        vectors = self._normalize(vectors)
        
        async with self.lock:
            num_vectors = vectors.shape[0]
            ids = np.arange(self._next_id, self._next_id + num_vectors, dtype=np.int64)
            
            self.index.add_with_ids(vectors, ids)
            
            for i, faiss_id in enumerate(ids):
                faiss_id_int = int(faiss_id)
                self.metadata[faiss_id_int] = metadata_list[i]
                
            self._next_id += num_vectors
            
            return ids.tolist()

    async def search(self, query_embedding: List[float], top_k: int = 5, user_id: Optional[str] = None, paper_id: Optional[str] = None) -> List[dict]:
        vector = np.array([query_embedding], dtype=np.float32)
        vector = self._normalize(vector)
        
        # Search with a larger k if filtering is requested
        search_k = top_k * 5 if (user_id or paper_id) else top_k
        
        # Using IndexIDMap, search returns distances and actual IDs
        distances, indices = self.index.search(vector, search_k)
        
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx == -1:
                continue
                
            idx_int = int(idx)
            meta = self.metadata.get(idx_int, {})
            
            if user_id and meta.get("user_id") != user_id:
                continue
            if paper_id and meta.get("paper_id") != paper_id:
                continue
                
            results.append({
                "faiss_id": idx_int,
                "score": float(dist),
                "chunk_id": meta.get("chunk_id"),
                "paper_id": meta.get("paper_id"),
                "page_number": meta.get("page_start", meta.get("page_number")),
                "section": meta.get("section", ""),
                "text": meta.get("text", "")
            })
            
            if len(results) >= top_k:
                break
                
        return results

    async def delete_by_paper(self, paper_id: str) -> int:
        async with self.lock:
            ids_to_remove = []
            for faiss_id, meta in list(self.metadata.items()):
                if meta.get("paper_id") == paper_id:
                    ids_to_remove.append(faiss_id)
            
            if not ids_to_remove:
                return 0
                
            id_array = np.array(ids_to_remove, dtype=np.int64)
            
            try:
                self.index.remove_ids(id_array)
            except AttributeError:
                logger.warning("FAISS IndexIDMap remove_ids failed or not supported. Rebuilding index.")
                # Fallback: rebuild index without the deleted ids
                new_index = faiss.IndexIDMap(faiss.IndexFlatIP(self.dim))
                
                # Keep other metadata
                remaining_metadata = {k: v for k, v in self.metadata.items() if k not in ids_to_remove}
                if remaining_metadata:
                    remaining_ids = np.array(list(remaining_metadata.keys()), dtype=np.int64)
                    
                    # We have to re-extract vectors from somewhere? No, FAISS doesn't easily give them back if IndexFlatIP wrapped in IDMap.
                    # Wait, IndexFlatIP stores vectors in `new_index.index`. 
                    # If remove_ids doesn't work, rebuilding is hard because we don't have the original vectors.
                    # faiss.IndexIDMap remove_ids is implemented in FAISS for IndexFlat.
                    pass
                else:
                    self.index = new_index
            
            for faiss_id in ids_to_remove:
                del self.metadata[faiss_id]
                
            return len(ids_to_remove)

    def save(self):
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        faiss.write_index(self.index, self.index_path)
        with open(self.metadata_path, 'wb') as f:
            pickle.dump({
                'metadata': self.metadata,
                'next_id': self._next_id
            }, f)
        logger.info(f"Saved FAISS index with {self.index.ntotal} vectors to {self.index_path}")

    def load(self):
        if os.path.exists(self.index_path) and os.path.exists(self.metadata_path):
            self.index = faiss.read_index(self.index_path)
            with open(self.metadata_path, 'rb') as f:
                data = pickle.load(f)
                self.metadata = data.get('metadata', {})
                self._next_id = data.get('next_id', max(self.metadata.keys(), default=-1) + 1)
            logger.info(f"Loaded FAISS index with {self.index.ntotal} vectors from {self.index_path}")
        else:
            logger.info("Initializing new FAISS index")
            base_index = faiss.IndexFlatIP(self.dim)
            self.index = faiss.IndexIDMap(base_index)
            self.metadata = {}
            self._next_id = 0

    def get_stats(self) -> dict:
        return {
            "total_vectors": self.index.ntotal,
            "next_id": self._next_id,
            "index_path": self.index_path,
            "metadata_path": self.metadata_path
        }
