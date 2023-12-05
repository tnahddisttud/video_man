import asyncio
import os
from fastapi import UploadFile, HTTPException
from database.models import JobStatus
from database.crud import update_upload_job, update_video
import moviepy.editor as moviepy


class VideoConverter:
    @staticmethod
    def convert_video(video_file: UploadFile):
        try:
            os.makedirs("files/uploads", exist_ok=True)
            os.makedirs("files/converted", exist_ok=True)
            upload_path = os.path.join("files/uploads", video_file.filename)
            with open(upload_path, "wb") as f:
                f.write(video_file.file.read())
            output_path = os.path.join("files/converted", f"{video_file.filename.rsplit('.', 1)[0]}.mp4")
            clip = moviepy.VideoFileClip(upload_path)
            clip.write_videofile(output_path)
            return output_path
        except Exception as e:
            print(e)
            raise HTTPException(status_code=500, detail=f"Failed to process video: {str(e)}")


class VideoProcessor:
    @staticmethod
    async def process_upload(db, job_id: str, video_id: int, video_file: UploadFile):
        try:
            video_path = await asyncio.to_thread(VideoConverter.convert_video, video_file)
            update_upload_job(db=db, job_id=job_id, status=JobStatus.completed)
            update_video(db=db, video_id=video_id, filename=video_file.filename, file_size=video_file.size,
                         upload_path=video_path)
            db.commit()
        except HTTPException as e:
            print(e)
            update_upload_job(db=db, job_id=job_id, status=JobStatus.failed, error=str(e))
        except Exception as e:
            print(e)
            update_upload_job(db=db, job_id=job_id, status=JobStatus.failed, error=f"Unexpected error: {str(e)}")
