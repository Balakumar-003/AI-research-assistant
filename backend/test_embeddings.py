import pytest
from app.providers.embedding_provider import EmbeddingProvider
from app.core.config import settings

def test_model_loads_and_embeds():
    provider = EmbeddingProvider()
    provider.model_name = "sentence-transformers/all-MiniLM-L6-v2"
    provider.load()
    
    assert provider.model is not None
    assert provider.dimension == 384
    
    texts = ["Test sentence 1", "Test sentence 2"]
    embeddings = provider.embed_documents(texts)
    
    assert len(embeddings) == 2
    assert len(embeddings[0]) == 384
    assert len(embeddings[1]) == 384

def test_embed_query():
    provider = EmbeddingProvider()
    provider.model_name = "sentence-transformers/all-MiniLM-L6-v2"
    provider.load()
    
    query = "Test query"
    embedding = provider.embed_query(query)
    
    assert len(embedding) == 384

def test_semantic_sanity():
    import numpy as np
    provider = EmbeddingProvider()
    provider.model_name = "sentence-transformers/all-MiniLM-L6-v2"
    provider.load()
    
    # Text A and B are semantically similar
    texts = [
        "The Transformer uses self-attention mechanisms.",
        "Self-attention allows the model to capture relationships between tokens.",
        "Stock prices increased significantly today."
    ]
    embeddings = provider.embed_documents(texts)
    
    A, B, C = np.array(embeddings[0]), np.array(embeddings[1]), np.array(embeddings[2])
    
    # Cosine similarity
    sim_AB = np.dot(A, B) / (np.linalg.norm(A) * np.linalg.norm(B))
    sim_AC = np.dot(A, C) / (np.linalg.norm(A) * np.linalg.norm(C))
    
    assert sim_AB > sim_AC

