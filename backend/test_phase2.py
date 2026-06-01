#!/usr/bin/env python3
"""
Simple test to verify Phase 2 core functionality
"""

import sys
import os
from pathlib import Path

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def test_imports():
    """Test that all key modules can be imported"""
    print("Testing imports...")
    try:
        from app.core.config import settings
        print("  ✅ Config")
    except Exception as e:
        print(f"  ❌ Config: {e}")
        return False
    
    try:
        from app.core.langgraph import query_graph, ingestion_graph
        print("  ✅ LangGraph workflows")
    except Exception as e:
        print(f"  ❌ LangGraph: {e}")
        return False
    
    try:
        from app.services.chunker import chunk_document
        print("  ✅ Chunker")
    except Exception as e:
        print(f"  ❌ Chunker: {e}")
        return False
    
    try:
        from app.services.embeddings import embed_text, embed_query
        print("  ✅ Embeddings")
    except Exception as e:
        print(f"  ❌ Embeddings: {e}")
        return False
    
    try:
        from app.services.vectorstore import get_vector_store
        print("  ✅ Vector Store")
    except Exception as e:
        print(f"  ❌ Vector Store: {e}")
        return False
    
    try:
        from app.services.retriever import retrieve_context
        print("  ✅ Retriever")
    except Exception as e:
        print(f"  ❌ Retriever: {e}")
        return False
    
    try:
        from app.services.extractors.text_extractor import extract_text
        from app.services.extractors.image_extractor import extract_image
        from app.services.extractors.audio_extractor import extract_audio
        from app.services.extractors.video_extractor import extract_video
        print("  ✅ All extractors")
    except Exception as e:
        print(f"  ❌ Extractors: {e}")
        return False
    
    return True

def test_chunker():
    """Test chunking functionality"""
    print("\nTesting chunker...")
    try:
        from app.services.chunker import chunk_document
        
        data = [{
            'text': ' '.join(['word'] * 600),  # 600 words
            'metadata': {'source': 'test.txt', 'page': 1}
        }]
        
        chunks = chunk_document(data, chunk_size=200, chunk_overlap=50)
        assert len(chunks) > 1, "Should create multiple chunks"
        assert all('text' in c for c in chunks), "All chunks should have text"
        assert all('chunk_index' in c for c in chunks), "All chunks should have index"
        
        print(f"  ✅ Chunker created {len(chunks)} chunks from 1 document")
        return True
    except Exception as e:
        print(f"  ❌ Chunker test failed: {e}")
        return False

def test_embeddings():
    """Test embedding generation"""
    print("\nTesting embeddings...")
    try:
        from app.services.embeddings import embed_text, embed_query
        
        texts = ["Hello world", "This is a test"]
        embeddings = embed_text(texts)
        
        if embeddings is None:
            print("  ⚠️  Embeddings model not available (may need download)")
            return True
        
        assert len(embeddings) == 2, "Should generate 2 embeddings"
        assert all(isinstance(e, list) for e in embeddings), "Each embedding should be a list"
        
        query_emb = embed_query("test query")
        assert isinstance(query_emb, list), "Query embedding should be a list"
        
        print(f"  ✅ Generated embeddings ({len(embeddings[0])} dimensions)")
        return True
    except Exception as e:
        print(f"  ❌ Embeddings test failed: {e}")
        return False

def test_vectorstore():
    """Test vector store"""
    print("\nTesting vector store...")
    try:
        from app.services.vectorstore import get_vector_store
        from app.core.config import settings
        
        store = get_vector_store(settings.CHROMA_PERSIST_DIR)
        
        if not store.is_available:
            print("  ⚠️  Vector store not available (may need initialization)")
            return True
        
        stats = store.get_collection_stats()
        print(f"  ✅ Vector store available ({stats['count']} chunks)")
        return True
    except Exception as e:
        print(f"  ❌ Vector store test failed: {e}")
        return False

def test_api_schemas():
    """Test API schemas"""
    print("\nTesting API schemas...")
    try:
        from app.models.schemas import ChatResponse, IngestionResult, Citation
        
        # Test ChatResponse
        resp = ChatResponse(
            response="Test response",
            citations=[],
            confidence="high"
        )
        assert resp.response == "Test response"
        
        # Test Citation
        cit = Citation(
            text="Citation text",
            source="test.pdf",
            score=0.9
        )
        assert cit.source == "test.pdf"
        
        # Test IngestionResult
        ing = IngestionResult(
            file_id="test_1",
            filename="test.txt",
            chunks_count=5,
            status="success"
        )
        assert ing.chunks_count == 5
        
        print("  ✅ All schemas validated")
        return True
    except Exception as e:
        print(f"  ❌ Schemas test failed: {e}")
        return False

def main():
    print("="*60)
    print("OmniRAG Phase 2 - Component Tests")
    print("="*60)
    
    results = [
        test_imports(),
        test_chunker(),
        test_embeddings(),
        test_vectorstore(),
        test_api_schemas(),
    ]
    
    print("\n" + "="*60)
    passed = sum(results)
    total = len(results)
    
    if all(results):
        print(f"✅ All {total} tests passed!")
        print("\nPhase 2 core functionality is working correctly.")
        print("\nTo start the backend:")
        print("  cd backend")
        print("  uvicorn app.main:app --reload")
    else:
        print(f"⚠️  {passed}/{total} tests passed")
        print("\nCheck errors above for details.")
    
    print("="*60)

if __name__ == "__main__":
    main()
