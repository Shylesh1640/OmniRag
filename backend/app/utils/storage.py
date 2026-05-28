import os
import shutil
from pathlib import Path
from typing import List, Optional
import json
from app.models.file import File, FileCreate
from app.core.config import settings

# Ensure the upload directory exists
UPLOAD_DIR = Path(settings.UPLOAD_DIR)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Metadata file path
METADATA_FILE = UPLOAD_DIR / "metadata.json"

def _load_metadata() -> dict:
    if METADATA_FILE.exists():
        with open(METADATA_FILE, "r") as f:
            return json.load(f)
    return {}

def _save_metadata(metadata: dict):
    with open(METADATA_FILE, "w") as f:
        json.dump(metadata, f, indent=2, default=str)

def save_file(*, file_content: bytes, filename: str, content_type: str) -> File:
    # Generate a unique ID for the file (using the filename and timestamp for simplicity)
    # In a real app, you might use UUID or a database ID
    file_id = f"{filename}_{int(os.path.getmtime(UPLOAD_DIR))}"
    
    # Save the file
    file_path = UPLOAD_DIR / file_id
    with open(file_path, "wb") as f:
        f.write(file_content)
    
    # Create file metadata
    file_metadata = FileCreate(
        filename=filename,
        content_type=content_type,
        size=len(file_content)
    )
    
    # Load existing metadata
    metadata = _load_metadata()
    
    # Add new file metadata
    metadata[file_id] = {
        "id": file_id,
        "filename": file_metadata.filename,
        "content_type": file_metadata.content_type,
        "size": file_metadata.size,
        "upload_time": str(os.path.getctime(file_path))
    }
    
    # Save metadata
    _save_metadata(metadata)
    
    # Return the file object
    return File(
        id=file_id,
        filename=file_metadata.filename,
        content_type=file_metadata.content_type,
        size=file_metadata.size,
        upload_time=str(os.path.getctime(file_path))
    )

def get_files() -> List[File]:
    metadata = _load_metadata()
    files = []
    for file_id, file_data in metadata.items():
        files.append(File(**file_data))
    return files

def get_file(file_id: str) -> Optional[File]:
    metadata = _load_metadata()
    if file_id in metadata:
        return File(**metadata[file_id])
    return None

def delete_file(file_id: str) -> bool:
    metadata = _load_metadata()
    if file_id not in metadata:
        return False
    
    # Delete the file
    file_path = UPLOAD_DIR / file_id
    if file_path.exists():
        file_path.unlink()
    
    # Remove from metadata
    del metadata[file_id]
    _save_metadata(metadata)
    return True