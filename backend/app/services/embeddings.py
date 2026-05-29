from typing import List, Optional

try:
    from sentence_transformers import SentenceTransformer
    HAS_SENTENCE_TRANSFORMERS = True
except ImportError:
    HAS_SENTENCE_TRANSFORMERS = False

_embedding_model = None


def _get_model(model_name: str = "all-MiniLM-L6-v2"):
    global _embedding_model
    if _embedding_model is None and HAS_SENTENCE_TRANSFORMERS:
        _embedding_model = SentenceTransformer(model_name)
    return _embedding_model


def embed_text(
    texts: List[str],
    model_name: str = "all-MiniLM-L6-v2"
) -> Optional[List[List[float]]]:
    if not HAS_SENTENCE_TRANSFORMERS:
        return None
    model = _get_model(model_name)
    if model is None:
        return None
    return model.encode(texts, show_progress_bar=False).tolist()


def embed_query(
    query: str,
    model_name: str = "all-MiniLM-L6-v2"
) -> Optional[List[float]]:
    embeddings = embed_text([query], model_name)
    if embeddings:
        return embeddings[0]
    return None
