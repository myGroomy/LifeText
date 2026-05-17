"""Intelligence endpoints for smart features."""
import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.db import get_db
from src.models import Job, JobStatus
from src.services.postprocess import (
    generate_meeting_notes,
    extract_quotes,
    translate_transcript
)

router = APIRouter(prefix="/api", tags=["intelligence"])
logger = logging.getLogger(__name__)


@router.post("/intelligence/meeting-notes/{job_id}")
async def create_meeting_notes(
    job_id: str,
    metadata: dict = None,
    db: Session = Depends(get_db)
):
    """
    Generate meeting notes from transcript.
    
    Args:
        job_id: Job ID with completed transcript
        metadata: Optional metadata (date, participants, type)
    """
    job = db.query(Job).filter(Job.job_id == job_id).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job.status != JobStatus.DONE:
        raise HTTPException(
            status_code=400,
            detail=f"Job not ready. Current status: {job.status}"
        )
    
    if not job.clean_transcript:
        raise HTTPException(
            status_code=400,
            detail="No transcript available"
        )
    
    logger.info(f"Generating meeting notes for job {job_id}")
    
    notes = generate_meeting_notes(
        transcript=job.clean_transcript,
        metadata=metadata or {}
    )
    
    return {
        "job_id": job_id,
        "mode": "meeting_notes",
        "output": notes
    }


@router.post("/intelligence/quotes/{job_id}")
async def extract_key_quotes(
    job_id: str,
    count: int = 5,
    db: Session = Depends(get_db)
):
    """
    Extract key quotes from transcript.
    
    Args:
        job_id: Job ID with completed transcript
        count: Number of quotes to extract (5-10)
    """
    job = db.query(Job).filter(Job.job_id == job_id).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job.status != JobStatus.DONE:
        raise HTTPException(
            status_code=400,
            detail=f"Job not ready. Current status: {job.status}"
        )
    
    if not job.clean_transcript:
        raise HTTPException(
            status_code=400,
            detail="No transcript available"
        )
    
    logger.info(f"Extracting quotes for job {job_id}")
    
    quotes = extract_quotes(
        transcript=job.clean_transcript,
        count=min(10, max(5, count))  # Clamp to 5-10
    )
    
    return {
        "job_id": job_id,
        "mode": "quotes",
        "output": quotes
    }


@router.post("/intelligence/translate/{job_id}")
async def translate_job_transcript(
    job_id: str,
    target_language: str,
    db: Session = Depends(get_db)
):
    """
    Translate transcript to another language.
    
    Args:
        job_id: Job ID with completed transcript
        target_language: Target language code (e.g., "en", "id", "es")
    """
    job = db.query(Job).filter(Job.job_id == job_id).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job.status != JobStatus.DONE:
        raise HTTPException(
            status_code=400,
            detail=f"Job not ready. Current status: {job.status}"
        )
    
    if not job.clean_transcript:
        raise HTTPException(
            status_code=400,
            detail="No transcript available"
        )
    
    logger.info(f"Translating job {job_id} to {target_language}")
    
    translated = translate_transcript(
        transcript=job.clean_transcript,
        source_language=job.language or "id",
        target_language=target_language
    )
    
    return {
        "job_id": job_id,
        "mode": "translate",
        "source_language": job.language,
        "target_language": target_language,
        "output": translated
    }
