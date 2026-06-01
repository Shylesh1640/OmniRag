# OmniRAG Phase 2 - Multimodal RAG Implementation

## Overview

Phase 2 implements a complete multimodal Retrieval-Augmented Generation (RAG) pipeline supporting:
- **Text & PDF** extraction with page-level metadata
- **Images** with OCR (Optical Character Recognition)
- **Audio** transcription with timestamps
- **Video** frame extraction + audio transcription
- **Intelligent Chunking** with configurable overlap
- **Semantic Search** using embeddings
- **Relevance Grading** with confidence scores
- **LangGraph-based Orchestration** with routing and fallback logic
- **Source Citations** in responses with metadata

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (Next.js)                        │
│  (Chat Interface, File Upload, File Listing)                │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              FastAPI Backend (Phase 2)                       │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  POST /api/v1/upload → File Ingestion Pipeline              │
│  ├─ Route by file type (text/pdf/image/audio/video)         │
│  ├─ Extract content (text, OCR, transcription, frames)      │
│  ├─ Split into chunks with metadata                         │
│  ├─ Generate embeddings                                     │
│  └─ Store in vector database                                │
│                                                               │
│  POST /api/v1/chat → Query & Retrieval Pipeline             │
│  ├─ Embed user query                                        │
│  ├─ Retrieve top-k similar chunks                           │
│  ├─ Grade relevance (confidence scoring)                    │
│  ├─ Route to generation or fallback                         │
│  ├─ Generate response with citations                        │
│  └─ Return response + sources                               │
│                                                               │
│  GET /api/v1/files → List ingested files                    │
│  GET /api/v1/files/{file_id} → File metadata                │
│                                                               │
└─────────────────────────────────────────────────────────────┘
         │                           │
         ▼                           ▼
┌──────────────────┐        ┌──────────────────┐
│  Extractors      │        │  LangGraph       │
├──────────────────┤        │  Orchestration   │
│ • Text/PDF       │        │                  │
│ • Image (OCR)    │        │ Ingestion Graph: │
│ • Audio (Whisper)│        │ • Route by type  │
│ • Video (FFmpeg) │        │ • Extract        │
└──────────────────┘        │ • Chunk          │
         │                  │ • Embed & Index  │
         └──────────┬───────┘                  │
                    │                          │
                    ▼                          ▼
            ┌──────────────────────────────────────┐
            │     ChromaDB Vector Store            │
            │  (Persistent Embeddings + Metadata)  │
            └──────────────────────────────────────┘
                    ▲
                    │ (Query Retrieval)
            ┌──────────────────────────────────────┐
            │   Query Processing Graph             │
            │ • Query Rewrite                      │
            │ • Retrieve Context                   │
            │ • Grade Relevance                    │
            │ • Route (Generate/Fallback)          │
            │ • Generate Answer with Citations     │
            └──────────────────────────────────────┘
