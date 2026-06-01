# OmniRAG Phase 2 - Project Structure & Components

## Overview

This document provides a detailed breakdown of the OmniRAG Phase 2 implementation, including all files, their purposes, and how they work together.

## Backend File Structure & Descriptions

### Core Application Files

#### `app/main.py`
**Purpose:** FastAPI application initialization and configuration

**Key Components:**
- FastAPI app initialization
- CORS middleware setup
- Route registration
- Health check endpoint

**Responsibilities:**
- Bootstrap the application
- Configure cross-origin requests
- Mount API routes

---

#### `app/core/config.py`
**Purpose:** Centralized configuration management

**Key Settings:**
- API configuration (version, title, host, port)
- CORS origins
- File upload settings
- RAG pipeline parameters
- Vector database settings
- Model configurations

**Used By:** All services and endpoints

---

#### `app/core/langgraph.py`
**Purpose:** Define complete LangGraph workflows for ingestion and querying

**Components:**

1. **AgentState TypedDict**
   - Defines state schema for both workflows
   - Contains message, query, retrieved chunks, response, etc.

2. **Query Pipeline** (Retrieval & Generation)
   - Nodes: query_rewrite → retrieve_context → grade_relevance → route_query → (fallback_search | generate_answer) → return_answer
   - Purpose: Answer user queries with cited sources

3. **Ingestion Pipeline** (File Processing)
   - Nodes: route_ingestion → (text/image/audio/video_ingest) → embed_and_index
   - Purpose: Process uploaded files and index content

**Workflows:**
- `query_graph`: Handles user queries
- `ingestion_graph`: Handles file uploads and indexing

---

### API Endpoints

#### `app/api/routes.py`
**Purpose:** API router configuration

**Routes:**
- `/api/v1/upload` - File upload
- `/api/v1/files` - File listing
- `/api/v1/chat` - Chat queries

---

#### `app/api/endpoints/upload.py`
**Purpose:** File upload and ingestion endpoint

**Workflow:**
1. Receive file upload
2. Validate size
3. Save file to disk
4. Create file metadata
5. Invoke ingestion_graph
6. Return ingestion result

**Response:** `IngestionResult` with file_id, chunks_count, status

---

#### `app/api/endpoints/chat.py`
**Purpose:** Chat query endpoint

**Workflow:**
1. Receive user message
2. Initialize query state
3. Invoke query_graph
4. Return response with citations

**Response:** `ChatResponse` with response text, citations, confidence

---

#### `app/api/endpoints/files.py`
**Purpose:** File listing and metadata retrieval

**Endpoints:**
- `GET /files/` - List all uploaded files
- `GET /files/{file_id}` - Get specific file metadata

---

### Models & Schemas

#### `app/models/file.py`
**Purpose:** File data models

**Models:**
- `FileBase`: Base file attributes
- `FileCreate`: File creation request
- `File`: Complete file object with metadata

---

#### `app/models/schemas.py`
**Purpose:** API request/response schemas

**Schemas:**
- `Citation`: Source reference with metadata
- `ChatResponse`: Chat endpoint response
- `IngestionResult`: Upload endpoint response

---

### Services & Business Logic

#### `app/services/chunker.py`
**Purpose:** Split extracted content into semantic chunks

**Algorithm:** Sliding window word-based chunking

**Functions:**
- `chunk_document(data, chunk_size, chunk_overlap)` - Main chunking function
- `_split_text(text, chunk_size, chunk_overlap)` - Word-based text splitting

**Features:**
- Configurable chunk size and overlap
- Metadata preservation for each chunk
- Support for multiple input documents

---

#### `app/services/embeddings.py`
**Purpose:** Generate semantic embeddings for text

**Model:** `sentence-transformers/all-MiniLM-L6-v2` (384 dimensions)

**Functions:**
- `embed_text(texts, model_name)` - Generate embeddings for multiple texts
- `embed_query(query, model_name)` - Generate embedding for single query
- `_get_model(model_name)` - Lazy-load embedding model

**Features:**
- Model caching (singleton pattern)
- Batch processing support
- Fallback for missing dependencies

---

#### `app/services/vectorstore.py`
**Purpose:** Vector storage and semantic search

**Technology:** ChromaDB (persistent, local)

**VectorStore Class:**
- `__init__(persist_dir)` - Initialize with persistence path
- `add_chunks(chunks, embeddings)` - Store chunks with embeddings
- `search(query_embedding, k)` - Semantic search with top-k results
- `get_collection_stats()` - Get database statistics
- `is_available` - Check if database is operational

**Features:**
- Persistent storage (survives restarts)
- Cosine similarity search
- Metadata attachment to embeddings
- Error handling and recovery

---

#### `app/services/retriever.py`
**Purpose:** Query retrieval and relevance grading

