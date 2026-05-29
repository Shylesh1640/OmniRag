from fastapi import APIRouter
from pydantic import BaseModel
from app.core.langgraph import query_graph
from app.models.schemas import ChatResponse

router = APIRouter()

class ChatMessage(BaseModel):
    message: str


@router.post("", response_model=ChatResponse)
async def chat(chat_message: ChatMessage):
    initial_state = {
        'message': chat_message.message,
        'chat_history': [],
        'rewritten_query': '',
        'retrieved_chunks': [],
        'needs_fallback': False,
        'fallback_reason': None,
        'fallback_response': None,
        'response': '',
        'citations': [],
        'confidence': 'high',
        'file_path': None,
        'file_name': None,
        'file_id': None,
        'file_type': None,
        'extracted_data': [],
        'chunks': [],
        'ingestion_status': None,
        'ingestion_error': None,
        'chunks_count': 0,
    }
    result = query_graph.invoke(initial_state)
    return ChatResponse(
        response=result.get('response', ''),
        citations=result.get('citations', []),
        confidence=result.get('confidence', 'low'),
    )