```

## Pipeline Details

### 1. Ingestion Pipeline (LangGraph)

**Entry Point:** Conditional routing based on file type

**Nodes:**
- **route_ingestion**: Determines file type → handler
- **text_ingest**: Extract text/PDF with `PyPDF2`
- **image_ingest**: Extract text via OCR with `pytesseract`
- **audio_ingest**: Transcribe with `faster-whisper`
- **video_ingest**: Extract audio + frames using `ffmpeg` and `cv2`
- **embed_and_index**: Chunk, embed, and store in ChromaDB

**Output:** 
- Chunks stored in vector database
- Metadata attached to each chunk (source, page, timestamp, etc.)

### 2. Query Pipeline (LangGraph)

**Entry Point:** User message

**Nodes:**
- **query_rewrite**: Normalize query
- **retrieve_context**: Semantic search using embeddings
- **grade_relevance**: Score chunks and decide confidence level
- **route_query**: Route to generation or fallback
- **fallback_search**: Generate fallback response
- **generate_answer**: Create response with citations
- **return_answer**: Return final response

**Output:**
- Response text
- List of citations with scores and sources
- Confidence level (high/medium/low)

### 3. Content Extraction

#### Text/PDF
- Extract text per page
- Metadata: source filename, page number, total pages
- Fallback for scanned PDFs: empty extraction with error note

#### Images
- OCR using Tesseract (via Pillow)
- Auto-generate caption from OCR preview
- Metadata: image size, mode, caption

#### Audio
- Transcribe using Whisper (faster-whisper)
- Segment-level timestamps
- Metadata: language, language probability, start/end times

#### Video
- Extract audio → transcribe with timestamps
- Extract key frames at intervals (default: every 30 seconds)
- OCR frames for visual text
- Combine transcript + frame text into searchable content
- Metadata: segment count, frame count, timestamps

### 4. Chunking Strategy

**Algorithm:** Sliding window word-based split
- **Chunk Size:** Configurable (default: 500 words)
- **Overlap:** Configurable (default: 50 words)
- **Metadata Preservation:** Each chunk carries source info + chunk index

**Example:**
```
Original text (1000 words)
├─ Chunk 0 (0-500 words) + metadata
├─ Chunk 1 (450-950 words) + metadata
└─ Chunk 2 (900-1000 words) + metadata
```

### 5. Embeddings

**Model:** `all-MiniLM-L6-v2` (384-dimensional vectors)
- Fast, lightweight, suitable for semantic search
- Alternatives available: `all-mpnet-base-v2` (better quality, slower)

**Storage:** ChromaDB with cosine similarity search

### 6. Retrieval & Relevance Grading

**Retrieval:**
1. Embed query with same model
2. Cosine similarity search (top-k, default: 5)
3. Score returned as distance → converted to similarity

**Relevance Grading:**
- Threshold-based (default: 0.3 / 1.0 scale)
- Confidence levels:
  - **High:** max_score >= 0.7
  - **Medium:** 0.4 <= max_score < 0.7
  - **Low:** max_score < 0.4 (triggers fallback)

**Fallback:** If no chunks exceed threshold, return clarification message

## Folder Structure

```
backend/
├── app/
│   ├── api/
│   │   ├── endpoints/
│   │   │   ├── chat.py          # Chat query endpoint
│   │   │   ├── upload.py        # File upload & ingestion
│   │   │   └── files.py         # List/retrieve file metadata
│   │   ├── deps.py              # Dependencies (unused in Phase 2)
│   │   └── routes.py            # API router
│   ├── core/
│   │   ├── config.py            # Settings & configuration
│   │   └── langgraph.py         # LangGraph workflows (ingestion + query)
│   ├── models/
│   │   ├── file.py              # File model
│   │   └── schemas.py           # Response schemas (ChatResponse, IngestionResult)
│   ├── services/
│   │   ├── chunker.py           # Text chunking logic
│   │   ├── embeddings.py        # Embedding generation (SentenceTransformers)
│   │   ├── retriever.py         # Query retrieval & relevance grading
│   │   ├── vectorstore.py       # ChromaDB wrapper
│   │   └── extractors/
│   │       ├── text_extractor.py      # Text/PDF extraction
│   │       ├── image_extractor.py     # Image OCR extraction
│   │       ├── audio_extractor.py     # Audio transcription (Whisper)
│   │       └── video_extractor.py     # Video extraction (audio + frames)
│   ├── utils/
│   │   └── storage.py           # File storage & metadata management
│   └── main.py                  # FastAPI app initialization
├── uploads/                     # Uploaded files directory
├── chroma_db/                   # Vector database (auto-created)
├── main.py                      # Entry point
├── requirements.txt             # Python dependencies
├── .env                         # Environment variables
├── .env.example                 # Environment template
└── README.md                    # Backend documentation

frontend/
├── app/
│   ├── layout.tsx               # Root layout
│   ├── page.tsx                 # Home page
│   ├── chat/
│   │   └── page.tsx             # Chat interface
│   ├── files/
│   │   └── page.tsx             # File listing
│   ├── upload/
│   │   └── page.tsx             # File upload
│   └── globals.css              # Global styles
├── components/
│   ├── ChatInterface.tsx        # Chat UI
│   ├── FileList.tsx             # File listing component
│   └── FileUploader.tsx         # File upload component
├── lib/
│   └── api.ts                   # API client
├── package.json                 # Node dependencies
├── tsconfig.json                # TypeScript config
├── tailwind.config.ts           # Tailwind CSS config
└── next.config.js               # Next.js config
```

## Installation & Setup

### Prerequisites

1. **Python 3.10+**
2. **Node.js 18+**
3. **System Tools:**
   ```bash
   # Ubuntu/Debian
   sudo apt-get install ffmpeg tesseract-ocr
   
   # macOS
   brew install ffmpeg tesseract
   
   # Windows
   # Download from: ffmpeg.org and github.com/UB-Mannheim/tesseract/wiki
   ```

### Backend Setup

1. **Create virtual environment:**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment:**
   ```bash
   # Copy and edit .env file
   cp .env.example .env
   # Edit .env with your settings
   ```

4. **Run backend:**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

   Backend will be available at: `http://localhost:8000`
   API docs: `http://localhost:8000/docs`