**Functions:**
- `retrieve_context(query, top_k, min_score)` - Main retrieval function
- `_grade_relevance(chunks, min_score)` - Filter and score chunks

**Features:**
- Semantic search via embeddings
- Relevance threshold filtering
- Fallback indication
- Detailed relevance scoring

---

### Content Extractors

#### `app/services/extractors/text_extractor.py`
**Purpose:** Extract text from plain text and PDF files

**Functions:**
- `extract_text(file_path)` - Route to appropriate extractor
- `extract_plain_text(file_path)` - Extract plain text/markdown
- `extract_pdf(file_path)` - Extract text from PDF pages

**Features:**
- Per-page extraction for PDFs
- Page number tracking in metadata
- UTF-8 encoding with error handling
- Empty file detection

**Output Format:**
```python
[{
    'text': 'extracted text content',
    'metadata': {
        'source': 'filename',
        'page': 1,
        'total_pages': 10,
        'type': 'pdf'
    }
}]
```

---

#### `app/services/extractors/image_extractor.py`
**Purpose:** Extract text from images via OCR

**Dependencies:** Tesseract OCR, PIL/Pillow

**Functions:**
- `extract_image(file_path)` - Main image extraction
- `_generate_caption(ocr_text, filename)` - Auto-generate image caption

**Features:**
- OCR with Tesseract
- Caption generation from OCR preview
- Image dimensions and color mode tracking
- Graceful fallback for missing OCR library

**Output Format:**
```python
[{
    'text': 'ocr extracted text',
    'metadata': {
        'source': 'image.png',
        'type': 'image',
        'caption': 'Image containing text: ...',
        'image_size': '1920x1080',
        'image_mode': 'RGB'
    }
}]
```

---

#### `app/services/extractors/audio_extractor.py`
**Purpose:** Transcribe audio to text

**Dependencies:** faster-whisper (OpenAI Whisper)

**Functions:**
- `extract_audio(file_path, model_size)` - Main transcription function
- `_get_whisper_model(model_size)` - Lazy-load Whisper model

**Features:**
- Speech-to-text transcription
- Multilingual support with language detection
- Segment-level timestamps
- Confidence scores and language probability
- Model size options: tiny, base, small, medium, large

**Output Format:**
```python
[{
    'text': 'transcribed segment text',
    'metadata': {
        'source': 'audio.mp3',
        'type': 'audio',
        'start': 0.0,
        'end': 5.3,
        'language': 'en',
        'language_probability': 0.98
    }
}]
```

---

#### `app/services/extractors/video_extractor.py`
**Purpose:** Extract audio and frames from video files

**Dependencies:** FFmpeg, OpenCV, Whisper, Tesseract

**Main Function:** `extract_video(file_path, frame_interval, whisper_model_size)`

**Sub-functions:**
- `_extract_video_audio()` - Audio extraction and transcription
- `_extract_video_frames()` - Key frame extraction and OCR
- `_ocr_frame()` - Apply OCR to video frame
- `_combine_video_results()` - Merge audio and frame results

**Features:**
- Audio extraction at 16kHz mono
- Frame extraction at configurable intervals
- Timestamp preservation
- Fallback if no extractors available

**Output Format:**
```python
[
    {  # Combined transcript
        'text': 'full transcript text',
        'metadata': {
            'source': 'video.mp4',
            'type': 'video_combined',
            'segments_count': 10,
            'frame_count': 5
        }
    },
    {  # Frame OCR
        'text': 'text from frame',
        'metadata': {
            'source': 'video.mp4',
            'type': 'video_frame',
            'timestamp': 30.5,
            'frame_number': 752,
            'duration': 300.0
        }
    }
]
```

---

### Utilities

#### `app/utils/storage.py`
**Purpose:** File storage and metadata management

**Functions:**
- `save_file(file_content, filename, content_type)` - Save uploaded file
- `get_files()` - List all uploaded files
- `get_file(file_id)` - Get specific file metadata
- `delete_file(file_id)` - Delete file and metadata
- `_load_metadata()` - Load metadata from disk
- `_save_metadata(metadata)` - Save metadata to disk

**Storage:**
- Files stored in `uploads/` directory
- Metadata stored in `uploads/metadata.json`
- File ID generation from filename and timestamp

---

## Data Flow Diagrams

### Ingestion Flow

```
User Uploads File
        │
        ▼
POST /api/v1/upload
        │
        ▼
Save File → route_ingestion()
        │
        ├─ Text/PDF → text_ingest() → extract_text()
        │
        ├─ Image → image_ingest() → extract_image()
        │
        ├─ Audio → audio_ingest() → extract_audio()
        │
        └─ Video → video_ingest() → extract_video()
              │ (extracts audio)
              └─ extract_audio()
                      │
                      └─ Also extracts frames + OCR
        │
        ▼
List of extracted data with metadata
        │
        ▼
chunk_document() - Split into chunks
        │
        ▼
embed_text() - Generate embeddings
        │
        ▼
vectorstore.add_chunks() - Store in ChromaDB
        │
        ▼
Return IngestionResult
```

