# LifeText Development Guidelines

Project-specific guidelines untuk development LifeText SaaS.

## Tech Stack

- **Backend**: FastAPI + Python 3.11
- **Database**: PostgreSQL 16
- **Queue/Cache**: Redis + Celery
- **ASR**: OpenAI Whisper
- **LLM**: Claude (Anthropic API)
- **Testing**: pytest + pytest-asyncio
- **Containerization**: Docker Compose

## Commands

```bash
# Development
npm run dev          # Start all services locally (requires Docker)
npm run api          # Run API server only
npm run worker       # Run Celery worker
npm run test         # Run test suite
npm run lint         # Type checking
npm run db:init      # Initialize database

# Production
npm run build        # Build Docker images
npm run migrate      # Run migrations
```

**Actual commands:**
```bash
docker-compose up                          # All services
python -m src.main                         # API (local)
celery -A src.workers.celery_app worker   # Worker
pytest                                     # Tests
python scripts/init_db.py                 # Init DB
```

## Project Structure

```
LifeText/
├── src/
│   ├── main.py                 # FastAPI app
│   ├── config.py               # Configuration
│   ├── db.py                   # Database
│   ├── models/job.py           # Job model
│   ├── schemas/                # Request/Response schemas
│   ├── services/
│   │   ├── asr.py              # Whisper service
│   │   ├── postprocess.py      # Claude post-processing
│   │   └── quality.py          # Quality checking
│   ├── routers/
│   │   ├── transcribe.py       # Upload endpoint
│   │   └── jobs.py             # Status polling
│   └── workers/
│       ├── celery_app.py       # Celery config
│       └── transcript_worker.py # Main worker
├── prompts/                    # Claude system prompts
├── tests/                      # Test suite
└── docker-compose.yml
```

## Code Conventions

### File Structure
- One class/concept per file
- Services for business logic
- Schemas for validation
- Routers for endpoints

### Naming
- Functions: snake_case
- Classes: PascalCase
- Constants: UPPER_SNAKE
- Private: _leading_underscore

### Async/Await
- API handlers: async
- Workers: sync (Celery handles async)
- Services: sync (let caller decide async)

### Error Handling
- Custom exceptions inherit from Exception
- Log errors with context
- Return HTTP errors with proper status codes
- Never expose internal details to API

## Boundaries

### Always Do
- Load prompts from `prompts/` directory, not hardcode
- Use dependency injection for db session
- Validate input at API boundary
- Log important events (job start, completion, errors)
- Cache Whisper model instance
- Use parameterized database queries

### Ask First
- Adding new services or major components
- Changing database schema
- Adding new dependencies
- Changing Claude API calls or prompts
- Modifying error handling strategy

### Never Do
- Hardcode prompts in Python code
- Use f-strings for SQL queries
- Store secrets in code
- Commit .env files
- Call LLM synchronously from API (use Celery)
- Assume file formats without validation

## Testing Strategy

- **Unit tests**: Services, schemas
- **Integration tests**: API endpoints
- **Test pattern**: Arrange-Act-Assert
- **Naming**: `test_<function>_<scenario>`
- **Coverage target**: 80%

## Development Workflow

1. **Start with spec** - Define inputs, outputs, acceptance criteria
2. **Write failing test** - Prove the behavior you want
3. **Implement** - Make the test pass
4. **Refactor** - Simplify while keeping tests green
5. **Verify** - Run full test suite, build, type check

Example:
```
Task: Add language detection to transcription
  1. Write test: test_transcribe_detects_language()
  2. Implement: asr.transcribe() detects language
  3. Verify: pytest passes
```

## Prompts Location and Loading

All prompts are in `prompts/` directory as `.txt` files:
- `system_transcription.txt` - Core transcription
- `system_meeting_notes.txt` - Meeting intelligence
- `system_interview.txt` - Interview/podcast mode
- `system_qa_chat.txt` - In-app assistant

Load with: `Path("prompts/system_transcription.txt").read_text()`

Never hardcode prompts in Python files.
