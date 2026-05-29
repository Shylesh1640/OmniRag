from typing import Dict, Any, List, Optional, TypedDict
from langgraph.graph import StateGraph, END

from app.core.config import settings
from app.services.extractors.text_extractor import extract_text
from app.services.extractors.image_extractor import extract_image
from app.services.extractors.audio_extractor import extract_audio
from app.services.extractors.video_extractor import extract_video
from app.services.chunker import chunk_document
from app.services.embeddings import embed_text
from app.services.vectorstore import get_vector_store
from app.services.retriever import retrieve_context


# ─── State ───────────────────────────────────────────────────────

class AgentState(TypedDict):
    message: str
    chat_history: List[Dict[str, str]]
    rewritten_query: str
    retrieved_chunks: List[Dict[str, Any]]
    needs_fallback: bool
    fallback_reason: Optional[str]
    fallback_response: Optional[str]
    response: str
    citations: List[Dict[str, Any]]
    confidence: str
    file_path: Optional[str]
    file_name: Optional[str]
    file_id: Optional[str]
    file_type: Optional[str]
    extracted_data: List[Dict[str, Any]]
    chunks: List[Dict[str, Any]]
    ingestion_status: Optional[str]
    ingestion_error: Optional[str]
    chunks_count: int


# ─── Query Flow ──────────────────────────────────────────────────

def query_rewrite(state: AgentState) -> AgentState:
    state['rewritten_query'] = state.get('message', '').strip()
    return state


def retrieve_context_node(state: AgentState) -> AgentState:
    query = state.get('rewritten_query', '')
    if not query:
        state['retrieved_chunks'] = []
        state['needs_fallback'] = True
        state['fallback_reason'] = 'Empty query'
        return state
    result = retrieve_context(
        query=query,
        top_k=settings.TOP_K_RETRIEVAL,
        min_score=settings.MIN_RELEVANCE_SCORE
    )
    state['retrieved_chunks'] = result.get('chunks', [])
    state['needs_fallback'] = result.get('needs_fallback', True)
    state['fallback_reason'] = result.get('reason')
    return state


def grade_relevance(state: AgentState) -> AgentState:
    chunks = state.get('retrieved_chunks', [])
    if not chunks:
        state['needs_fallback'] = True
        state['fallback_reason'] = state.get('fallback_reason') or 'No retrieved chunks'
        return state
    scores = [c['score'] for c in chunks]
    max_score = max(scores)
    if max_score >= 0.7:
        state['confidence'] = 'high'
        state['needs_fallback'] = False
    elif max_score >= 0.4:
        state['confidence'] = 'medium'
        state['needs_fallback'] = False
    else:
        state['confidence'] = 'low'
        state['needs_fallback'] = True
        state['fallback_reason'] = 'All retrieved chunks have low relevance scores'
    return state


def route_query(state: AgentState) -> str:
    if state.get('needs_fallback', False):
        return 'fallback'
    return 'generate'


def fallback_search(state: AgentState) -> AgentState:
    reason = state.get('fallback_reason', 'No relevant results found')
    query = state.get('rewritten_query', '')
    state['fallback_response'] = (
        f"I couldn't find strongly relevant information from the ingested documents "
        f"to answer your question. {reason}. "
        f"You may want to upload more relevant documents, or try rephrasing your query."
    )
    state['confidence'] = 'low'
    return state


def generate_answer(state: AgentState) -> AgentState:
    if state.get('needs_fallback', False) and state.get('fallback_response'):
        state['response'] = state['fallback_response']
        state['citations'] = []
        return state
    chunks = state.get('retrieved_chunks', [])
    query = state.get('rewritten_query', '')
    if not chunks:
        state['response'] = "I don't have enough information to answer that question."
        state['citations'] = []
        state['confidence'] = 'low'
        return state
    context_parts = []
    citations = []
    for i, chunk in enumerate(chunks):
        text = chunk.get('text', '')
        meta = chunk.get('metadata', {})
        source = meta.get('source', 'Unknown')
        page = meta.get('page')
        timestamp = meta.get('timestamp') or meta.get('start')
        score = chunk.get('score', 0)
        ci = meta.get('chunk_index')
        context_parts.append(
            f"[Source {i+1}: {source}"
            + (f", Page {page}" if page else "")
            + (f", Time {timestamp:.1f}s" if timestamp else "")
            + f"]\n{text}"
        )
        citations.append({
            'text': text[:200] + ('...' if len(text) > 200 else ''),
            'source': source,
            'page': page,
            'timestamp': timestamp,
            'score': score,
            'chunk_index': ci
        })
    state['response'] = "Based on the retrieved information, here's what I found:\n\n" + '\n\n'.join(context_parts)
    state['citations'] = citations
    return state


def return_answer(state: AgentState) -> AgentState:
    return state


# ─── Ingestion Flow ──────────────────────────────────────────────

