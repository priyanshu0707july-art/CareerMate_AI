import logging
import math
import google.generativeai as genai
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.config import settings
from app.models import DocumentChunk
from app.services.embedding_service import EMBEDDING_MODEL

logger = logging.getLogger(__name__)

def generate_query_embedding(query: str) -> List[float]:
    """Generates an embedding vector for a search query using Gemini API."""
    try:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        result = genai.embed_content(
            model=EMBEDDING_MODEL,
            content=query,
            task_type="retrieval_query"
        )
        return result['embedding']
    except Exception as e:
        logger.error(f"Failed to generate query embedding: {e}")
        return []

def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    """Calculates cosine similarity between two vectors."""
    if len(v1) != len(v2) or len(v1) == 0:
        return 0.0
    dot_product = sum(a * b for a, b in zip(v1, v2))
    norm_v1 = math.sqrt(sum(a * a for a in v1))
    norm_v2 = math.sqrt(sum(b * b for b in v2))
    if norm_v1 == 0 or norm_v2 == 0:
        return 0.0
    return dot_product / (norm_v1 * norm_v2)

def retrieve_context(db: Session, user_id: int, query: str, top_k: int = 3) -> str:
    """
    Retrieves the most relevant document chunks for a given query.
    Falls back to Python-based cosine similarity if pgvector is unavailable (e.g. SQLite tests).
    """
    query_vector = generate_query_embedding(query)
    if not query_vector:
        return ""
        
    # Get all chunks for the user
    # In a pure Postgres environment, we'd use:
    # chunks = db.query(DocumentChunk).filter(DocumentChunk.user_id == user_id).order_by(DocumentChunk.embedding.cosine_distance(query_vector)).limit(top_k).all()
    # But for cross-compatibility with our SQLite test database, we will fetch and sort in memory.
    # Note: For production with millions of rows, pgvector indexing is required.
    
    all_chunks = db.query(DocumentChunk).filter(DocumentChunk.user_id == user_id).all()
    
    if not all_chunks:
        return ""
        
    scored_chunks = []
    for chunk in all_chunks:
        if chunk.embedding:
            # Handle possible stringified JSON in SQLite
            if isinstance(chunk.embedding, str):
                import json
                try:
                    embedding = json.loads(chunk.embedding)
                except:
                    continue
            else:
                embedding = chunk.embedding
                
            score = cosine_similarity(query_vector, embedding)
            scored_chunks.append((score, chunk.text_content))
            
    # Sort by descending similarity score
    scored_chunks.sort(key=lambda x: x[0], reverse=True)
    
    top_chunks = scored_chunks[:top_k]
    
    # Combine texts
    context_text = "\n\n---\n\n".join([chunk for score, chunk in top_chunks])
    return context_text
