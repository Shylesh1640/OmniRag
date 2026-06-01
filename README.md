# OmniRAG - Multimodal RAG System

A production-ready multimodal Retrieval-Augmented Generation (RAG) system supporting Text, PDF, Image, Audio, and Video content with semantic search, intelligent routing, and cited responses.

## 🚀 Status

- **Phase 1** ✅ Complete
  - Next.js frontend with chat and file upload
  - FastAPI backend with basic routing
  - File upload and listing

- **Phase 2** ✅ Complete
  - Multimodal content extraction (Text, PDF, Image, Audio, Video)
  - Semantic embeddings and ChromaDB vector store
  - LangGraph orchestration with routing and fallback
  - Citation-based response generation
  - Relevance grading and confidence scores

- **Phase 3** 🚧 Coming Soon
  - LLM integration (OpenAI/Llama/Ollama)
  - Multi-turn conversation support
  - Advanced retrieval and re-ranking
  - Knowledge graph integration
  - User authentication and multi-tenant support

## 📋 System Architecture

```
┌─────────────────────────────────────────────────┐
│        Next.js Frontend                         │
│  (Chat Interface, File Upload, File Browser)   │
└──────────────────┬──────────────────────────────┘
                   │ HTTP/REST
                   ▼
┌─────────────────────────────────────────────────┐
│        FastAPI Backend                          │
│  ┌─────────────────────────────────────────┐   │
│  │  Multimodal Extraction Layer            │   │
│  │  • Text/PDF (PyPDF2)                    │   │
│  │  • Images (Tesseract OCR)               │   │
│  │  • Audio (Whisper)                      │   │
│  │  • Video (FFmpeg + Whisper + OCR)       │   │
│  └─────────────────────────────────────────┘   │
│                     │                           │
│  ┌─────────────────────────────────────────┐   │
│  │  LangGraph Orchestration                │   │
│  │  • Ingestion Pipeline                   │   │
│  │  • Query Pipeline with Routing          │   │
│  │  • Fallback Handling                    │   │
│  └─────────────────────────────────────────┘   │
│                     │                           │
│  ┌─────────────────────────────────────────┐   │
│  │  RAG Core                               │   │
│  │  • Semantic Chunking                    │   │
│  │  • Embeddings (SentenceTransformers)    │   │
│  │  • Vector Search (ChromaDB)             │   │
│  │  • Relevance Grading                    │   │
│  └─────────────────────────────────────────┘   │
└─────────────────────────────────────────────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │  ChromaDB Vector DB   │
         │  (Persistent Store)   │
         └───────────────────────┘
```

## ✨ Key Features

### Content Support
- ✅ **Text** - Plain text, markdown
- ✅ **PDF** - Multi-page document extraction with page metadata
- ✅ **Images** - OCR with caption generation
- ✅ **Audio** - Speech-to-text with timestamp preservation
- ✅ **Video** - Audio transcription + key frame extraction + OCR

### Intelligence
- 🧠 **Semantic Search** - Find relevant content by meaning, not keywords
- 📊 **Relevance Grading** - Confidence-based confidence (high/medium/low)
- 🔗 **Smart Citations** - Responses include source references with metadata
- 🎯 **Intelligent Routing** - Fallback when retrieval confidence is low
- 📝 **Metadata Preservation** - Track source, page number, timestamp, chunk index

### Technology
- 🦀 **LangGraph** - Clear, composable workflow orchestration
- 🚀 **FastAPI** - High-performance async API
- ⚡ **ChromaDB** - Lightweight vector database
- 🤖 **Whisper** - Free, multilingual audio transcription
- 🖼️ **Tesseract** - Proven OCR technology
- 🧬 **SentenceTransformers** - Efficient semantic embeddings

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- System tools: `ffmpeg`, `tesseract-ocr`

### Backend

```bash
cd backend

# Setup
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure (optional)
cp .env.example .env

# Validate
python validate.py

# Run
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API docs: http://localhost:8000/docs

### Frontend

```bash
cd frontend

# Setup
npm install

# Run
npm run dev
```

Access at: http://localhost:3000

## 📚 Detailed Documentation

- **[Phase 2 Architecture](./PHASE2.md)** - Complete technical documentation
- **[Backend Guide](./backend/README.md)** - Backend setup and API reference
- **[Frontend Guide](./frontend/README.md)** - Frontend setup (if exists)

## 🎯 How It Works

### 1. Upload a File

The system automatically detects file type and routes to appropriate extractor:

```bash
curl -F "file=@document.pdf" http://localhost:8000/api/v1/upload
```

**Processing:**
1. Extract content (text, OCR, transcription, etc.)
2. Split into semantic chunks
3. Generate embeddings
4. Store in vector database with metadata
5. Return ingestion status and chunk count

### 2. Query the Knowledge Base

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"message":"What is the main topic?"}' \
  http://localhost:8000/api/v1/chat
```

**Processing:**
1. Embed user query
2. Search vector database for similar chunks
3. Grade relevance with confidence scoring
4. Route to generation or fallback
5. Generate response with citations
6. Return response + sources + confidence

### 3. Response Format

