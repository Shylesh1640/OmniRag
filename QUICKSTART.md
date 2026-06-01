# OmniRAG Phase 2 - Quick Start & Deployment Guide

## ⚡ Ultra-Quick Start (5 minutes)

### Backend

```bash
# Navigate to backend
cd backend

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Verify installation
python validate.py

# Start server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Visit: `http://localhost:8000/docs` for API documentation

### Frontend

```bash
# In a new terminal, navigate to frontend
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Visit: `http://localhost:3000`

### Test It Out

1. **Upload a file** via frontend or:
   ```bash
   curl -F "file=@document.pdf" http://localhost:8000/api/v1/upload
   ```

2. **Ask a question** via frontend or:
   ```bash
   curl -X POST -H "Content-Type: application/json" \
     -d '{"message":"What is this about?"}' \
     http://localhost:8000/api/v1/chat
   ```

## 📋 Pre-requisites

### System Requirements

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y python3.10 python3-pip python3-venv
sudo apt-get install -y ffmpeg tesseract-ocr
sudo apt-get install -y build-essential

# macOS
brew install python@3.10 ffmpeg tesseract node

# Windows
# 1. Download Python 3.10+ from python.org
# 2. Download FFmpeg from ffmpeg.org
# 3. Download Tesseract from github.com/UB-Mannheim/tesseract/wiki
# 4. Download Node.js from nodejs.org
```

### Check Installations

```bash
python --version          # Should be 3.10+
node --version            # Should be 18+
ffmpeg -version           # Should show FFmpeg version
tesseract --version       # Should show Tesseract version
```

## 🚀 Full Setup Steps

### 1. Clone/Setup Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install Python packages
pip install -r requirements.txt

# Configure environment (optional)
# Copy .env.example to .env and customize if needed
# Most defaults work fine for local development

# Validate everything is working
python validate.py

# If validation passes, start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Expected Output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

### 2. Setup Frontend (New Terminal)

```bash
cd frontend

# Install Node packages
npm install

# Start development server
npm run dev
```

**Expected Output:**
```
> next dev
  ▲ Next.js 14.x.x
  - Local:        http://localhost:3000
```

### 3. Verify Everything Works

Open `http://localhost:3000` in your browser and:

1. **Upload a file:**
   - Click "Files" in navigation
   - Click "Upload New File"
   - Select any: .txt, .pdf, .png, .mp3, .mp4
   - Wait for confirmation

2. **Ask a question:**
   - Click "Chat" in navigation
   - Type a question about the uploaded file
   - View response with sources

## 📁 File Organization

```
OmniRAG/
├── backend/
│   ├── app/                    # Main application
│   │   ├── api/               # API endpoints
│   │   ├── core/              # Config & workflows
│   │   ├── models/            # Data models
│   │   ├── services/          # Business logic
│   │   └── utils/             # Utilities
│   ├── uploads/               # Auto-created, uploaded files
│   ├── chroma_db/             # Auto-created, vector database
│   ├── requirements.txt        # Python dependencies
│   ├── .env                    # Configuration
│   ├── validate.py            # Validation script
│   └── README.md              # Backend docs
│
├── frontend/
│   ├── app/                   # Next.js pages
│   ├── components/            # React components
│   ├── lib/                   # Utilities
│   ├── package.json           # Node dependencies
│   └── README.md              # Frontend docs
│
├── README.md                   # Main project README
├── PHASE2.md                   # Phase 2 documentation
├── ARCHITECTURE.md             # Detailed architecture
└── PROJECT_STRUCTURE.md        # This file
```

## ⚙️ Configuration

### Basic Configuration (.env)

The backend uses `backend/.env` for configuration. Default values work for local development:

```
# Most important settings for Phase 2:

CHUNK_SIZE=500                    # Words per chunk (smaller = more chunks)
TOP_K_RETRIEVAL=5                 # How many results to retrieve
MIN_RELEVANCE_SCORE=0.3           # Relevance threshold (0-1, lower = more results)
EMBEDDING_MODEL=all-MiniLM-L6-v2  # Embedding model (fast, 384 dims)
WHISPER_MODEL_SIZE=base           # Audio model (tiny/base/small/medium/large)
```

### For Better Quality

If you want more accurate results (slower processing):

```
CHUNK_SIZE=300                    # Smaller chunks
MIN_RELEVANCE_SCORE=0.5           # Higher threshold
EMBEDDING_MODEL=all-mpnet-base-v2 # Better quality
WHISPER_MODEL_SIZE=medium         # Better transcription
```

### For Faster Processing

```
CHUNK_SIZE=1000                   # Larger chunks
MIN_RELEVANCE_SCORE=0.2           # Lower threshold
EMBEDDING_MODEL=all-MiniLM-L6-v2  # Fastest
WHISPER_MODEL_SIZE=tiny           # Fastest
```

## 🧪 Testing

### Run Validation Script

```bash
cd backend
python validate.py
```

This checks:
- ✅ Python version
- ✅ All packages installed
- ✅ System tools available
- ✅ Vector store initialized
- ✅ Embedding model loaded
- ✅ LangGraph workflows
- ✅ All extractors

### Run Component Tests

```bash
cd backend
python test_phase2.py
```

This tests:
- ✅ Module imports
- ✅ Text chunking
- ✅ Embedding generation
- ✅ Vector store operations
- ✅ API schemas

### Manual API Tests

```bash
# Upload text file
echo "Hello world. This is a test document." > test.txt
curl -F "file=@test.txt" http://localhost:8000/api/v1/upload

# List files
curl http://localhost:8000/api/v1/files

# Query
curl -X POST -H "Content-Type: application/json" \
  -d '{"message":"What is in the document?"}' \
  http://localhost:8000/api/v1/chat
```

