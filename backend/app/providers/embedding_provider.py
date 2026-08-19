import logging
from typing import List, Optional
from sentence_transformers import SentenceTransformer
from app.core.config import settings

logger = logging.getLogger(__name__)

class EmbeddingProvider:
    """
    Singleton provider for the Sentence Transformers model.
    Loads the model once on startup and keeps it in memory.
    """
    def __init__(self):
        self.model: Optional[SentenceTransformer] = None
        self.model_name: str = settings.EMBEDDING_MODEL
        self.dimension: Optional[int] = None

    def load(self):
        if self.model is None:
            logger.info(f"Loading embedding model: {self.model_name}...")
            self.model = SentenceTransformer(self.model_name)
            self.dimension = self.model.get_sentence_embedding_dimension()
            logger.info(f"Embedding model loaded. Dimension: {self.dimension}")

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        if not self.model:
            raise RuntimeError("Embedding model not loaded")
        # Generate embeddings and convert to list of floats
        embeddings = self.model.encode(texts, batch_size=settings.EMBEDDING_BATCH_SIZE, convert_to_numpy=True)
        return embeddings.tolist()

    def embed_query(self, text: str) -> List[float]:
        if not self.model:
            raise RuntimeError("Embedding model not loaded")
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.tolist()

# Create a global instance
embedding_provider = EmbeddingProvider()