```json
{
  "response": "Based on the retrieved information...",
  "citations": [
    {
      "text": "Quote from source",
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

## 🗂️ Project Structure

```
OmniRAG/
├── README.md                 # This file
├── PHASE2.md                 # Detailed Phase 2 architecture
│
├── backend/                  # FastAPI backend
│   ├── app/
│   │   ├── api/             # API endpoints
│   │   ├── core/            # Config & LangGraph workflows
│   │   ├── models/          # Data models & schemas
│   │   ├── services/        # Business logic
│   │   │   ├── extractors/  # Content extraction
│   │   │   ├── chunker.py
│   │   │   ├── embeddings.py
│   │   │   ├── retriever.py
│   │   │   └── vectorstore.py
│   │   └── utils/           # Utilities
│   ├── uploads/             # User uploads
│   ├── chroma_db/           # Vector database
│   ├── requirements.txt
│   ├── .env
│   ├── validate.py          # Validation script
│   └── README.md
│
└── frontend/                 # Next.js frontend
    ├── app/                 # Pages & layouts
    ├── components/          # React components
    ├── lib/                 # Utilities & API client
    ├── package.json
    └── README.md
```

## 📖 API Reference

### Chat Endpoint
```
POST /api/v1/chat
Content-Type: application/json

{
  "message": "Your query here"
}
```

**Response:**
- `response` - Generated answer with citations
- `citations` - List of source references with scores
- `confidence` - high/medium/low

### Upload Endpoint
```
POST /api/v1/upload
Content-Type: multipart/form-data

file: <binary>
```

**Response:**
- `file_id` - Unique file identifier
- `filename` - Original filename
- `chunks_count` - Number of chunks created
- `status` - success/failed
- `error` - Error message if applicable

### File Listing
```
GET /api/v1/files
```

Returns list of uploaded files with metadata.

### Get File Details
```
GET /api/v1/files/{file_id}
```

Returns specific file metadata.

## ⚙️ Configuration

Key settings in `backend/.env`:

| Setting | Default | Purpose |
|---------|---------|---------|
| `CHUNK_SIZE` | 500 | Words per chunk |
| `CHUNK_OVERLAP` | 50 | Word overlap between chunks |
| `TOP_K_RETRIEVAL` | 5 | Number of results to retrieve |
| `MIN_RELEVANCE_SCORE` | 0.3 | Threshold for result relevance |
| `EMBEDDING_MODEL` | all-MiniLM-L6-v2 | Embedding model name |
| `WHISPER_MODEL_SIZE` | base | Audio transcription model |
| `VIDEO_FRAME_INTERVAL` | 30 | Seconds between key frames |
| `MAX_UPLOAD_SIZE` | 100MB | File upload limit |

## 📊 Performance

**Typical processing times (CPU):**

| Content | Size | Time |
|---------|------|------|
| Text file | 100 KB | < 1s |
| PDF (10 pages) | 500 KB | 5-10s |
| Image | 2 MB | 3-5s |
| Audio (1 min) | 2 MB | 10-15s |
| Video (1 min) | 50 MB | 60-90s |

**Storage (approximate):**
- Each embedding: ~1.5 KB (384 dimensions)
- Example: 10,000 chunks ≈ 15 MB

## 🛠️ Development

### Run Validation
```bash
cd backend
python validate.py
```

Checks all dependencies, system tools, and components.

### Debug Specific Extractor
```python
from app.services.extractors.text_extractor import extract_text
result = extract_text("path/to/document.pdf")
print(result)
```

### Check Vector Store
```python
from app.services.vectorstore import get_vector_store
from app.core.config import settings

store = get_vector_store(settings.CHROMA_PERSIST_DIR)
stats = store.get_collection_stats()
print(f"Chunks in store: {stats['count']}")
```

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| ChromaDB errors | `rm -rf backend/chroma_db` and restart |
| Tesseract not found | `sudo apt-get install tesseract-ocr` |
| FFmpeg not found | `brew install ffmpeg` (macOS) or download from ffmpeg.org |
| Out of memory | Reduce `CHUNK_SIZE` or use smaller `WHISPER_MODEL_SIZE` |
| Slow responses | Switch to smaller embedding model |

## 📋 Requirements

### System
- Ubuntu 20.04+, macOS 10.15+, or Windows 10+
- 2GB+ RAM
- 5GB+ disk space for models and database

### Python Packages
- FastAPI, Pydantic, LangGraph
- ChromaDB, SentenceTransformers
- PyPDF2, Pillow, pytesseract
- OpenCV, faster-whisper
- (See requirements.txt for full list)

### System Tools
- ffmpeg - video/audio processing
- tesseract-ocr - optical character recognition

## 🗺️ Roadmap

### Phase 1 - ✅ Complete
- Frontend with chat interface
- Backend with file upload
- Basic routing

### Phase 2 - ✅ Complete
- Multimodal extraction
- Vector store integration
- LangGraph orchestration
- Relevance grading
- Source citations

### Phase 3 - 🚧 In Progress
- LLM integration (OpenAI/Llama/Ollama)
- Multi-turn conversations
- Query expansion & re-ranking
- User authentication
- Advanced analytics

### Phase 4+ - 🔮 Future
- Knowledge graph integration
- Fine-tuning on custom data
- Batch processing
- Mobile app
- Enterprise features

## 📄 License

[Add your license here]

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📞 Support

- 📖 [Phase 2 Documentation](./PHASE2.md)
- 🐛 [GitHub Issues](https://github.com/your-repo/issues)
- 💬 [Discussions](https://github.com/your-repo/discussions)

## 🙏 Acknowledgments

- LangGraph for orchestration framework
- Hugging Face for models and libraries
- OpenAI Whisper for transcription
- ChromaDB for vector storage

---

**Built with ❤️ for the RAG community**