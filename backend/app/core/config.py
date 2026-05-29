import os
from typing import List
try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings

class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "OmniRAG"
    
    # Server Settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # CORS Settings
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    
    # File Storage Settings
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    # LangGraph Settings
    LANGGRAPH_THREAD_ID: str = "default"
    
    # Phase 2: RAG Pipeline Settings
    CHROMA_PERSIST_DIR: str = "./chroma_db"
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    WHISPER_MODEL_SIZE: str = "base"
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50
    TOP_K_RETRIEVAL: int = 5
    MIN_RELEVANCE_SCORE: float = 0.3
    VIDEO_FRAME_INTERVAL: int = 30
    
    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()