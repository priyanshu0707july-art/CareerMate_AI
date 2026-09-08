import logging
import google.generativeai as genai
from typing import List
from sqlalchemy.orm import Session
from app.config import settings
from app.models import DocumentChunk

logger = logging.getLogger(__name__)

# Note: Using text-embedding-004 standard for Gemini embeddings
EMBEDDING_MODEL = "models/text-embedding-004"

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """Basic text chunking algorithm."""
    words = text.split()
    chunks = []
    
    if not words:
        return []
        
    i = 0
    while i < len(words):
        chunk_words = words[i:i + chunk_size]
        chunks.append(" ".join(chunk_words))
        i += chunk_size - overlap
        
    return chunks

def generate_embedding(text: str) -> List[float]:
    """Generates an embedding vector using Gemini API."""
    try:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        result = genai.embed_content(
            model=EMBEDDING_MODEL,
            content=text,
            task_type="retrieval_document"
        )
        return result['embedding']
    except Exception as e:
        logger.error(f"Failed to generate embedding: {e}")
        # Return fallback zeros vector if API fails to prevent crashing the flow (or raise exception depending on strictness)
        # We will raise so the caller knows it failed.
        raise RuntimeError(f"Embedding generation failed: {e}")

def process_and_store_document(db: Session, user_id: int, source_id: int, source_type: str, text: str):
    """
    Chunks a document (resume or job), generates embeddings for each chunk,
    and stores them in the database.
    """
    chunks = chunk_text(text)
    
    for chunk in chunks:
        try:
            embedding = generate_embedding(chunk)
            
            doc_chunk = DocumentChunk(
                user_id=user_id,
                source_id=source_id,
                source_type=source_type,
                text_content=chunk,
                embedding=embedding
            )
            db.add(doc_chunk)
        except Exception as e:
            logger.warning(f"Failed to store chunk for {source_type} {source_id}: {e}")
            continue
            
    db.commit()
