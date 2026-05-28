from fastapi import APIRouter, HTTPException
from app.services.file_service import get_files, get_file
from app.models.file import File
from typing import List

router = APIRouter()

@router.get("", response_model=List[File])
async def list_files():
    files = get_files()
    return files

@router.get("/{file_id}", response_model=File)
async def get_file_by_id(file_id: str):
    file = get_file(file_id)
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    return file