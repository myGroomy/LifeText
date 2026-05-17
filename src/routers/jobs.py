"""Job status endpoints."""
import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.db import get_db
from src.models import Job
from src.schemas.transcribe import JobStatusResponse

router = APIRouter(prefix="/api", tags=["jobs"])
logger = logging.getLogger(__name__)


@router.get("/jobs/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str, db: Session = Depends(get_db)):
    """
    Get status of a transcription job.
    """
    job = db.query(Job).filter(Job.job_id == job_id).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return JobStatusResponse(
        job_id=job.job_id,
        status=job.status,
        language=job.language,
        clean_transcript=job.clean_transcript,
        quality_score=job.quality_score,
        flag_review=job.flag_review,
        output_format=job.output_format,
        error_message=job.error_message
    )
