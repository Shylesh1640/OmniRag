import uuid
from typing import List, Dict, Any, Optional

try:
    import chromadb
    from chromadb.config import Settings
    HAS_CHROMA = True
except ImportError:
    HAS_CHROMA = False


class VectorStore:
    def __init__(self, persist_dir: str = "./chroma_db"):
        self.persist_dir = persist_dir
        self.client = None
        self.collection = None
        self._init_store()

    def _init_store(self):
        if not HAS_CHROMA:
            return
        try:
            self.client = chromadb.PersistentClient(
                path=self.persist_dir,
                settings=Settings(anonymized_telemetry=False)
            )
            self.collection = self.client.get_or_create_collection(
                name="omnirag",
                metadata={"hnsw:space": "cosine"}
            )
        except Exception as e:
            print(f"Warning: Failed to initialize ChromaDB: {e}")
            self.client = None
            self.collection = None

    @property
    def is_available(self) -> bool:
        return HAS_CHROMA and self.collection is not None

    def add_chunks(
        self,
        chunks: List[Dict[str, Any]],
        embeddings: List[List[float]]
    ) -> int:
        if not self.is_available:
            return 0
        ids = [str(uuid.uuid4()) for _ in chunks]
        texts = [c.get('text', '') for c in chunks]
        metadatas = [dict(c.get('metadata', {})) for c in chunks]
        for i, c in enumerate(chunks):
            if 'chunk_index' in c:
                metadatas[i]['chunk_index'] = c['chunk_index']
        valid = [(i, t, m, e) for i, (t, m, e) in
                 enumerate(zip(texts, metadatas, embeddings)) if t.strip()]
        if not valid:
            return 0
        f_ids = [ids[i] for i, _, _, _ in valid]
        f_texts = [t for _, t, _, _ in valid]
        f_metas = [m for _, _, m, _ in valid]
        f_embs = [e for _, _, _, e in valid]
        self.collection.add(
            ids=f_ids, documents=f_texts,
            metadatas=f_metas, embeddings=f_embs
        )
        return len(f_ids)

    def search(
        self,
        query_embedding: List[float],
        k: int = 5
    ) -> List[Dict[str, Any]]:
        if not self.is_available:
            return []
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=k,
            include=['documents', 'metadatas', 'distances']
        )
        if not results['ids'] or not results['ids'][0]:
            return []
        retrieved = []
        for i in range(len(results['ids'][0])):
            dist = results['distances'][0][i] if results.get('distances') else 0
            retrieved.append({
                'chunk_id': results['ids'][0][i],
                'text': results['documents'][0][i],
                'metadata': results['metadatas'][0][i],
                'score': 1.0 - dist
            })
        return retrieved

    def get_collection_stats(self) -> Dict[str, Any]:
        if not self.is_available:
            return {'count': 0, 'available': False}
        try:
            count = self.collection.count()
            return {'count': count, 'available': True}
        except Exception:
            return {'count': 0, 'available': False}


_vector_store: Optional[VectorStore] = None


def get_vector_store(persist_dir: str = "./chroma_db") -> VectorStore:
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStore(persist_dir)
    return _vector_store
