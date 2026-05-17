# LifeText Complete Setup Guide

Complete Phase 0-5 MVP with any LLM provider. Fully implemented and ready to test!

## Table of Contents

1. [Quick Start (5 minutes)](#quick-start)
2. [Choose Your LLM Provider](#choose-your-llm-provider)
3. [Detailed Setup](#detailed-setup)
4. [Run Tests](#run-tests)
5. [API Endpoints Reference](#api-endpoints-reference)
6. [Troubleshooting](#troubleshooting)

---

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.11+ (for local development)
- One of: OpenAI API key, Gemini API key, Ollama installed, etc

### 30-Second Setup

```bash
cd LifeText

# 1. Copy config for your LLM provider
cp .env.claude-example .env          # or .env.openai-example, .env.ollama-example, etc
# Edit .env with your API key

# 2. Start services
docker-compose up -d
sleep 5

# 3. Init database
docker-compose exec api python scripts/init_db.py

# 4. Test
curl http://localhost:8000/health
# Should return: {"status": "ok", "environment": "development"}

# Done! API is running at http://localhost:8000
# Docs at http://localhost:8000/docs
```

---

## Choose Your LLM Provider

### Option 1: Claude (Anthropic) ⭐ RECOMMENDED

**Best for:** Production, balanced cost/quality, recommended default

```bash
cp .env.claude-example .env
# Edit .env: add your API key from console.anthropic.com
```

- Cost: $3 per 1M input, $15 per 1M output tokens
- Quality: ⭐⭐⭐⭐
- Speed: ⭐⭐⭐⭐
- Recommended for: Most use cases

### Option 2: OpenAI (GPT-4)

**Best for:** Highest quality, most tested

```bash
cp .env.openai-example .env
# Edit .env: add your API key from platform.openai.com
```

- Cost: $30 per 1M input, $60 per 1M output tokens (expensive!)
- Quality: ⭐⭐⭐⭐⭐
- Speed: ⭐⭐⭐⭐
- Recommended for: Mission-critical applications

### Option 3: Gemini (Google)

**Best for:** Fast, competitive pricing, multimodal support

```bash
cp .env.gemini-example .env
# Edit .env: add your API key from aistudio.google.com
```

- Cost: $0.50 per 1M input, $1.50 per 1M output tokens
- Quality: ⭐⭐⭐⭐
- Speed: ⭐⭐⭐⭐⭐ (fastest)
- Recommended for: Speed-critical, cost-conscious

### Option 4: DeepSeek

**Best for:** Budget, high volume

```bash
cp .env.deepseek-example .env
# Edit .env: add your API key from platform.deepseek.com
```

- Cost: $0.10 per 1M input, $0.30 per 1M output tokens (CHEAPEST!)
- Quality: ⭐⭐⭐
- Speed: ⭐⭐⭐⭐
- Recommended for: Budget-conscious, high volume

### Option 5: Ollama (Local, FREE!) 🎁

**Best for:** Development, privacy, no internet needed

```bash
# First, install Ollama from ollama.ai
# Then:
ollama serve  # In one terminal

# In another terminal:
cd LifeText
cp .env.ollama-example .env
# .env already configured for Ollama
```

- Cost: FREE (just hardware)
- Quality: ⭐⭐⭐ (good for development)
- Speed: Depends on GPU
- Recommended for: Development, testing, privacy-critical

### Option 6: LM Studio (Local, FREE!)

**Best for:** GUI-based local development

```bash
# Install from lmstudio.ai
# Load a model, start server

cd LifeText
cp .env.lmstudio-example .env
# .env already configured for LM Studio
```

- Cost: FREE
- Quality: ⭐⭐⭐
- Speed: Depends on GPU
- Recommended for: Developers who prefer GUI

---

## Detailed Setup

### Step 1: Clone/Download LifeText

```bash
# You should already have LifeText folder
cd LifeText
ls -la  # Should see src/, prompts/, docker-compose.yml, etc
```

### Step 2: Choose and Configure LLM Provider

```bash
# See "Choose Your LLM Provider" section above
# Pick one provider and copy its config:

# Example: Using Claude (recommended)
cp .env.claude-example .env

# Edit .env and add your API key
nano .env  # or vi, VSCode, etc
# Look for LLM_API_KEY and paste your key
```

### Step 3: Verify Configuration

```bash
# Check .env is valid
cat .env | grep LLM_

# Should see:
# LLM_PROVIDER=anthropic
# LLM_API_KEY=sk-ant-xxxxx
# LLM_MODEL=claude-sonnet-4-20250514
# (or your chosen provider's config)
```

### Step 4: Install Python Dependencies

```bash
# If running locally (not Docker):
pip install -r requirements.txt

# If using Docker, skip this (dependencies installed in container)
```

### Step 5: Start Docker Services

```bash
# Start all services (PostgreSQL, Redis, API, Worker)
docker-compose up -d

# Wait for services to be healthy
sleep 5

# Check status
docker-compose ps
# Should show all services as "up"
```

### Step 6: Initialize Database

```bash
# Create database tables
docker-compose exec api python scripts/init_db.py

# Expected output:
# Initializing database...
# ✅ Database initialized successfully!
# Tables created:
#   - jobs
```

### Step 7: Test Health Check

```bash
# Check API is responding
curl http://localhost:8000/health

# Expected response:
# {"status":"ok","environment":"development"}

# View API documentation
open http://localhost:8000/docs
# Or: http://localhost:8000/docs in browser
```

### Step 8: Test Transcription (Phase 1)

```bash
# Upload an audio file (MP3, MP4, WAV, etc)
JOB_ID=$(curl -s -X POST "http://localhost:8000/api/transcribe" \
  -F "file=@your_audio.mp3" | jq -r '.job_id')

echo "Job ID: $JOB_ID"

# Poll for result (wait for status = "done")
for i in {1..30}; do
  STATUS=$(curl -s "http://localhost:8000/api/jobs/$JOB_ID" | jq -r '.status')
  SCORE=$(curl -s "http://localhost:8000/api/jobs/$JOB_ID" | jq -r '.quality_score')
  echo "[$i/30] Status: $STATUS, Quality: $SCORE"
  [ "$STATUS" = "done" ] && break
  sleep 2
done

# View final result
curl "http://localhost:8000/api/jobs/$JOB_ID" | jq '.'
```

### Step 9: Test Intelligence Features (Phase 3)

```bash
# Assuming job_id from step 8

# Get meeting notes
curl "http://localhost:8000/api/intelligence/meeting-notes/$JOB_ID" | jq '.output'

# Get key quotes
curl "http://localhost:8000/api/intelligence/quotes/$JOB_ID?count=5" | jq '.output'

# Translate transcript
curl "http://localhost:8000/api/intelligence/translate/$JOB_ID?target_language=en" | jq '.output'
```

### Step 10: Test Chat (Phase 4)

```bash
# Ask LifeText a question
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "What file formats do you support?"}' | jq '.response'

# Try off-topic question (should refuse)
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Tell me a joke"}' | jq '.response'
```

---

## Run Tests

### Full Test Suite

```bash
# Run all tests
docker-compose exec api pytest -v

# Expected output:
# tests/test_api.py::TestHealth::test_health_check PASSED
# tests/test_api.py::TestTranscribeEndpoint::test_transcribe_mp3 PASSED
# ...
# ======================== X passed in Ys ========================
```

### Run Specific Tests

```bash
# Test API only
docker-compose exec api pytest tests/test_api.py -v

# Test ASR only
docker-compose exec api pytest tests/test_asr.py -v

# Test with coverage
docker-compose exec api pytest --cov=src tests/
```

---

## API Endpoints Reference

### Health & Info

```bash
# Health check
GET /health
→ {"status": "ok", "environment": "development"}

# Root endpoint
GET /
→ {"name": "LifeText API", "version": "0.1.0", "docs": "/docs"}
```

### Transcription (Phase 1)

```bash
# Upload file and start transcription
POST /api/transcribe
  Params:
    - file: Audio/video file (required)
    - language: ISO code, default "id" (optional)
    - model_size: tiny/base/small/medium/large, default "base" (optional)
    - output_format: plain/srt/vtt/json, default "plain" (optional)
  
  Response:
    {
      "job_id": "uuid",
      "status": "queued"
    }

# Get job status and transcript
GET /api/jobs/{job_id}
  Response:
    {
      "job_id": "uuid",
      "status": "queued|processing|done|failed",
      "language": "id",
      "clean_transcript": "Cleaned text here..." (only when done),
      "quality_score": 8,
      "flag_review": false,
      "output_format": "plain",
      "error_message": null
    }
```

### Intelligence Features (Phase 3)

```bash
# Extract meeting notes
POST /api/intelligence/meeting-notes/{job_id}
  Params:
    - metadata: Optional dict with date, participants, type
  Response:
    {
      "job_id": "uuid",
      "mode": "meeting_notes",
      "output": "## Meeting Overview...\n## Key Decisions..."
    }

# Extract quotes
POST /api/intelligence/quotes/{job_id}?count=5
  Response:
    {
      "job_id": "uuid",
      "mode": "quotes",
      "output": "> \"Quote here\"\n— Speaker Name\n\n> \"Another quote\"..."
    }

# Translate transcript
POST /api/intelligence/translate/{job_id}?target_language=en
  Response:
    {
      "job_id": "uuid",
      "mode": "translate",
      "source_language": "id",
      "target_language": "en",
      "output": "Translated text here..."
    }
```

### Chat (Phase 4)

```bash
# Chat with assistant
POST /api/chat
  Body:
    {
      "message": "How do I upload a file?"
    }
  Response:
    {
      "response": "You can upload audio or video files..."
    }
```

---

## Troubleshooting

### Services Won't Start

```bash
# Full reset
docker-compose down -v
docker-compose build --no-cache
docker-compose up

# Check logs
docker-compose logs -f api
docker-compose logs -f postgres
docker-compose logs -f redis
```

### Database Connection Error

```bash
# Reinitialize database
docker-compose exec api python scripts/init_db.py

# Or if container not running:
docker-compose exec -T api python scripts/init_db.py
```

### LLM API Key Error

```bash
# Check .env has correct key
cat .env | grep LLM_

# Verify it's correct:
# - OpenAI: starts with "sk-proj-"
# - Claude: starts with "sk-ant-"
# - Gemini: long string from aistudio.google.com
# - DeepSeek: starts with "sk-"
# - Ollama: can be anything (local)
```

### Whisper Too Slow

```bash
# First transcription downloads model (~1-2 GB)
# Subsequent requests use cached model and are faster

# Use smaller model for faster testing
# Edit .env: WHISPER_MODEL_SIZE=tiny

# Restart
docker-compose restart api
docker-compose restart celery_worker
```

### "Module not found" Error

```bash
# Install missing LLM provider package
# Based on your LLM_PROVIDER:

# OpenAI
pip install openai

# Claude
pip install anthropic

# Gemini
pip install google-generativeai

# Or rebuild Docker image
docker-compose build --no-cache api
```

### Jobs Stuck in "processing"

```bash
# Check worker logs
docker-compose logs -f celery_worker

# Restart worker
docker-compose restart celery_worker

# Check Redis is running
docker-compose logs redis
```

### Port Already in Use

```bash
# Change port in docker-compose.yml
# Find: ports: - "8000:8000"
# Change to: ports: - "8001:8000"

# Then access at http://localhost:8001
```

---

## Next Steps

### After Basic Setup Works

1. **Test with real files** - Try different audio/video formats
2. **Test each phase** - Verify transcription, post-processing, quality check
3. **Switch LLM providers** - Try different providers by editing .env
4. **Load testing** - Upload multiple files, test performance
5. **Production setup** - Add authentication, setup S3 storage, etc

### Going to Production

1. Read `Phase 5: Production Hardening` in IMPLEMENTATION_PLAN_v2.md
2. Add user authentication
3. Setup S3 for file storage
4. Configure monitoring/alerting
5. Load test and optimize
6. Deploy to production environment

---

## Support

- **API Docs**: http://localhost:8000/docs
- **LLM Setup**: See `LLM_CONFIGURATION.md`
- **Implementation**: See `IMPLEMENTATION_PLAN_v2.md`
- **Development**: See `CLAUDE.md`
- **Project Overview**: See `PROJECT_SUMMARY.md`

---

## Example Complete Workflow

```bash
# 1. Setup (one time)
cd LifeText
cp .env.claude-example .env
# Add API key to .env
docker-compose up -d
docker-compose exec api python scripts/init_db.py

# 2. Upload file
JOB=$(curl -s -X POST http://localhost:8000/api/transcribe \
  -F "file=@meeting.mp3" | jq -r '.job_id')

# 3. Wait for completion
sleep 10  # Give it time to process

# 4. Get results
curl http://localhost:8000/api/jobs/$JOB | jq '.'

# 5. Get intelligence
curl http://localhost:8000/api/intelligence/meeting-notes/$JOB | jq '.output'

# 6. Get quotes
curl http://localhost:8000/api/intelligence/quotes/$JOB | jq '.output'

# 7. Chat
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What quality was my transcript?"}' | jq '.response'
```

---

**🎉 LifeText MVP is ready to use with ANY LLM provider!**

Choose your provider, follow setup, and start transcribing!
