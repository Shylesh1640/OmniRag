from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class FileBase(BaseModel):
    filename: str
    content_type: str
    size: int

class FileCreate(FileBase):
    pass

class File(FileBase):
    id: str
    upload_time: datetime
    
    class Config:
        orm_mode = True