## 🐛 Troubleshooting

### Backend Won't Start

```bash
# Issue: Port 8000 already in use
# Solution: Use different port
uvicorn app.main:app --port 8001

# Issue: Module not found
# Solution: Install requirements again
pip install -r requirements.txt

# Issue: ChromaDB error
# Solution: Reset database
rm -rf chroma_db
python validate.py  # Will recreate
```

### Frontend Won't Start

```bash
# Issue: Port 3000 already in use
# Solution: Use different port
npm run dev -- -p 3001

# Issue: Modules not found
# Solution: Reinstall dependencies
rm -rf node_modules package-lock.json
npm install
```

### FFmpeg or Tesseract Missing

```bash
# Ubuntu/Debian
sudo apt-get install ffmpeg tesseract-ocr

# macOS
brew install ffmpeg tesseract

# Windows
# Download from ffmpeg.org and github.com/UB-Mannheim/tesseract/wiki
```

### Out of Memory

If processing fails due to memory:

1. Reduce `CHUNK_SIZE` (default 500 → try 300)
2. Use smaller `WHISPER_MODEL_SIZE` (base → tiny)
3. Process one file at a time
4. Restart services to clear memory

### Embeddings Taking Too Long

The first time embeddings are generated, the model (~24MB) is downloaded. This may take 1-2 minutes. Subsequent requests will be instant due to caching.

## 📊 Expected Performance

### Typical Processing Times (CPU, 4GB RAM)

| File Type | Size | Processing Time |
|-----------|------|-----------------|
| Text | 100 KB | < 1 second |
| PDF | 500 KB | 5-10 seconds |
| Image | 2 MB | 3-5 seconds |
| Audio | 2 MB (1 min) | 10-15 seconds |
| Video | 50 MB (1 min) | 60-90 seconds |

### First-Time Setup

| Component | Time |
|-----------|------|
| Backend setup | 2-3 minutes |
| Model downloads | 2-5 minutes (varies by internet) |
| First query | 2-3 seconds |
| Subsequent queries | < 500ms |

## 🔌 API Endpoints Summary

### Upload File
```
POST /api/v1/upload
Returns: IngestionResult with file_id and chunks_count
```

### List Files
```
GET /api/v1/files
Returns: Array of uploaded files with metadata
```

### Get File Details
```
GET /api/v1/files/{file_id}
Returns: File metadata
```

### Chat Query
```
POST /api/v1/chat
Body: {"message": "your question"}
Returns: ChatResponse with answer, citations, and confidence
```

### API Documentation
```
GET http://localhost:8000/docs
```

Interactive Swagger UI for all endpoints

## 📚 Documentation Files

| File | Purpose |
|------|---------|
| [README.md](README.md) | Project overview |
| [PHASE2.md](PHASE2.md) | Complete Phase 2 documentation |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Detailed architecture & components |
| [backend/README.md](backend/README.md) | Backend-specific guide |
| [frontend/README.md](frontend/README.md) | Frontend-specific guide (if exists) |

## 🚀 Production Deployment

### Docker

```dockerfile
FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
    ffmpeg tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t omnirag-backend .
docker run -p 8000:8000 -v $(pwd)/chroma_db:/app/chroma_db omnirag-backend
```

### Environment Variables (Production)

```
BACKEND_CORS_ORIGINS=["https://yourdomain.com"]
CHROMA_PERSIST_DIR=/data/chroma_db
MAX_UPLOAD_SIZE=52428800
MIN_RELEVANCE_SCORE=0.5
EMBEDDING_MODEL=all-mpnet-base-v2
```

## 🔐 Security Notes

⚠️ **Phase 2 is for development/demo only. Before production:**

- [ ] Add authentication/authorization
- [ ] Implement rate limiting
- [ ] Add input validation
- [ ] Set up HTTPS
- [ ] Enable audit logging
- [ ] Encrypt sensitive data
- [ ] Use environment secrets (not .env)
- [ ] Configure proper CORS origins

(These will be added in Phase 3)

## 📞 Support & Resources

### If Something Doesn't Work

1. Run `python validate.py` to check system
2. Check error logs (watch terminal output)
3. See troubleshooting section above
4. Review relevant README or architecture docs
5. Check GitHub issues (if applicable)

### Learning Resources

- **LangGraph:** https://langchain.com/langgraph
- **ChromaDB:** https://docs.trychroma.com
- **Whisper:** https://github.com/openai/whisper
- **Tesseract:** https://github.com/UB-Mannheim/tesseract/wiki
- **FastAPI:** https://fastapi.tiangolo.com
- **Next.js:** https://nextjs.org

## ✅ Checklist for First Run

- [ ] System tools installed (ffmpeg, tesseract)
- [ ] Python 3.10+ installed
- [ ] Node.js 18+ installed
- [ ] Backend virtual environment created
- [ ] Python dependencies installed
- [ ] `validate.py` passes all checks
- [ ] Backend running on port 8000
- [ ] Frontend running on port 3000
- [ ] Can upload a test file
- [ ] Can query the knowledge base
- [ ] Responses include citations

## 🎉 Next Steps After Setup

1. **Explore the UI** - Try different file types
2. **Review responses** - Check quality of citations
3. **Adjust settings** - Tune CHUNK_SIZE, MIN_RELEVANCE_SCORE
4. **Read documentation** - Understand architecture
5. **Plan Phase 3** - Consider LLM integration

---

**Happy RAG-ing! 🚀**

For detailed information, see [PHASE2.md](PHASE2.md) and [ARCHITECTURE.md](ARCHITECTURE.md)
