# LifeText Setup Guide

## Prerequisites

- Docker & Docker Compose
- Python 3.11+ (for local development)
- API Keys:
  - `CLAUDE_API_KEY` from Anthropic

## Quick Start

### 1. Clone & Setup

```bash
cd LifeText
cp .env.example .env
# Edit .env and add your CLAUDE_API_KEY
```

### 2. Start Services

```bash
# Start all services (PostgreSQL, Redis, API, Worker)
docker-compose up

# In new terminal, init database
docker-compose exec api python scripts/init_db.py
```

### 3. Test API

```bash
# Health check
curl http://localhost:8000/health

# API docs
open http://localhost:8000/docs
```

### 4. Test Transcription

```bash
# Upload a file (MP3, MP4, WAV, etc)
curl -X POST "http://localhost:8000/api/transcribe" \
  -F "file=@audio.mp3" \
  -F "language=id"

# You'll get a job_id in response like:
# {"job_id": "abc-123", "status": "queued"}

# Poll for status
curl "http://localhost:8000/api/jobs/abc-123"
```

## Local Development (Without Docker)

```bash
# Install dependencies
pip install -r requirements.txt

# Terminal 1: Start API
export PYTHONPATH=.
uvicorn src.main:app --reload

# Terminal 2: Start Celery worker
celery -A src.workers.celery_app worker --loglevel=info

# Terminal 3: Start Redis
redis-server

# Terminal 4: Run tests
pytest
```

## Running Tests

```bash
# All tests
pytest

# Specific test file
pytest tests/test_asr.py -v

# With coverage
pytest --cov=src tests/
```

## Project Structure

```
LifeText/
├── README.md                    # Overview
├── SETUP.md                    # This file
├── IMPLEMENTATION_PLAN.md      # Development phases
├── CLAUDE.md                   # Development guidelines
├── requirements.txt            # Python dependencies
├── docker-compose.yml          # Docker services
├── Dockerfile                  # Container config
│
├── src/
│   ├── main.py                 # FastAPI app
│   ├── config.py               # Configuration
│   ├── db.py                   # Database connection
│   │
│   ├── models/
│   │   └── job.py              # Job database model
│   │
│   ├── schemas/
│   │   └── transcribe.py       # Request/Response schemas
│   │
│   ├── services/
│   │   └── asr.py              # Whisper ASR service
│   │
│   ├── routers/
│   │   ├── transcribe.py       # POST /transcribe endpoint
│   │   └── jobs.py             # GET /jobs/{id} endpoint
│   │
│   └── workers/
│       ├── celery_app.py       # Celery configuration
│       └── transcript_worker.py # Main transcription task
│
├── prompts/                    # Claude system prompts
│   ├── system_transcription.txt
│   ├── system_meeting_notes.txt
│   ├── system_interview.txt
│   └── system_qa_chat.txt
│
└── tests/
    ├── test_api.py             # API endpoint tests
    └── test_asr.py             # ASR service tests
```

## API Endpoints (Phase 0 - Currently Available)

### Health Check
```
GET /health
→ {"status": "ok", "environment": "development"}
```

### Start Transcription
```
POST /api/transcribe
Content-Type: multipart/form-data

Parameters:
- file: Audio/video file (MP3, MP4, WAV, etc)
- language: (optional) ISO language code, default "id"
- model_size: (optional) Whisper model (tiny, base, small, medium, large), default "base"
- output_format: (optional) Output format (plain, srt, vtt, json), default "plain"

Response:
{
  "job_id": "uuid-string",
  "status": "queued"
}
```

### Get Job Status
```
GET /api/jobs/{job_id}

Response:
{
  "job_id": "uuid-string",
  "status": "queued|processing|done|failed",
  "language": "id",
  "clean_transcript": "...(only when status=done)",
  "quality_score": 8,
  "flag_review": false,
  "output_format": "plain",
  "error_message": null
}
```

## Troubleshooting

### Docker Issues
```bash
# Rebuild containers
docker-compose down
docker-compose build --no-cache
docker-compose up

# Check logs
docker-compose logs -f api
docker-compose logs -f celery_worker
```

### Database Connection Failed
```bash
# Check PostgreSQL is running
docker-compose logs postgres

# Reinitialize
docker-compose exec api python scripts/init_db.py
```

### Redis Connection Failed
```bash
# Check Redis is running
docker-compose logs redis

# Clear cache
docker-compose exec redis redis-cli FLUSHALL
```

### Whisper Model Too Large
For first run, Whisper will download the model (~1-2 GB). This happens on first transcription.
- Use smaller model: `model_size=tiny` (40 MB) for testing
- Model is cached locally, subsequent runs are faster

## Next Steps

1. **Phase 1 Testing**: 
   - Upload a real audio file (MP3 or MP4)
   - Verify Whisper transcribes correctly
   - Check job polling works

2. **Phase 2: Post-processing**
   - Implement Claude post-processing service
   - Add quality scoring

3. **Phase 3: Intelligence Features**
   - Meeting notes extraction
   - Quote extraction
   - Podcast chapter markers

## Support

- API Documentation: http://localhost:8000/docs
- Check implementation plan: `IMPLEMENTATION_PLAN.md`
- Check guidelines: `CLAUDE.md`
