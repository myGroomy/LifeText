"""Main transcription worker with retry logic."""
import logging
import time
from pathlib import Path
from sqlalchemy.orm import Session
from src.workers.celery_app import celery_app
from src.db import SessionLocal
from src.models import Job, JobStatus
from src.services import asr
from src.services.postprocess import post_process_transcript
from src.services.quality import check_quality

logger = logging.getLogger(__name__)

# Retry configuration
MAX_RETRIES = 2
BACKOFF_FACTOR = 2  # Exponential backoff: 2s, 4s, 8s


@celery_app.task(
    name="transcribe_file",
    autoretry_for=(Exception,),
    retry_kwargs={
        "max_retries": MAX_RETRIES,
        "countdown": 2
    },
    bind=True
)
def transcribe_file(
    self,
    job_id: str,
    file_path: str,
    model_size: str = "base",
    language: str = "id"
):
    """
    Main worker task: transcribe a file.
    
    Pipeline:
    1. Extract audio from video if needed
    2. Transcribe with Whisper (ASR)
    3. Post-process with LLM (cleanup)
    4. Quality check with LLM
    5. Update job in database
    
    Args:
        job_id: UUID of the job
        file_path: Path to media file
        model_size: Whisper model size (tiny, base, small, medium, large)
        language: ISO language code (e.g., 'id', 'en')
    """
    db = SessionLocal()
    try:
        job = db.query(Job).filter(Job.job_id == job_id).first()
        if not job:
            logger.error(f"Job {job_id} not found")
            return
        
        # Mark as processing
        job.status = JobStatus.PROCESSING
        db.commit()
        
        logger.info(f"[{job_id}] Starting transcription (attempt {self.request.retries + 1})")
        
        # ============ STEP 1: Extract Audio ============
        audio_path = file_path
        if asr.is_video_file(file_path):
            logger.info(f"[{job_id}] Extracting audio from video")
            try:
                audio_path = asr.extract_audio(file_path)
                logger.info(f"[{job_id}] Audio extracted successfully")
            except Exception as e:
                logger.error(f"[{job_id}] Audio extraction failed: {str(e)}")
                raise
        
        # ============ STEP 2: Transcribe with Whisper ============
        logger.info(f"[{job_id}] Starting Whisper transcription (model: {model_size})")
        try:
            result = asr.transcribe(
                audio_path,
                model_size=model_size,
                language=language
            )
            raw_transcript = result.get("text", "").strip()
            detected_language = result.get("language", language)
            
            if not raw_transcript:
                raise ValueError("Whisper returned empty transcript")
            
            job.raw_transcript = raw_transcript
            job.language = detected_language
            db.commit()
            
            logger.info(
                f"[{job_id}] Transcription complete "
                f"({len(raw_transcript)} chars, language: {detected_language})"
            )
        except Exception as e:
            logger.error(f"[{job_id}] Whisper transcription failed: {str(e)}")
            raise
        
        # ============ STEP 3: Post-process with LLM ============
        logger.info(f"[{job_id}] Post-processing with LLM")
        try:
            clean_transcript = post_process_transcript(
                raw_transcript=job.raw_transcript,
                language=job.language,
                remove_fillers=True,
                verbatim=False
            )
            
            job.clean_transcript = clean_transcript
            db.commit()
            
            logger.info(f"[{job_id}] Post-processing complete")
        except Exception as e:
            logger.error(f"[{job_id}] Post-processing failed: {str(e)}")
            # Don't fail the job, just use raw transcript
            logger.warning(f"[{job_id}] Using raw transcript as fallback")
            job.clean_transcript = job.raw_transcript
            db.commit()
        
        # ============ STEP 4: Quality Check ============
        logger.info(f"[{job_id}] Running quality check")
        try:
            quality_result = check_quality(job.clean_transcript)
            
            job.quality_score = quality_result["quality_score"]
            job.flag_review = quality_result["flag_review"]
            
            db.commit()
            
            logger.info(
                f"[{job_id}] Quality check complete "
                f"(score: {job.quality_score}, flag_review: {job.flag_review})"
            )
        except Exception as e:
            logger.error(f"[{job_id}] Quality check failed: {str(e)}")
            # Don't fail the job, just use default quality
            logger.warning(f"[{job_id}] Using default quality score")
            job.quality_score = 7  # Default middle score
            job.flag_review = True  # Flag for manual review
            db.commit()
        
        # ============ STEP 5: Mark Complete ============
        job.status = JobStatus.DONE
        job.error_message = None
        db.commit()
        
        logger.info(
            f"[{job_id}] Transcription complete! "
            f"(quality: {job.quality_score}, words: {len(job.clean_transcript.split())})"
        )
        
    except Exception as e:
        logger.error(f"[{job_id}] Worker error: {str(e)}", exc_info=True)
        
        # Update job status
        job.status = JobStatus.FAILED
        job.error_message = f"{type(e).__name__}: {str(e)}"
        db.commit()
        
        # Re-raise for Celery to handle retry
        raise
    
    finally:
        db.close()


@celery_app.task(name="quality_check_job")
def quality_check_job(job_id: str):
    """
    Background task to run quality check on existing job.
    
    Useful for re-checking quality without re-transcribing.
    """
    db = SessionLocal()
    try:
        job = db.query(Job).filter(Job.job_id == job_id).first()
        if not job or not job.clean_transcript:
            logger.warning(f"Job {job_id} not found or has no transcript")
            return
        
        logger.info(f"Running quality check on job {job_id}")
        quality_result = check_quality(job.clean_transcript)
        
        job.quality_score = quality_result["quality_score"]
        job.flag_review = quality_result["flag_review"]
        db.commit()
        
        logger.info(f"Quality check complete for {job_id}")
        
    except Exception as e:
        logger.error(f"Quality check failed for {job_id}: {str(e)}")
    finally:
        db.close()


@celery_app.task(name="reprocess_job")
def reprocess_job(job_id: str, language: str = "id"):
    """
    Background task to reprocess a job.
    
    Re-runs post-processing and quality check without re-transcribing.
    Useful if LLM settings change.
    """
    db = SessionLocal()
    try:
        job = db.query(Job).filter(Job.job_id == job_id).first()
        if not job or not job.raw_transcript:
            logger.warning(f"Job {job_id} not found or has no raw transcript")
            return
        
        logger.info(f"Reprocessing job {job_id}")
        
        # Re-process
        clean_transcript = post_process_transcript(
            raw_transcript=job.raw_transcript,
            language=language,
            remove_fillers=True,
            verbatim=False
        )
        job.clean_transcript = clean_transcript
        
        # Re-check quality
        quality_result = check_quality(clean_transcript)
        job.quality_score = quality_result["quality_score"]
        job.flag_review = quality_result["flag_review"]
        
        db.commit()
        logger.info(f"Reprocessing complete for {job_id}")
        
    except Exception as e:
        logger.error(f"Reprocessing failed for {job_id}: {str(e)}")
    finally:
        db.close()
