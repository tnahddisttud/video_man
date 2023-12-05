from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from main import app
from database.models import UploadJob

client = TestClient(app)


def test_upload_video_valid():
    with client as c:
        response = c.post("/upload-video/", files={"video_file": ("test_video.mp4", open("test_video.mp4", "rb"))})
        assert response.status_code == 200
        assert "job_id" in response.json()


def test_upload_video_invalid_file():
    with client as c:
        response = c.post("/upload-video/", files={"video_file": ("test_image.jpg", open("test_image.jpg", "rb"))})
        assert response.status_code == 400
        assert "Uploaded file: test_image.jpg, is not a video!" in response.text


def test_check_upload_valid():
    job_id = "dummy_job_id"
    upload_job = UploadJob(job_id=job_id, status="success", video_id="dummy_video_id", error=None)
    db = MagicMock()
    db.get_upload_job.return_value = upload_job

    with client as c:
        response = c.get(f"/check-upload/{job_id}")
        assert response.status_code == 200
        assert response.json()["job_id"] == job_id


def test_check_upload_invalid():
    job_id = "nonexistent_job_id"
    db = MagicMock()
    db.get_upload_job.return_value = None

    with client as c:
        response = c.get(f"/check-upload/{job_id}")
        assert response.status_code == 404
        assert f"Job with ID={job_id}, not found" in response.text
