from fastapi import APIRouter, File, UploadFile, HTTPException
from app.utils.storage import save_file
from app.models.file import File
from app.core.config import settings

router = APIRouter()

@router.post("", response_model=File)
async def upload_file(file: UploadFile = File(...)):
    # Check file size
    contents = await file.read()
    if len(contents) > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=413, detail="File too large")
    
    # Save file using storage
    db_file = save_file(
        file_content=contents,
        filename=file.filename,
        content_type=file.content_type
    )
    return db_file