"""Automatic Speech Recognition (ASR) service using OpenAI Whisper."""
import subprocess
from pathlib import Path
import whisper
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

# Cache model instance to avoid reloading per request
_model_cache: Dict[str, Any] = {}


def get_whisper_model(model_size: str = "base") -> whisper.Whisper:
    """
    Load and cache Whisper model.
    
    Args:
        model_size: tiny | base | small | medium | large
        
    Returns:
        Cached Whisper model instance
    """
    if model_size not in _model_cache:
        logger.info(f"Loading Whisper model: {model_size}")
        _model_cache[model_size] = whisper.load_model(model_size)
    return _model_cache[model_size]


def extract_audio(video_path: str, output_path: str = "/tmp/extracted_audio.wav") -> str:
    """
    Extract audio from video file using ffmpeg.
    
    Args:
        video_path: Path to video file
        output_path: Path where extracted audio will be saved
        
    Returns:
        Path to extracted audio file
        
    Raises:
        RuntimeError: If ffmpeg extraction fails
    """
    cmd = [
        "ffmpeg",
        "-i", video_path,
        "-vn",                    # no video
        "-acodec", "pcm_s16le",  # WAV format
        "-ar", "16000",          # 16kHz sample rate (Whisper optimal)
        "-ac", "1",              # mono channel
        "-y",                    # overwrite output
        output_path
    ]
    
    logger.info(f"Extracting audio from {video_path}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg error: {result.stderr}")
    
    return output_path


def transcribe(
    audio_path: str,
    model_size: str = "base",
    language: Optional[str] = None,
    task: str = "transcribe"
) -> Dict[str, Any]:
    """
    Transcribe audio file using Whisper.
    
    Args:
        audio_path: Path to audio file
        model_size: tiny | base | small | medium | large
        language: ISO language code (e.g., "id", "en"). None = auto-detect
        task: "transcribe" | "translate" (translate to English)
        
    Returns:
        Result dict with 'text', 'segments', 'language'
    """
    model = get_whisper_model(model_size)
    
    options = {"task": task}
    if language:
        options["language"] = language
    
    logger.info(f"Transcribing {audio_path} with model {model_size}")
    result = model.transcribe(audio_path, **options)
    
    return result


def is_video_file(filepath: str) -> bool:
    """Check if file is a video based on extension."""
    video_ext = {'.mp4', '.mov', '.avi', '.mkv', '.webm', '.ts', '.3gp', '.m4v'}
    ext = Path(filepath).suffix.lower()
    return ext in video_ext


def is_supported_format(filepath: str) -> bool:
    """Check if file format is supported."""
    supported_ext = {
        # Audio
        '.mp3', '.wav', '.m4a', '.aac', '.ogg', '.flac', '.opus', '.wma',
        # Video
        '.mp4', '.mov', '.avi', '.mkv', '.webm', '.ts', '.3gp', '.m4v'
    }
    ext = Path(filepath).suffix.lower()
    return ext in supported_ext


def get_file_duration(filepath: str) -> float:
    """
    Get file duration in seconds using ffprobe.
    
    Args:
        filepath: Path to media file
        
    Returns:
        Duration in seconds
    """
    cmd = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1:0",
        filepath
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        logger.warning(f"Could not determine duration for {filepath}")
        return 0.0
    
    try:
        return float(result.stdout.strip())
    except (ValueError, AttributeError):
        logger.warning(f"Invalid duration output for {filepath}")
        return 0.0