### Frontend Setup

1. **Install dependencies:**
   ```bash
   cd frontend
   npm install
   ```

2. **Run frontend:**
   ```bash
   npm run dev
   ```

   Frontend will be available at: `http://localhost:3000`

## API Reference

### Upload File (Ingestion)

**Endpoint:** `POST /api/v1/upload`

**Request:**
```bash
curl -X POST -F "file=@document.pdf" http://localhost:8000/api/v1/upload
```

**Response:**
```json
{
  "file_id": "document.pdf_1780028179",
  "filename": "document.pdf",
  "chunks_count": 42,
  "status": "success",
  "error": null
}
```

### Chat Query (Retrieval)

**Endpoint:** `POST /api/v1/chat`

**Request:**
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"message":"What is the main topic?"}' \
  http://localhost:8000/api/v1/chat
```

**Response:**
```json
{
  "response": "Based on the retrieved information, here's what I found:\n\n[Source 1: document.pdf, Page 5]\nThe main topic is...",
  "citations": [
    {
      "text": "The main topic is...",
      "source": "document.pdf",
      "page": 5,
      "timestamp": null,
      "score": 0.92,
      "chunk_index": 12
    }
  ],
  "confidence": "high"
}
```

### List Files

**Endpoint:** `GET /api/v1/files`

**Response:**
```json
[
  {
    "id": "document.pdf_1780028179",
    "filename": "document.pdf",
    "content_type": "application/pdf",
    "size": 1024000,
    "upload_time": "2024-06-01T10:30:00"
  }
]
```

### Get File Metadata

**Endpoint:** `GET /api/v1/files/{file_id}`

**Response:**
```json
{
  "id": "document.pdf_1780028179",
  "filename": "document.pdf",
  "content_type": "application/pdf",
  "size": 1024000,
  "upload_time": "2024-06-01T10:30:00"
}
```

## Configuration

### Key Settings in `.env`

| Setting | Default | Description |
|---------|---------|-------------|
| `CHUNK_SIZE` | 500 | Words per chunk |
| `CHUNK_OVERLAP` | 50 | Word overlap between chunks |
| `TOP_K_RETRIEVAL` | 5 | Number of chunks to retrieve |
| `MIN_RELEVANCE_SCORE` | 0.3 | Threshold for relevance (0-1) |
| `EMBEDDING_MODEL` | all-MiniLM-L6-v2 | SentenceTransformers model |
| `WHISPER_MODEL_SIZE` | base | tiny/base/small/medium/large |
| `VIDEO_FRAME_INTERVAL` | 30 | Seconds between extracted frames |
| `CHROMA_PERSIST_DIR` | ./chroma_db | Vector database location |

### Performance Tuning

**Faster Ingestion (lower quality):**
```
CHUNK_SIZE=1000
WHISPER_MODEL_SIZE=tiny
EMBEDDING_MODEL=all-MiniLM-L6-v2
```

**Better Quality (slower):**
```
CHUNK_SIZE=300
WHISPER_MODEL_SIZE=medium
EMBEDDING_MODEL=all-mpnet-base-v2
```

## Usage Examples

### Upload Different File Types

```bash
# PDF
curl -F "file=@report.pdf" http://localhost:8000/api/v1/upload

# Image
curl -F "file=@screenshot.png" http://localhost:8000/api/v1/upload

# Audio
curl -F "file=@interview.mp3" http://localhost:8000/api/v1/upload

# Video
curl -F "file=@presentation.mp4" http://localhost:8000/api/v1/upload

# Plain text
curl -F "file=@notes.txt" http://localhost:8000/api/v1/upload
```

### Query Examples

```bash
# Simple question
curl -X POST -H "Content-Type: application/json" \
  -d '{"message":"What is mentioned about X?"}' \
  http://localhost:8000/api/v1/chat

