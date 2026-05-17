# LifeText - Quick Start (5 minutes)

## 1. Setup Environment

```bash
cd LifeText
cp .env.example .env
```

Edit `.env`:
```
CLAUDE_API_KEY=sk-ant-xxxxx  # Add your Anthropic API key
```

## 2. Start Services

```bash
docker-compose up
```

Wait for all services to be healthy:
- ✅ postgres - ready
- ✅ redis - ready
- ✅ api - running on :8000
- ✅ celery_worker - ready

## 3. Initialize Database (in another terminal)

```bash
docker-compose exec api python scripts/init_db.py
```

## 4. Test the API

### Health Check
```bash
curl http://localhost:8000/health
```

Should return:
```json
{"status": "ok", "environment": "development"}
```

### Browse API Docs
```
http://localhost:8000/docs
```

### Upload a File for Transcription

```bash
# Upload an MP3 or MP4 file
curl -X POST "http://localhost:8000/api/transcribe" \
  -F "file=@your_audio.mp3" \
  -F "language=id"
```

Response (save job_id):
```json
{"job_id": "abc-123-def-456", "status": "queued"}
```

### Check Transcription Status

```bash
curl "http://localhost:8000/api/jobs/abc-123-def-456"
```

Response:
```json
{
  "job_id": "abc-123-def-456",
  "status": "processing",
  "language": "id",
  "clean_transcript": null,
  "quality_score": null,
  "flag_review": false,
  "output_format": "plain",
  "error_message": null
}
```

Poll again until status becomes `"done"`:
```json
{
  "job_id": "abc-123-def-456",
  "status": "done",
  "language": "id",
  "clean_transcript": "Transcribed text here...",
  "quality_score": 8,
  "flag_review": false,
  "output_format": "plain",
  "error_message": null
}
```

## 5. Run Tests

```bash
docker-compose exec api pytest -v
```

## 6. View Logs

```bash
# API logs
docker-compose logs -f api

# Worker logs
docker-compose logs -f celery_worker

# Database logs
docker-compose logs -f postgres
```

## Project Structure

```
LifeText/
├── src/              # Application code
├── prompts/          # Claude system prompts
├── tests/            # Test suite
└── [documentation]   # README, SETUP, etc
```

## Common Commands

| Task | Command |
|------|---------|
| Start all services | `docker-compose up` |
| Stop services | `docker-compose down` |
| View logs | `docker-compose logs -f api` |
| Run tests | `docker-compose exec api pytest` |
| Init database | `docker-compose exec api python scripts/init_db.py` |
| Shell in container | `docker-compose exec api bash` |
| Rebuild containers | `docker-compose build --no-cache` |

## Troubleshooting

**Services won't start?**
```bash
docker-compose down -v
docker-compose up --build
```

**Database connection error?**
```bash
docker-compose logs postgres
docker-compose exec api python scripts/init_db.py
```

**Tests failing?**
```bash
docker-compose exec api pytest -v
```

**Whisper slow on first run?**
It downloads the model on first transcription (~1-2 GB). This is normal.

## What's Next?

1. Read `PROJECT_SUMMARY.md` for full project overview
2. Read `IMPLEMENTATION_PLAN.md` for development phases
3. Read `CLAUDE.md` for coding guidelines
4. Test Phase 1 with a real audio file

## Files Reference

- 📖 **README.md** - Project overview
- 🚀 **SETUP.md** - Detailed setup guide
- 📋 **IMPLEMENTATION_PLAN.md** - Phase breakdown
- 💻 **CLAUDE.md** - Development guidelines
- 📊 **PROJECT_SUMMARY.md** - What was built

---

**Phase 0: Setup** ✅ DONE

Ready for Phase 1: ASR Service testing!
