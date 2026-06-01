from typing import List, Dict, Any

from app.services.embeddings import embed_query
from app.services.vectorstore import get_vector_store
from app.core.config import settings


def retrieve_context(
    query: str,
    top_k: int = 5,
    min_score: float = 0.3
) -> Dict[str, Any]:
    store = get_vector_store(settings.CHROMA_PERSIST_DIR)
    if not store.is_available:
        return {
            'chunks': [], 'query': query,
            'needs_fallback': True,
            'reason': 'Vector store not available'
        }
    stats = store.get_collection_stats()
    if stats['count'] == 0:
        return {
            'chunks': [], 'query': query,
            'needs_fallback': True,
            'reason': 'No documents in vector store'
        }
    query_emb = embed_query(query, settings.EMBEDDING_MODEL)
    if query_emb is None:
        return {
            'chunks': [], 'query': query,
            'needs_fallback': True,
            'reason': 'Embedding model not available'
        }
    results = store.search(query_emb, k=top_k)
    graded = _grade_relevance(results, min_score)
    return {
        'chunks': graded,
        'query': query,
        'needs_fallback': len(graded) == 0,
        'reason': 'No relevant chunks found above threshold' if not graded else None
    }


def _grade_relevance(
    chunks: List[Dict[str, Any]],
    min_score: float
) -> List[Dict[str, Any]]:
    return sorted(
        [c for c in chunks if c['score'] >= min_score],
        key=lambda x: x['score'],
        reverse=True
    )
