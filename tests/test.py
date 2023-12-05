import datetime

import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock

from jose import jwt
from config import settings
from main import app
from database.models import UploadJob, User, Role, Video


@pytest.fixture
def admin_user(db_session):
    admin_user = User(email="admin@example.com", password="admin_password", role=Role.admin)
    db_session.add(admin_user)
    db_session.commit()
    data = {"sub": admin_user.email}
    admin_token = jwt.encode(data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return admin_token


@pytest.fixture
def non_admin_user(db_session):
    just_user = User(email="admin@example.com", password="admin_password", role=Role.user)
    db_session.add(just_user)
    db_session.commit()
    data = {"sub": just_user.email}
    user_token = jwt.encode(data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return user_token


client = TestClient(app)


def test_upload_video_valid():
    with client as c:
        response = c.post("/upload-video/",
                          files={"video_file": ("test_video.mp4", open("resource/test_video.mkv", "rb"))},
                          headers={"Authorization": f"Bearer {admin_user}"})
        assert response.status_code == 200
        assert "job_id" in response.json()


def test_upload_video_invalid_file():
    with client as c:
        response = c.post("/upload-video/",
                          files={"video_file": ("test_image.jpg", open("resource/test_image.jpg", "rb"))},
                          headers={"Authorization": f"Bearer {admin_user}"})
        assert response.status_code == 400
        assert "Uploaded file: test_image.jpg, is not a video!" in response.text


def test_check_upload_valid():
    job_id = "dummy_job_id"
    upload_job = UploadJob(job_id=job_id, status="success", video_id="dummy_video_id", error=None)
    db = MagicMock()
    db.get_upload_job.return_value = upload_job

    with client as c:
        response = c.get(f"/check-upload/{job_id}", headers={"Authorization": f"Bearer {admin_user}"})
        assert response.status_code == 200
        assert response.json()["job_id"] == job_id


def test_check_upload_invalid():
    job_id = "nonexistent_job_id"
    db = MagicMock()
    db.get_upload_job.return_value = None

    with client as c:
        response = c.get(f"/check-upload/{job_id}", headers={"Authorization": f"Bearer {admin_user}"})
        assert response.status_code == 404
        assert f"Job with ID={job_id}, not found" in response.text


def test_get_videos_admin():
    video = Video(id=1, filename="some_file_name", file_size=50, upload_date=datetime.datetime.now())
    db = MagicMock()
    db.get_video.return_value = video
    with client as c:
        response = client.get("/videos/", headers={"Authorization": f"Bearer {admin_user}"})
        assert response.status_code == 200
        assert isinstance(response.json(), list)


def test_get_videos_non_admin():
    db = MagicMock()
    db.get_video.return_value = None
    with client as c:
        response = client.get("/videos/", headers={"Authorization": f"Bearer {non_admin_user}"})
        assert response.status_code == 403
