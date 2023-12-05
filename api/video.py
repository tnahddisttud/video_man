# api/routers/video.py
from typing import List
from fastapi import APIRouter, File, UploadFile, HTTPException, BackgroundTasks, Depends, Query, status
from datetime import datetime
from database.db import get_db
from database.crud import create_upload_job, get_upload_job, create_video
from database.models import Video, User, Role
from services.video import VideoProcessor
from schema.schemas import UploadVideoResponse, CheckUploadResponse, VideoResponse
from jose import jwt
from config import settings
from .auth import oauth2_scheme

router = APIRouter()


def get_user_from_token(db, token):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, settings.ALGORITHM)
        username = payload.get("sub")
        if not username:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate Credentials",
            )
    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate Credentials",
        )
    user = db.query(User).filter(User.email == username).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
    return user


@router.post("/upload-video/", tags=["Video"], response_model=UploadVideoResponse)
async def upload_video(
        background_tasks: BackgroundTasks,
        video_file: UploadFile = File(...),
        db=Depends(get_db), token: str = Depends(oauth2_scheme)):
    user = get_user_from_token(db, token)
    if user.role is not Role.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    if video_file.content_type.startswith("video"):
        job_id = str(hash(video_file.filename))
        video = create_video(db, video_file.filename, video_file.size)
        create_upload_job(db=db, job_id=job_id, video_id=video.id)
        background_tasks.add_task(VideoProcessor.process_upload, db, job_id, video.id, video_file)
        return {"message": "Video upload started", "job_id": job_id}
    else:
        raise HTTPException(status_code=400, detail=f"Uploaded file: {video_file.filename}, is not a video!")


@router.get("/check-upload/{job_id}", tags=["Video"], response_model=CheckUploadResponse)
async def check_upload(job_id: str, db=Depends(get_db), token: str = Depends(oauth2_scheme)):
    user = get_user_from_token(db, token)
    if user.role is not Role.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    job = get_upload_job(db, job_id)
    if job:
        return {"job_id": job.job_id, "status": job.status, "video_id": job.video_id,
                "error": job.error}
    else:
        raise HTTPException(status_code=404, detail=f"Job with ID={job_id}, not found")


@router.get("/videos/", tags=["Video"], response_model=List[VideoResponse])
async def get_videos(video_id: int = Query(None, title="Video ID filter"),
                     filename: str = Query(None, title="Filename filter"),
                     file_size: int = Query(None, title="File size filter"),
                     upload_date: datetime = Query(None, title="Upload date filter"),
                     db=Depends(get_db), token: str = Depends(oauth2_scheme)):
    user = get_user_from_token(db, token)
    if user.role is not Role.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    query = db.query(Video)

    if video_id:
        query = query.filter(Video.id == video_id)

    if filename:
        query = query.filter(Video.filename == filename)

    if file_size is not None:
        query = query.filter(Video.file_size == file_size)

    if upload_date:
        query = query.filter(Video.upload_date == upload_date)

    videos = query.all()
    if videos:
        return videos
    else:
        raise HTTPException(status_code=404, detail="Could not find a video matching the query.")
