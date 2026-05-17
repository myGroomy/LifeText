# LifeText - AI Transcript SaaS MVP

Platform transkripsi audio/video berbasis AI untuk profesional dengan standar akurasi tinggi.

## Fitur

- **Transkripsi Audio/Video** - Gunakan Whisper untuk ASR, Claude untuk post-processing
- **Smart Meeting Notes** - Extract action items, key decisions dari meeting
- **Multiple Output Formats** - Plain text, SRT, VTT, JSON
- **Quality Control** - Automated quality scoring dan flagging untuk review
- **Async Job Processing** - Celery workers untuk file processing

## Tech Stack

- **Backend**: FastAPI + Python 3.11
- **Database**: PostgreSQL 16
- **Cache/Queue**: Redis + Celery
- **ASR**: OpenAI Whisper
- **LLM**: Claude (Anthropic API)
- **Containerization**: Docker Compose

## Quick Start

### Setup

```bash
# Copy environment
cp .env.example .env

# Start services (requires Docker)
docker-compose up -d

# Install dependencies
pip install -r requirements.txt

# Initialize database
python -m scripts.init_db

# Run tests
pytest
```

### Local Development

```bash
# Terminal 1: API server
uvicorn src.main:app --reload

# Terminal 2: Celery worker
celery -A src.workers.celery_app worker --loglevel=info

# Terminal 3: Redis (if not using Docker)
redis-server
```

## Project Structure

```
LifeText/
├── src/
│   ├── main.py                 # FastAPI app
│   ├── config.py               # Configuration
│   ├── db.py                   # Database setup
│   ├── models/
│   │   └── job.py              # Job model
│   ├── schemas/
│   │   └── transcribe.py       # Request/Response schemas
│   ├── services/
│   │   ├── asr.py              # Whisper ASR service
│   │   ├── postprocess.py      # Claude post-processing
│   │   └── quality.py          # Quality checking
│   ├── routers/
│   │   ├── transcribe.py       # Upload endpoint
│   │   └── jobs.py             # Status polling
│   ├── workers/
│   │   ├── celery_app.py       # Celery setup
│   │   └── transcript_worker.py # Main worker
│   └── utils/
│       └── errors.py           # Error handling
├── prompts/                    # Claude system prompts
│   ├── system_transcription.txt
│   ├── system_meeting_notes.txt
│   ├── system_interview.txt
│   └── system_qa_chat.txt
├── tests/
│   ├── test_asr.py
│   ├── test_postprocess.py
│   └── test_api.py
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

## API Endpoints

- `POST /transcribe` - Upload file untuk transkripsi
- `GET /jobs/{job_id}` - Polling status
- `POST /intelligence` - Smart features (meeting notes, dll)
- `POST /chat` - In-app assistant

## Development Phases

1. **Phase 0**: Setup ✅
2. **Phase 1**: ASR Service 🔄
3. **Phase 2**: Post-process & Quality
4. **Phase 3**: Job System
5. **Phase 4**: Intelligence Endpoints
6. **Phase 5**: In-App Chat
