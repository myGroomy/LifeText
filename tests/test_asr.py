"""Tests for ASR service."""
import pytest
from pathlib import Path
from src.services import asr


class TestFormatDetection:
    """Test file format detection."""
    
    def test_is_supported_format_mp3(self):
        """Test MP3 is supported."""
        assert asr.is_supported_format("audio.mp3")
    
    def test_is_supported_format_mp4(self):
        """Test MP4 is supported."""
        assert asr.is_supported_format("video.mp4")
    
    def test_is_supported_format_unsupported(self):
        """Test unsupported format returns False."""
        assert not asr.is_supported_format("document.pdf")
    
    def test_is_video_file_mp4(self):
        """Test MP4 is detected as video."""
        assert asr.is_video_file("video.mp4")
    
    def test_is_video_file_mp3(self):
        """Test MP3 is not detected as video."""
        assert not asr.is_video_file("audio.mp3")


class TestWhisperModel:
    """Test Whisper model loading."""
    
    def test_get_whisper_model_base(self):
        """Test loading base model."""
        model = asr.get_whisper_model("base")
        assert model is not None
    
    def test_get_whisper_model_caching(self):
        """Test model caching."""
        model1 = asr.get_whisper_model("base")
        model2 = asr.get_whisper_model("base")
        assert model1 is model2  # Same instance
