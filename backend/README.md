# OmniRAG Backend - Phase 2

FastAPI-based multimodal RAG (Retrieval-Augmented Generation) system with support for Text, PDF, Image, Audio, and Video content.

## Quick Start

### 1. Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install system dependencies
# Ubuntu/Debian: sudo apt-get install ffmpeg tesseract-ocr
# macOS: brew install ffmpeg tesseract
```

### 2. Configure

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your settings (optional)
nano .env
```

### 3. Run

```bash
# Start backend server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Visit API docs at: http://localhost:8000/docs
```

## Project Structure

```
backend/
├── app/
│   ├── api/endpoints/           # API route handlers
│   │   ├── chat.py             # Chat endpoint
│   │   ├── upload.py           # File upload endpoint
│   │   └── files.py            # File listing endpoint
│   ├── core/
│   │   ├── config.py           # Configuration & settings
│   │   └── langgraph.py        # LangGraph workflows
│   ├── models/
│   │   ├── file.py             # File model
│   │   └── schemas.py          # Response schemas
│   ├── services/
│   │   ├── chunker.py          # Text chunking
│   │   ├── embeddings.py       # Embedding generation
│   │   ├── retriever.py        # Query retrieval
│   │   ├── vectorstore.py      # ChromaDB wrapper
│   │   └── extractors/         # Content extraction
│   ├── utils/
│   │   └── storage.py          # File storage management
│   └── main.py                 # FastAPI app
├── uploads/                    # Uploaded files
├── chroma_db/                  # Vector database (auto-created)
└── requirements.txt            # Python dependencies
```

## Core Concepts

### LangGraph Workflows

**Ingestion Pipeline:**
```
File Upload → Route by Type → Extract Content → Chunk → Embed → Index
```

**Query Pipeline:**
```
User Query → Rewrite → Retrieve → Grade → Route → Generate → Return
```

### Supported Content Types

| Type | Format | Processing |
|------|--------|-----------|
| **Text** | .txt, .md | Direct extraction |
| **PDF** | .pdf | Per-page extraction |
| **Image** | .png, .jpg, .gif | OCR extraction |
| **Audio** | .mp3, .wav, .m4a | Whisper transcription |
| **Video** | .mp4, .avi, .mov | Audio transcription + frame OCR |

## API Endpoints

### Chat Query
```bash
POST /api/v1/chat
Content-Type: application/json

{
  "message": "What is the main topic?"
}
```

Response includes: answer, citations, confidence level

### Upload File
```bash
POST /api/v1/upload
Content-Type: multipart/form-data

file: <binary data>
```

### List Files
```bash
GET /api/v1/files
```

### Get File Info
```bash
GET /api/v1/files/{file_id}
```

## Configuration

Key settings in `.env`:

```
CHUNK_SIZE=500              # Words per chunk
CHUNK_OVERLAP=50            # Overlap between chunks
TOP_K_RETRIEVAL=5           # Chunks to retrieve
MIN_RELEVANCE_SCORE=0.3     # Relevance threshold
EMBEDDING_MODEL=all-MiniLM-L6-v2  # Embedding model
WHISPER_MODEL_SIZE=base     # Transcription model
```

## Key Features

✅ **Multimodal Extraction**
- Text/PDF with PyPDF2
- Images with Tesseract OCR
- Audio with Whisper
- Video with FFmpeg + OCR + Transcription

✅ **Smart Chunking**
- Configurable chunk size & overlap
- Metadata preservation
- Sliding window strategy

✅ **Semantic Search**
- SentenceTransformers embeddings
- ChromaDB vector storage
- Cosine similarity search

✅ **Relevance Grading**
- Confidence-based routing
- Fallback handling
- Source citations

✅ **Orchestration**
- LangGraph-based workflows
- Conditional routing
- Error handling

## Development

### Run Tests
```bash
# (Test suite to be added)
pytest tests/
```

### Debug Extractors
```python
from app.services.extractors.text_extractor import extract_text
result = extract_text("path/to/file.pdf")
print(result)
```

### Check Vector Store
```python
from app.services.vectorstore import get_vector_store
store = get_vector_store()
stats = store.get_collection_stats()
print(f"Chunks stored: {stats['count']}")
```

## Performance

**Typical processing times (CPU):**
- Text page: < 1s
- PDF (10 pages): 5-10s
- Image: 3-5s
- Audio (1 min): 10-15s
- Video (1 min): 60-90s

## Troubleshooting

| Issue | Solution |
|-------|----------|
| ChromaDB errors | `rm -rf chroma_db` then restart |
| Tesseract not found | Install: `sudo apt-get install tesseract-ocr` |
| FFmpeg not found | Install: `brew install ffmpeg` (macOS) or from ffmpeg.org |
| Out of memory | Reduce CHUNK_SIZE or use smaller model |
| Slow embeddings | Use all-MiniLM-L6-v2 (faster) |

## Next Steps

- See [PHASE2.md](../PHASE2.md) for detailed architecture
- Phase 3 will add LLM integration for better answer generation
- Phase 3 will add multi-turn conversation support

## Contributing

Code structure follows clean architecture:
- Services are modular and testable
- LangGraph nodes are pure functions
- Extractors are independent
- No mixed concerns