### Query Flow

```
User Sends Message
        │
        ▼
POST /api/v1/chat
        │
        ▼
query_rewrite() - Normalize query
        │
        ▼
embed_query() - Generate embedding
        │
        ▼
vectorstore.search() - Find similar chunks
        │
        ▼
_grade_relevance() - Score chunks
        │
        ▼
route_query() - Check confidence
        │
        ├─ Confidence too low → fallback_search()
        │                           │
        │                           ▼
        │                       Return clarification
        │                           │
        └───────────────┬───────────┘
                        │
                        ▼
                generate_answer() - Create response
                        │
                        ▼
                return_answer() - Return final response
```

## Configuration Hierarchy

```
Environment Variables (.env)
        ↓
app/core/config.py (Settings class)
        ↓
Used by:
├─ app/core/langgraph.py (Workflow parameters)
├─ app/services/vectorstore.py (DB path)
├─ app/services/embeddings.py (Model name)
├─ app/services/retrievers.py (Top-k, min_score)
└─ app/api/endpoints/upload.py (Max file size)
```

## External Dependencies & Models

### Runtime Models (Downloaded on First Use)

| Model | Purpose | Size | Source |
|-------|---------|------|--------|
| `all-MiniLM-L6-v2` | Text embeddings | ~24 MB | HuggingFace |
| `base` Whisper | Audio transcription | ~140 MB | OpenAI |
| Tesseract | OCR | ~50 MB | Google |

### System Dependencies

| Tool | Purpose | Alternative |
|------|---------|-------------|
| FFmpeg | Video/audio processing | libav |
| Tesseract | OCR | EasyOCR, Paddleocr |

## Error Handling Strategy

### By Component

**Extractors:** Return empty text with error metadata
```python
{
    'text': '',
    'metadata': {
        'source': 'filename',
        'type': 'pdf',
        'error': 'error message'
    }
}
```

**Embeddings:** Return None for unavailable models
```python
embeddings = embed_text(texts)  # Returns None if model unavailable
```

**Retrieval:** Return empty chunks with fallback indicator
```python
return {
    'chunks': [],
    'needs_fallback': True,
    'reason': 'specific reason'
}
```

**LangGraph:** State carries ingestion_error and ingestion_status
```python
state['ingestion_error'] = 'error message'
state['ingestion_status'] = 'failed' | 'partial' | 'success'
```

## Performance Optimizations

1. **Lazy Loading:** Models loaded only when needed
2. **Singleton Patterns:** Embedding model and vector store cached globally
3. **Batch Processing:** Embeddings generated in batches
4. **Early Termination:** Graph routes to fallback early if no relevant results
5. **Metadata Indexing:** ChromaDB automatically indexes metadata

## Security Considerations

⚠️ **Phase 2 Limitations (to address in Phase 3):**

- No authentication or authorization
- No input validation on file content
- No rate limiting
- File size checks are minimal
- No audit logging
- No encryption of stored data
- No access control per file

## Testing & Validation

### Provided Scripts

1. **`validate.py`** - Check all dependencies and configurations
2. **`test_phase2.py`** - Test core Phase 2 functionality

### How to Run

```bash
# Validate environment
python validate.py

# Test components
python test_phase2.py
```

## Future Enhancements (Phase 3+)

### Planned Improvements

1. **LLM Integration**
   - Replace template-based responses with actual generation
   - Support multiple LLM backends (OpenAI, Llama, Ollama)

2. **Multi-turn Chat**
   - Conversation history and context
   - Query expansion based on history

3. **Advanced Retrieval**
   - Query expansion
   - Hybrid search (semantic + keyword)
   - Re-ranking of results

4. **Knowledge Management**
   - Deduplication detection
   - Similarity clustering
   - Knowledge graph integration

5. **User Features**
   - Authentication and multi-tenancy
   - File-level access control
   - User analytics

6. **Performance**
   - Real-time progress updates
   - Asynchronous batch processing
   - Caching layer

## Deployment Considerations

### Docker

```dockerfile
FROM python:3.10
RUN apt-get install ffmpeg tesseract-ocr
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0"]
```

### Environment Variables (Production)

```
BACKEND_CORS_ORIGINS=["https://yourdomain.com"]
CHROMA_PERSIST_DIR=/data/chroma_db
MAX_UPLOAD_SIZE=52428800  # 50MB
MIN_RELEVANCE_SCORE=0.5   # Higher threshold
EMBEDDING_MODEL=all-mpnet-base-v2  # Better quality
```

---

**Last Updated:** June 2024  
**Phase:** 2 (Complete)  
**Next Phase:** 3 (LLM Integration)
