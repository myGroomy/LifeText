# LifeText - AI-Powered Transcription & Intelligence Platform

Transform audio and video into actionable intelligence. Automatic transcription, LLM post-processing, meeting notes extraction, and more.

**Status**: MVP Complete ✅ | Phase 5 Production Hardening 🔄

---

## 🚀 Quick Start

### Using Docker (Recommended)
```bash
# Clone repository
git clone https://github.com/yourusername/LifeText.git
cd LifeText

# Copy environment template
cp .env.example .env
# Edit .env with your LLM provider credentials

# Start all services
docker-compose up
```

### Local Development
```bash
# Install dependencies
make install

# Start development server
make dev

# Run tests
make test

# Check code quality
make lint
```

---

## 📚 Documentation

All documentation is in the `doc/` folder:

- **[00_START_HERE.md](doc/00_START_HERE.md)** - Quick orientation for your role
- **[QUICK_START.md](doc/QUICK_START.md)** - 5-minute setup guide
- **[COMPLETE_SETUP_GUIDE.md](doc/COMPLETE_SETUP_GUIDE.md)** - Detailed setup with all providers
- **[LLM_CONFIGURATION.md](doc/LLM_CONFIGURATION.md)** - Configure any LLM provider
- **[PRODUCTION_READINESS_ROADMAP.md](doc/PRODUCTION_READINESS_ROADMAP.md)** - Production deployment guide

### Phase Documentation
- **Phase 0-4**: [FINAL_CHECKLIST.md](doc/FINAL_CHECKLIST.md) - MVP completion status
- **Phase 5**: [PHASE_5_TASKS.md](doc/PHASE_5_TASKS.md) - Production hardening tasks

---

## ⚙️ Supported LLM Providers

LifeText works with **any LLM provider**. Switch providers by editing `.env`:

| Provider | Setup | Cost | Notes |
|----------|-------|------|-------|
| **Claude** (Anthropic) | `LLM_PROVIDER=anthropic` | $ | Recommended, best reasoning |
| **GPT-4** (OpenAI) | `LLM_PROVIDER=openai` | $ | Most tested, reliable |
| **Gemini** (Google) | `LLM_PROVIDER=gemini` | $ | Fast, competitive pricing |
| **DeepSeek** | `LLM_PROVIDER=deepseek` | $ | Cheapest option |
| **Ollama** (Local) | `LLM_PROVIDER=openai-compatible` | Free | Run locally, no API key needed |
| **LM Studio** (Local) | `LLM_PROVIDER=openai-compatible` | Free | Desktop GUI, easy setup |

See [LLM_CONFIGURATION.md](doc/LLM_CONFIGURATION.md) for detailed setup.

---

## 🎯 Core Features

### Phase 1: Transcription ✅
- Upload MP3, MP4, WAV, and other audio/video formats
- Automatic speech-to-text using OpenAI Whisper
- Job tracking and status polling

### Phase 2: Post-Processing & Quality ✅
- LLM-based punctuation and grammar correction
- ASR error detection and fixing
- Quality scoring (1-10)
- Flag transcripts needing review

### Phase 3: Intelligence ✅
- Extract meeting notes (decisions, action items, discussion points)
- Extract key quotes with speaker attribution
- Translate transcripts to any language

### Phase 4: Chat ✅
- In-app assistant for questions about transcriptions
- Scoped to LifeText topics

### Phase 5: Production Ready 🔄
- API authentication and rate limiting
- Centralized error tracking
- Monitoring and health checks
- Database migrations and resilience
- Automated deployment

---

## 📊 API Endpoints

### Core Endpoints
```
POST   /api/transcribe              Upload audio/video file
GET    /api/jobs/{id}               Get transcription status
```

### Intelligence Endpoints
```
POST   /api/intelligence/meeting-notes/{id}   Extract meeting notes
POST   /api/intelligence/quotes/{id}          Extract key quotes
POST   /api/intelligence/translate/{id}       Translate transcript
```

