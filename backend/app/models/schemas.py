from pydantic import BaseModel
from typing import Dict, Any, List, Optional


class Citation(BaseModel):
    text: str
    source: str
    page: Optional[int] = None
    timestamp: Optional[float] = None
    score: float
    chunk_index: Optional[int] = None


class ChatResponse(BaseModel):
    response: str
    citations: List[Citation] = []
    confidence: str = "high"


class IngestionResult(BaseModel):
    file_id: str
    filename: str
    chunks_count: int
    status: str
    error: Optional[str] = None
