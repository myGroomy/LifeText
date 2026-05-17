"""Schemas for transcription endpoints."""
from pydantic import BaseModel, Field
from typing import Optional


class TranscribeRequest(BaseModel):
    """Request to start a transcription job."""
    language: Optional[str] = Field(None, description="ISO language code (e.g., 'id', 'en')")
    model_size: str = Field("base", description="Whisper model size")
    output_format: str = Field("plain", description="Output format: plain, srt, vtt, json")


class JobResponse(BaseModel):
    """Response for job creation."""
    job_id: str
    status: str


class JobStatusResponse(BaseModel):
    """Response for job status query."""
    job_id: str
    status: str
    language: Optional[str] = None
    clean_transcript: Optional[str] = None
    quality_score: Optional[int] = None
    flag_review: bool = False
    output_format: str
    error_message: Optional[str] = None


class IntelligenceRequest(BaseModel):
    """Request for intelligence features."""
    job_id: str
    mode: str = Field("meeting_notes", description="meeting_notes, quotes, translate, etc")
    options: Optional[dict] = None
