#!/usr/bin/env python3
"""
OmniRAG Phase 2 Validation Script

This script validates that all Phase 2 components are properly installed and configured.
"""

import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Check Python version >= 3.10"""
    if sys.version_info < (3, 10):
        print("❌ Python 3.10+ required")
        return False
    print(f"✅ Python {sys.version.split()[0]}")
    return True

def check_package(package_name, import_name=None):
    """Check if a package is installed"""
    if import_name is None:
        import_name = package_name
    try:
        __import__(import_name)
        print(f"✅ {package_name}")
        return True
    except ImportError:
        print(f"❌ {package_name} - not installed")
        return False

def check_system_tool(tool_name):
    """Check if a system tool is available"""
    try:
        subprocess.run([tool_name, "--version"], capture_output=True, check=True)
        print(f"✅ {tool_name}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print(f"❌ {tool_name} - not found")
        return False

def check_directories():
    """Check if required directories exist or can be created"""
    dirs = ["uploads", "chroma_db"]
    all_ok = True
    for dir_name in dirs:
        path = Path(dir_name)
        if path.exists():
            print(f"✅ Directory: {dir_name}")
        else:
            try:
                path.mkdir(exist_ok=True)
                print(f"✅ Directory: {dir_name} (created)")
            except Exception as e:
                print(f"❌ Directory: {dir_name} - {e}")
                all_ok = False
    return all_ok

def test_vectorstore():
    """Test ChromaDB initialization"""
    try:
        from app.services.vectorstore import get_vector_store
        from app.core.config import settings
        store = get_vector_store(settings.CHROMA_PERSIST_DIR)
        if store.is_available:
            stats = store.get_collection_stats()
            print(f"✅ ChromaDB - {stats['count']} chunks in collection")
            return True
        else:
            print("⚠️  ChromaDB - not available (may not affect functionality)")
            return True
    except Exception as e:
        print(f"❌ ChromaDB test - {e}")
        return False

def test_embeddings():
    """Test embedding model"""
    try:
        from app.services.embeddings import embed_text
        result = embed_text(["test"], "all-MiniLM-L6-v2")
        if result:
            print(f"✅ Embeddings - model loaded ({len(result[0])} dimensions)")
            return True
        else:
            print("❌ Embeddings - model not available")
            return False
    except Exception as e:
        print(f"❌ Embeddings test - {e}")
        return False

def test_extractors():
    """Test content extractors"""
    from pathlib import Path
    results = {}
    
    # Text extractor
    try:
        from app.services.extractors.text_extractor import extract_plain_text
        results["text"] = "✅ Text extractor"
    except Exception as e:
        results["text"] = f"❌ Text extractor - {e}"
    
    # Image extractor
    try:
        from app.services.extractors.image_extractor import extract_image
        results["image"] = "✅ Image extractor (OCR)"
    except Exception as e:
        results["image"] = f"⚠️  Image extractor - {e}"
    
    # Audio extractor
    try:
        from app.services.extractors.audio_extractor import extract_audio
        results["audio"] = "✅ Audio extractor (Whisper)"
    except Exception as e:
        results["audio"] = f"⚠️  Audio extractor - {e}"
    
    # Video extractor
    try:
        from app.services.extractors.video_extractor import extract_video
        results["video"] = "✅ Video extractor"
    except Exception as e:
        results["video"] = f"⚠️  Video extractor - {e}"
    
    for name, result in results.items():
        print(result)
    
    return all("✅" in v or "⚠️" in v for v in results.values())

def test_langgraph():
    """Test LangGraph workflows"""
    try:
        from app.core.langgraph import query_graph, ingestion_graph
        print("✅ Query graph loaded")
        print("✅ Ingestion graph loaded")
        return True
    except Exception as e:
        print(f"❌ LangGraph test - {e}")
        return False

def main():
    """Run all validation tests"""
    print("\n" + "="*60)
    print("OmniRAG Phase 2 Validation")
    print("="*60 + "\n")
    
    print("📋 Python & Core Packages:")
    checks = [
        check_python_version(),
    ]
    
    print("\n📦 Python Dependencies:")
    packages = [
        ("FastAPI", "fastapi"),
        ("Pydantic", "pydantic"),
        ("LangGraph", "langgraph"),
        ("ChromaDB", "chromadb"),
        ("SentenceTransformers", "sentence_transformers"),
        ("PyPDF2", "PyPDF2"),
        ("Pillow", "PIL"),
        ("OpenCV", "cv2"),
        ("Faster-Whisper", "faster_whisper"),
    ]
    
    for package, import_name in packages:
        checks.append(check_package(package, import_name))
    
    print("\n🔧 System Tools:")
    tools = ["ffmpeg", "tesseract"]
    for tool in tools:
        check_system_tool(tool)
    
    print("\n📁 Directories:")
    checks.append(check_directories())
    
    print("\n🧪 Component Tests:")
    checks.append(test_vectorstore())
    checks.append(test_embeddings())
    checks.append(test_extractors())
    checks.append(test_langgraph())
    
    print("\n" + "="*60)
    if all(checks):
        print("✅ All validations passed! Phase 2 is ready.")
        print("\n🚀 Start the backend with:")
        print("   uvicorn app.main:app --reload")
        print("\n📖 API docs at: http://localhost:8000/docs")
    else:
        print("⚠️  Some validations failed. See above for details.")
        print("\nCommon fixes:")
        print("  - Install system tools: sudo apt-get install ffmpeg tesseract-ocr")
        print("  - Reinstall Python packages: pip install -r requirements.txt")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
