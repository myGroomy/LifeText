"""Job model for tracking transcription tasks."""
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, String, DateTime, Text, Integer, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class JobStatus(str, Enum):
    """Job status enum."""
    QUEUED = "queued"
    PROCESSING = "processing"
    DONE = "done"
    FAILED = "failed"


class Job(Base):
    """Database model for transcription jobs."""
    
    __tablename__ = "jobs"
    
    job_id = Column(String(36), primary_key=True, index=True)
    user_id = Column(String(100), index=True)
    status = Column(String(20), default=JobStatus.QUEUED)
    
    # Input
    file_path = Column(String(500))
    original_filename = Column(String(500))
    file_size = Column(Integer)  # bytes
    language = Column(String(10), default="id")  # ISO language code
    
    # Output
    raw_transcript = Column(Text, nullable=True)
    clean_transcript = Column(Text, nullable=True)
    quality_score = Column(Integer, nullable=True)  # 0-10
    flag_review = Column(Boolean, default=False)
    output_format = Column(String(20), default="plain")  # plain, srt, vtt, json
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    error_message = Column(Text, nullable=True)
