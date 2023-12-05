from typing import Type, List

from sqlalchemy.orm import Session
from .models import Video, UploadJob, JobStatus


def create_video(db: Session, filename: str, file_size: int) -> Video:
    video = Video(filename=filename, file_size=file_size)
    db.add(video)
    db.commit()
    db.refresh(video)
    return video


def update_video(db: Session, video_id: int, filename: str = None, file_size: int = None, upload_path: str = None):
    video = get_video(db, video_id)
    if video:
        if filename is not None:
            video.filename = filename
        if file_size is not None:
            video.file_size = file_size
        if upload_path is not None:
            video.upload_path = upload_path
        db.commit()
        db.refresh(video)

        return video
    else:
        return None


def get_video(db: Session, video_id: int) -> Type[Video] | None:
    return db.query(Video).filter(Video.id == video_id).first()


def get_videos(db: Session, skip: int = 0, limit: int = 10) -> list[Type[Video]]:
    return db.query(Video).offset(skip).limit(limit).all()


def create_upload_job(db: Session, job_id: str, video_id: int) -> UploadJob:
    upload_job = UploadJob(job_id=job_id, video_id=video_id)
    db.add(upload_job)
    db.commit()
    db.refresh(upload_job)
    return upload_job


def get_upload_job(db: Session, job_id: str) -> Type[UploadJob] | None:
    return db.query(UploadJob).filter(UploadJob.job_id == job_id).first()


def update_upload_job(db: Session, job_id: str, status: JobStatus, error: str = None) -> Type[UploadJob] | None:
    upload_job = get_upload_job(db, job_id)
    if upload_job:
        upload_job.status = status
        if error:
            upload_job.error = error
        if status == JobStatus.failed and upload_job.video:
            delete_video(db, upload_job.video_id)
        db.commit()
        db.refresh(upload_job)
    return upload_job


def delete_video(db: Session, video_id: int):
    video = get_video(db, video_id)
    if video:
        db.delete(video)
        db.commit()
