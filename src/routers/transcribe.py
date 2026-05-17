"""Transcription endpoints."""
import uuid
import logging
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from src.db import get_db
from src.models import Job, JobStatus
from src.schemas.transcribe import TranscribeRequest, JobResponse
from src.workers.transcript_worker import transcribe_file
from src.services.asr import is_supported_format
from src.config import get_settings
import shutil
from pathlib import Path

router = APIRouter(prefix="/api", tags=["transcribe"])
logger = logging.getLogger(__name__)
settings = get_settings()

# Create uploads directory if it doesn't exist
UPLOAD_DIR = Path("/tmp/lifetext_uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@router.post("/transcribe", response_model=JobResponse)
async def start_transcription(
    file: UploadFile = File(...),
    language: str = "id",
    model_size: str = "base",
    output_format: str = "plain",
    db: Session = Depends(get_db)
):
    """
    Upload a file and start transcription.
    
    Returns job_id for status polling.
    """
    # Validate file
    if not is_supported_format(file.filename):
        raise HTTPException(
            status_code=400,
            detail=f"File format not supported. Supported: MP3, WAV, MP4, MOV, etc."
        )
    
    # Save file
    job_id = str(uuid.uuid4())
    file_path = UPLOAD_DIR / job_id / file.filename
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
    except Exception as e:
        logger.error(f"Error saving file: {str(e)}")
        raise HTTPException(status_code=500, detail="Error saving file")
    
    # Create job record
    job = Job(
        job_id=job_id,
        user_id=settings.development_user_id,
        file_path=str(file_path),
        original_filename=file.filename,
        file_size=file_path.stat().st_size,
        language=language,
        output_format=output_format,
        status=JobStatus.QUEUED
    )
    db.add(job)
    db.commit()
    
    # Enqueue transcription task
    transcribe_file.delay(job_id, str(file_path), model_size, language)
    
    logger.info(f"Transcription job created: {job_id}")
    
    return JobResponse(job_id=job_id, status=JobStatus.QUEUED)