# Multi-turn context (future enhancement)
# Currently stateless, but state can be added to chat endpoint
```

## Supported File Types & Formats

| Type | Format | Extractor | Processing |
|------|--------|-----------|-----------|
| **Text** | .txt, .md | Native read | Direct text extraction |
| **PDF** | .pdf | PyPDF2 | Per-page text extraction |
| **Image** | .png, .jpg, .gif, .bmp | Tesseract OCR | Text extraction via OCR |
| **Audio** | .mp3, .wav, .m4a, .ogg | Whisper | Transcription + timestamps |
| **Video** | .mp4, .avi, .mov, .mkv | FFmpeg + Whisper + Tesseract | Audio transcription + frame OCR |

## Fallback Behavior

If retrieval returns no relevant chunks:

1. **Vector store empty:** "No documents in vector store"
2. **Query embedding fails:** "Embedding model not available"
3. **Low relevance scores:** "No relevant chunks found above threshold"
4. **Generic fallback:** User is prompted to upload more relevant documents or rephrase

## Limitations & Future Work

### Current Limitations
- No persistent chat history (stateless)
- No multi-turn context awareness
- Fallback is simple template (no LLM generation yet)
- No duplicate detection across chunks
- No real-time progress updates for ingestion
- Video frame extraction at fixed intervals (not content-aware)

### Phase 3 Will Add
- **Real LLM Integration** (OpenAI/LLama/Ollama)
- **Multi-turn Conversations** with chat memory
- **Advanced Routing** based on query complexity
- **Query Expansion** for better retrieval
- **Re-ranking** of retrieved chunks
- **Knowledge Graph** integration
- **User Authentication** & multi-tenant support
- **File-level Access Control**
- **Real-time Ingestion Progress**
- **Content-aware Video Frame Sampling**
- **Duplicate Detection** (MinHash/LSH)
- **Performance Monitoring** (latency, throughput)

## Troubleshooting

### Common Issues

**ChromaDB connection errors:**
```
Solution: Delete `./chroma_db` directory and restart
rm -rf backend/chroma_db
```

**Tesseract not found:**
```
# Ubuntu/Debian
sudo apt-get install tesseract-ocr

# Set environment variable if needed
export PYTESSERACT_PATH=/usr/bin/tesseract
```

**FFmpeg not found:**
```
# Install ffmpeg
# Ubuntu: sudo apt-get install ffmpeg
# macOS: brew install ffmpeg
# Windows: Download from ffmpeg.org
```

**Out of memory during large file processing:**
```
Reduce CHUNK_SIZE or WHISPER_MODEL_SIZE
Use smaller embedding model
Process files sequentially
```

**Slow embeddings:**
```
Switch to all-MiniLM-L6-v2 (faster)
Reduce CHUNK_SIZE
Enable GPU (configure PyTorch)
```

## Performance Benchmarks

**Approximate processing times (CPU, ~2GB available RAM):**

| Content | Size | Processing Time |
|---------|------|-----------------|
| Plain text page | 5 KB | < 1s |
| PDF (10 pages) | 500 KB | 5-10s |
| Image (OCR) | 2 MB | 3-5s |
| Audio (1 min) | 2 MB | 10-15s |
| Video (1 min) | 50 MB | 60-90s |

**Storage:**
- Each chunk embedding: ~1.5 KB (384-dimensional vector)
- Example: 1000 chunks ≈ 1.5 MB in ChromaDB

## Architecture Decisions

1. **ChromaDB:** Lightweight, persistent, no external DB needed
2. **SentenceTransformers:** Small models, excellent semantic search, open-source
3. **Whisper:** Free, multilingual, handles various audio quality levels
4. **Tesseract:** Mature OCR, good for document images
5. **LangGraph:** Clear node-based orchestration, easy to extend
6. **FastAPI:** Fast, async, automatic docs
7. **Next.js:** Modern frontend, SSR capability, excellent DX

## API Response Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 400 | Bad request (invalid input) |
| 413 | File too large |
| 404 | Resource not found |
| 500 | Server error |

## Development Tips

1. **Enable debug logging:**
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

2. **Test extractors independently:**
   ```python
   from app.services.extractors.text_extractor import extract_text
   result = extract_text("path/to/file.pdf")
   ```

3. **Check vector store stats:**
   ```python
   from app.services.vectorstore import get_vector_store
   store = get_vector_store()
   stats = store.get_collection_stats()
   print(f"Stored chunks: {stats['count']}")
   ```

4. **Monitor ChromaDB:**
   ChromaDB stores data in `./chroma_db/` - inspect with file browser

## Security Considerations

- ⚠️ **Phase 2 lacks authentication** - add before production
- ⚠️ **No file size limits enforced** - configure MAX_UPLOAD_SIZE
- ⚠️ **No input validation** - add rate limiting & sanitization
- ⚠️ **No audit logging** - track all uploads/queries in Phase 3

## Next Steps

1. Test all extractors with various file types
2. Configure embeddings model for your use case
3. Tune chunking parameters for better retrieval
4. Set up monitoring & logging
5. Plan Phase 3: LLM integration and multi-turn chat

