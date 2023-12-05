# api/routers/video.py
from fastapi import APIRouter, File, UploadFile, HTTPException, BackgroundTasks, Depends
from database.db import get_db
from database.crud import create_upload_job, get_upload_job, create_video
from services.video import VideoProcessor

router = APIRouter()


@router.post("/upload-video/")
async def upload_video(
        background_tasks: BackgroundTasks,
        video_file: UploadFile = File(...),
        db=Depends(get_db),):
    if video_file.content_type.startswith("video"):
        job_id = str(hash(video_file.filename))
        video = create_video(db, video_file.filename, video_file.size)
        create_upload_job(db=db, job_id=job_id, video_id=video.filename)
        background_tasks.add_task(VideoProcessor.process_upload, db, job_id, video_file)
        return {"message": "Video upload started", "job_id": job_id}
    else:
        return HTTPException(status_code=400, detail=f"Uploaded file: {video_file.filename}, is not a video!")


@router.get("/check-upload/{job_id}")
async def check_upload(job_id: str, db=Depends(get_db)):
    job = get_upload_job(db, job_id)
    if job:
        return {"job_id": job.job_id, "status": job.status, "video_id": job.video_id, "error": job.error}
    else:
        raise HTTPException(status_code=404, detail=f"Job with ID={job_id}, not found")
