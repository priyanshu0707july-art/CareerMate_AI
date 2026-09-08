import pytest
from unittest.mock import patch, MagicMock
from app.services.embedding_service import chunk_text
from app.services.rag_service import cosine_similarity, retrieve_context
from app.models import DocumentChunk
import json

def test_chunk_text():
    text = "Word " * 100
    chunks = chunk_text(text, chunk_size=50, overlap=10)
    
    assert len(chunks) > 1
    assert len(chunks[0].split()) == 50

def test_cosine_similarity():
    v1 = [1.0, 0.0, 0.0]
    v2 = [1.0, 0.0, 0.0]
    v3 = [0.0, 1.0, 0.0]
    
    assert cosine_similarity(v1, v2) == 1.0
    assert cosine_similarity(v1, v3) == 0.0

@patch('app.services.rag_service.generate_query_embedding')
def test_retrieve_context(mock_embed):
    # Mock the query embedding
    mock_embed.return_value = [1.0, 0.0, 0.0]
    
    # Mock the database
    mock_db = MagicMock()
    
    # Create fake chunks
    chunk1 = DocumentChunk(text_content="Relevant info", embedding=json.dumps([0.9, 0.1, 0.0]))
    chunk2 = DocumentChunk(text_content="Irrelevant info", embedding=json.dumps([0.0, 1.0, 0.0]))
    
    mock_db.query().filter().all.return_value = [chunk1, chunk2]
    
    # Execute retrieval
    context = retrieve_context(mock_db, user_id=1, query="Find relevant info", top_k=1)
    
    assert "Relevant info" in context
    assert "Irrelevant info" not in context