def route_ingestion(state: AgentState) -> str:
    ft = state.get('file_type', '').lower()
    if 'pdf' in ft or 'text' in ft or 'plain' in ft:
        return 'text_ingest'
    if 'image' in ft:
        return 'image_ingest'
    if 'audio' in ft:
        return 'audio_ingest'
    if 'video' in ft:
        return 'video_ingest'
    return 'text_ingest'


def text_ingest(state: AgentState) -> AgentState:
    try:
        state['extracted_data'] = extract_text(state['file_path'])
        state['ingestion_status'] = 'success'
    except Exception as e:
        state['extracted_data'] = []
        state['ingestion_status'] = 'failed'
        state['ingestion_error'] = str(e)
    return state


def image_ingest(state: AgentState) -> AgentState:
    try:
        state['extracted_data'] = extract_image(state['file_path'])
        state['ingestion_status'] = 'success'
    except Exception as e:
        state['extracted_data'] = []
        state['ingestion_status'] = 'failed'
        state['ingestion_error'] = str(e)
    return state


def audio_ingest(state: AgentState) -> AgentState:
    try:
        state['extracted_data'] = extract_audio(
            state['file_path'], settings.WHISPER_MODEL_SIZE
        )
        state['ingestion_status'] = 'success'
    except Exception as e:
        state['extracted_data'] = []
        state['ingestion_status'] = 'failed'
        state['ingestion_error'] = str(e)
    return state


def video_ingest(state: AgentState) -> AgentState:
    try:
        state['extracted_data'] = extract_video(
            state['file_path'],
            frame_interval=settings.VIDEO_FRAME_INTERVAL,
            whisper_model_size=settings.WHISPER_MODEL_SIZE
        )
        state['ingestion_status'] = 'success'
    except Exception as e:
        state['extracted_data'] = []
        state['ingestion_status'] = 'failed'
        state['ingestion_error'] = str(e)
    return state


def embed_and_index(state: AgentState) -> AgentState:
    data = state.get('extracted_data', [])
    if not data:
        state['chunks'] = []
        state['chunks_count'] = 0
        return state
    chunks = chunk_document(
        data,
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP
    )
    state['chunks'] = chunks
    valid = [c for c in chunks if c['text'].strip()]
    if not valid:
        state['chunks_count'] = 0
        return state
    embeddings = embed_text(
        [c['text'] for c in valid],
        settings.EMBEDDING_MODEL
    )
    if embeddings is None:
        state['chunks_count'] = len(valid)
        state['ingestion_status'] = 'partial'
        state['ingestion_error'] = 'Embedding model unavailable'
        return state
    store = get_vector_store(settings.CHROMA_PERSIST_DIR)
    indexed = store.add_chunks(valid, embeddings)
    state['chunks_count'] = indexed
    state['ingestion_status'] = 'success' if indexed > 0 else 'failed'
    if indexed == 0:
        state['ingestion_error'] = 'Vector store indexing failed'
    return state


# ─── Graph Builders ──────────────────────────────────────────────

def create_query_graph():
    workflow = StateGraph(AgentState)
    for name, fn in [
        ('query_rewrite', query_rewrite),
        ('retrieve_context', retrieve_context_node),
        ('grade_relevance', grade_relevance),
        ('fallback_search', fallback_search),
        ('generate_answer', generate_answer),
        ('return_answer', return_answer),
    ]:
        workflow.add_node(name, fn)
    workflow.set_entry_point('query_rewrite')
    workflow.add_edge('query_rewrite', 'retrieve_context')
    workflow.add_edge('retrieve_context', 'grade_relevance')
    workflow.add_conditional_edges(
        'grade_relevance', route_query,
        {'fallback': 'fallback_search', 'generate': 'generate_answer'}
    )
    workflow.add_edge('fallback_search', 'generate_answer')
    workflow.add_edge('generate_answer', 'return_answer')
    workflow.add_edge('return_answer', END)
    return workflow.compile()


def create_ingestion_graph():
    workflow = StateGraph(AgentState)
    workflow.add_node('text_ingest', text_ingest)
    workflow.add_node('image_ingest', image_ingest)
    workflow.add_node('audio_ingest', audio_ingest)
    workflow.add_node('video_ingest', video_ingest)
    workflow.add_node('embed_and_index', embed_and_index)
    workflow.set_conditional_entry_point(
        route_ingestion,
        {
            'text_ingest': 'text_ingest',
            'image_ingest': 'image_ingest',
            'audio_ingest': 'audio_ingest',
            'video_ingest': 'video_ingest',
        }
    )
    for n in ['text_ingest', 'image_ingest', 'audio_ingest', 'video_ingest']:
        workflow.add_edge(n, 'embed_and_index')
    workflow.add_edge('embed_and_index', END)
    return workflow.compile()


query_graph = create_query_graph()
ingestion_graph = create_ingestion_graph()