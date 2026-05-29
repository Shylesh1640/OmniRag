import os
from fastapi import APIRouter, File, UploadFile, HTTPException
from app.utils.storage import save_file
from app.models.schemas import IngestionResult
from app.core.config import settings
from app.core.langgraph import ingestion_graph

router = APIRouter()


@router.post("", response_model=IngestionResult)
async def upload_file(file: UploadFile = File(...)):
    contents = await file.read()
    if len(contents) > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=413, detail="File too large")
    db_file = save_file(
        file_content=contents,
        filename=file.filename,
        content_type=file.content_type
    )
    file_path = os.path.join(settings.UPLOAD_DIR, db_file.id)
    initial_state = {
        'message': '',
        'chat_history': [],
        'rewritten_query': '',
        'retrieved_chunks': [],
        'needs_fallback': False,
        'fallback_reason': None,
        'fallback_response': None,
        'response': '',
        'citations': [],
        'confidence': '',
        'file_path': file_path,
        'file_name': file.filename,
        'file_id': db_file.id,
        'file_type': file.content_type or '',
        'extracted_data': [],
        'chunks': [],
        'ingestion_status': None,
        'ingestion_error': None,
        'chunks_count': 0,
    }
    result = ingestion_graph.invoke(initial_state)
    return IngestionResult(
        file_id=db_file.id,
        filename=file.filename,
        chunks_count=result.get('chunks_count', 0),
        status=result.get('ingestion_status', 'failed'),
        error=result.get('ingestion_error'),
    )