from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class UploadVideoResponse(BaseModel):
    message: str
    job_id: str


class CheckUploadResponse(BaseModel):
    job_id: str
    status: str
    video_id: Optional[int] = None
    error: Optional[str] = None


class VideoResponse(BaseModel):
    id: int
    filename: Optional[str] = None
    file_size: int
    upload_date: Optional[datetime] = None
    upload_path: Optional[str] = None