### Chat & Status
```
POST   /api/chat                     Ask questions
GET    /health                       Health check
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────┐
│        FastAPI Application      │
├─────────────────────────────────┤
│  • Transcription Endpoints      │
│  • Intelligence Endpoints       │
│  • Chat Endpoint                │
│  • Health Check                 │
└─────────────────────────────────┘
         ↓
┌─────────────────────────────────┐
│    Async Job Queue (Celery)     │
├─────────────────────────────────┤
│  • Whisper Transcription        │
│  • LLM Post-Processing          │
│  • Quality Checking             │
└─────────────────────────────────┘
         ↓
┌─────────────────────────────────┐
│      Persistent Layer           │
├─────────────────────────────────┤
│  • PostgreSQL (job tracking)    │
│  • Redis (job queue)            │
│  • S3 (file storage)            │
└─────────────────────────────────┘
```

---

## 🧪 Testing

```bash
# Run all tests
make test

# Run specific test file
pytest tests/unit/test_asr.py -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run security checks
make security

# Run linting
make lint
```

---

## 🐳 Docker Support

```bash
# Build image
docker build -t lifetext-api:latest .

# Run with Docker Compose
docker-compose up

# Run API only (with external services)
docker run -p 8000:8000 lifetext-api:latest
```

---

## 📋 Development

### Setup
```bash
make install
make setup-db
```

### Development Server
```bash
make dev
# Server runs at http://localhost:8000
# Docs at http://localhost:8000/docs
```

### Code Quality
```bash
make lint      # Run linting
make security  # Run security checks
make test      # Run tests
```

---

## 🚀 Deployment

### Production Checklist
See [PRODUCTION_READINESS_ROADMAP.md](doc/PRODUCTION_READINESS_ROADMAP.md) for:
- Security hardening
- Environment setup
- Deployment procedures
- Monitoring configuration
- Rollback strategy

### Key Files
- `docker-compose.yml` - Local development orchestration
- `Dockerfile` - API container image
- `.github/workflows/` - CI/CD pipelines

---

## 📊 Monitoring & Logging

Production deployment includes:
- **Error Tracking**: Sentry integration
- **Structured Logging**: JSON logs to CloudWatch
- **Health Checks**: System status endpoint
- **Metrics**: Request latency, error rates, queue depth

---

## 🔐 Security

- All endpoints require API key authentication
- Secrets managed via AWS Secrets Manager
- Input validation on all boundaries
- Rate limiting to prevent abuse
- No secrets in code or git history

See `.gitignore` for files that are never committed.

---

## 📈 Performance

- Job processing with exponential backoff retry
- Connection pooling for database resilience
- Caching for frequently accessed data
- Async processing for long-running tasks

---

## 🤝 Contributing

1. Create a feature branch: `git checkout -b feature/my-feature`
2. Commit changes: `git commit -am 'Add feature'`
3. Push to branch: `git push origin feature/my-feature`
4. Open a Pull Request

See [CLAUDE.md](doc/CLAUDE.md) for development guidelines.

---

## 📝 License

[Add your license here]

---

## 📧 Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check documentation in `doc/` folder
- Review API docs at `/docs` endpoint

---

## 🗺️ Roadmap

### Phase 5: Production Hardening (In Progress)
- [ ] API authentication (Phase 5.2)
- [ ] Monitoring & alerting (Phase 5.4)
- [ ] Database migrations (Phase 5.5)
- [ ] Automated deployment (Phase 5.6)

### Phase 6: Multi-User (Future)
- User registration & login
- Per-user API key management
- Organizations/teams
- Role-based access control
- Usage analytics & billing

---

## 📚 Additional Resources

- [Complete Setup Guide](doc/COMPLETE_SETUP_GUIDE.md)
- [LLM Configuration Guide](doc/LLM_CONFIGURATION.md)
- [Phase 5 Tasks](doc/PHASE_5_TASKS.md)
- [Implementation Plan](doc/IMPLEMENTATION_PLAN_v2.md)

---

**Built with ❤️ using FastAPI, Whisper, and LLMs**
