from datetime import datetime, timezone

from database.db import Base
from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey, Boolean
from sqlalchemy.orm import relationship
import enum


class Video(Base):
    __tablename__ = "videos"
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=True)
    file_size = Column(Integer)
    upload_date = Column(DateTime, default=datetime.now(timezone.utc))
    upload_job = relationship("UploadJob", backref="video", uselist=False)
    upload_path = Column(String, nullable=True)


class JobStatus(enum.Enum):
    pending = "pending"
    completed = "completed"
    failed = "failed"


class UploadJob(Base):
    __tablename__ = "upload_jobs"
    job_id = Column(String, primary_key=True, index=True)
    status = Column(Enum(JobStatus), default=JobStatus.pending)
    error = Column(String, nullable=True)
    video_id = Column(Integer, ForeignKey("videos.id"))


class Role(enum.Enum):
    admin = "admin"
    user = "user"


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    role = Column(Enum(Role), default=Role.user)
