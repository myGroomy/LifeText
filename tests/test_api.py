"""Tests for API endpoints."""
import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.db import get_db, SessionLocal


@pytest.fixture
def client():
    """FastAPI test client."""
    return TestClient(app)


class TestHealth:
    """Test health check endpoint."""
    
    def test_health_check(self, client):
        """Test health check returns ok."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"
    
    def test_root_endpoint(self, client):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "LifeText API"
        assert "version" in data


class TestTranscribeEndpoint:
    """Test transcribe endpoint."""
    
    def test_transcribe_unsupported_format(self, client):
        """Test upload with unsupported file format."""
        response = client.post(
            "/api/transcribe",
            files={"file": ("document.pdf", b"PDF content", "application/pdf")}
        )
        assert response.status_code == 400
    
    def test_transcribe_mp3(self, client):
        """Test MP3 file upload."""
        # Create a minimal MP3-like file
        response = client.post(
            "/api/transcribe",
            files={"file": ("audio.mp3", b"ID3", "audio/mpeg")},
            params={"language": "id", "model_size": "base"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "job_id" in data
        assert data["status"] == "queued"
