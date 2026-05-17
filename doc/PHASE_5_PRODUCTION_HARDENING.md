# Phase 5: Production Hardening — Complete Specification

**Status**: SPECIFICATION PHASE  
**Last Updated**: 2025-05-17  
**Version**: 1.0.0

---

## ASSUMPTIONS I'M MAKING

Before proceeding with implementation, please verify these assumptions:

1. **Deployment Target**: Single-server deployment initially (cloud VM or managed container service)
2. **Auth Approach**: Simple API key-based auth for MVP (not full OAuth2/OIDC yet)
3. **File Storage**: AWS S3 for production file storage (local /tmp for MVP testing)
4. **Database**: PostgreSQL managed database (AWS RDS, Supabase, or Neon)
5. **Monitoring**: Basic error tracking (Sentry) + CloudWatch/app logs
6. **User Base**: Single-user MVP initially (dev_user_id), multi-user in Phase 6
7. **Scale**: <100 concurrent users, <1000 jobs/day for initial production
8. **SLA**: No strict SLA requirement for MVP; best-effort availability
9. **Data Retention**: Keep all transcripts and jobs (no deletion policy yet)
10. **Compliance**: No GDPR/HIPAA requirements for MVP

→ **Correct me now if any of these don't match your intent.**

---

## OBJECTIVE

Transition LifeText MVP from development-ready to **production-safe**:

- Handle failures gracefully without data loss
- Monitor for problems before users see them
- Maintain security (secrets, input validation, error handling)
- Scale from 1 to 100+ concurrent users
- Recover from infrastructure failures
- Log and debug issues in production environment
- Deploy safely with rollback capability

**Success Criteria:**
- ✅ Zero secrets in code or git history
- ✅ All errors logged and tracked
- ✅ API rate-limited to prevent abuse
- ✅ File uploads validated and scanned
- ✅ Database connections pooled and resilient
- ✅ Monitoring dashboards show key metrics
- ✅ Can rollback any deployment in <5 minutes
- ✅ Can scale horizontally (add more API servers)
- ✅ Can handle 24-hour operation without manual intervention

---

## TECH STACK

```
Application:
  ├── FastAPI (already in place)
  ├── Pydantic (validation, already in place)
  ├── SQLAlchemy + Alembic (database + migrations)
  └── Celery + Redis (async tasks, already in place)

Infrastructure:
  ├── Docker + Docker Compose (local/staging)
  ├── Docker + ECS/K8s (production)
  └── PostgreSQL managed database

Monitoring:
  ├── Sentry (error tracking)
  ├── CloudWatch (logs, metrics)
  ├── Prometheus (optional: application metrics)
  └── Grafana (optional: dashboards)

Secrets:
  ├── AWS Secrets Manager OR HashiCorp Vault
  ├── Environment variables for prod
  └── .env files for dev/staging

Storage:
  ├── AWS S3 (production files)
  ├── Local /tmp (MVP testing)
  └── Backup strategy for database

Security:
  ├── API authentication (API keys or JWT)
  ├── Rate limiting (per IP, per user)
  ├── File validation (type, size, virus scan)
  ├── SQL injection prevention (already using ORM)
  └── XSS prevention (API-only, no HTML rendering)
```

---

## COMMANDS

```bash
# Development
npm run dev              # (N/A — using Python/Celery)
uvicorn src.main:app --reload  # FastAPI dev server

# Testing
pytest tests/           # Run all tests
pytest --cov           # With coverage

# Building
docker build -t lifetext-api:latest .
docker build -t lifetext-worker:latest -f Dockerfile.worker .

# Deployment
docker push lifetext-api:latest
docker push lifetext-worker:latest

# Migrations
alembic upgrade head    # Apply migrations
alembic downgrade -1    # Rollback last migration

# Monitoring
# (See deployment section for CloudWatch/Sentry setup)
```

---

## PROJECT STRUCTURE

**Current (after Phase 0-4):**
```
LifeText/
├── src/
│   ├── main.py                    # FastAPI app
│   ├── config.py                  # Configuration
│   ├── db.py                      # Database setup
│   ├── models/
│   │   └── job.py                 # Job model
│   ├── schemas/
│   │   └── transcribe.py          # Request/response schemas
│   ├── services/
│   │   ├── asr.py                 # Whisper
│   │   ├── llm_provider.py        # LLM abstraction
│   │   ├── postprocess.py         # Post-processing
│   │   └── quality.py             # Quality checking
│   ├── routers/
│   │   ├── transcribe.py          # Upload endpoint
│   │   ├── jobs.py                # Status endpoint
│   │   ├── intelligence.py        # Intelligence endpoints
│   │   └── chat.py                # Chat endpoint
│   └── workers/
│       ├── celery_app.py          # Celery config
│       └── transcript_worker.py   # Worker tasks
├── docker-compose.yml             # Local orchestration
├── Dockerfile                     # API container
├── requirements.txt               # Python deps
├── pytest.ini                     # Test config
├── tests/                         # Tests
├── prompts/                       # System prompts
├── scripts/
│   └── init_db.py                 # DB initialization
└── docs/
    └── ...                        # Documentation
```

**New (Phase 5 additions):**
```
LifeText/
├── migrations/                    # Alembic migrations (NEW)
│   ├── versions/
│   └── env.py
├── src/
│   ├── middleware/                # (NEW)
│   │   ├── auth.py                # API key validation
│   │   ├── error_handler.py       # Global error handling
│   │   └── logging.py             # Request logging
│   ├── utils/                     # (NEW)
│   │   ├── storage.py             # S3 + local file handling
│   │   ├── secrets.py             # Secret management
│   │   ├── monitoring.py          # Sentry + CloudWatch
│   │   └── validation.py          # File validation
│   └── models/
│       ├── job.py                 # (UPDATED: add audit fields)
│       └── api_key.py             # (NEW: API key model)
├── scripts/
│   ├── init_db.py                 # (existing)
│   ├── create_api_key.py          # (NEW)
│   └── deploy.sh                  # (NEW: deployment script)
├── .env.example                   # (UPDATE: add new fields)
├── .env.production.example        # (NEW)
├── Dockerfile.worker              # (NEW: separate worker container)
├── docker-compose.prod.yml        # (NEW: production composition)
├── .dockerignore                  # (NEW)
└── DEPLOYMENT.md                  # (NEW: deployment guide)
```

---

## CODE STYLE

Use the same Python conventions as Phase 0-4:

```python
# Type hints (required)
from typing import Optional, List, Dict
from pydantic import BaseModel, Field

def transcribe_file(job_id: str, file_path: str) -> Dict[str, str]:
    """Transcribe file and return result."""
    pass

# Logging (structured)
import logging
logger = logging.getLogger(__name__)

logger.info("Processing job", extra={
    "job_id": job_id,
    "duration_ms": 1234,
    "provider": "openai",
})

# Error handling (specific exceptions)
class ValidationError(Exception):
    """Raised when input validation fails."""
    pass

class StorageError(Exception):
    """Raised when file storage fails."""
    pass

# Configuration (environment-driven)
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    api_keys_enabled: bool = Field(default=True, env="API_KEYS_ENABLED")
    max_file_size_mb: int = Field(default=500, env="MAX_FILE_SIZE_MB")
    
    class Config:
        env_file = ".env"
```

---

## TESTING STRATEGY

### Test Coverage by Tier

**Unit Tests (~70%)**
- LLM provider implementations
- File validation logic
- Post-processing service
- Quality checking
- Utilities (secrets, storage)

**Integration Tests (~20%)**
- API endpoints (health, transcribe, jobs, intelligence, chat)
- Database operations (create, read, update)
- File upload → storage → retrieval
- Worker task execution
- Error handling and retries

**E2E Tests (~10%)**
- Complete flow: upload → transcribe → intelligence
- Multi-provider testing (run same test with 2+ LLM providers)
- Rate limiting enforcement
- API key authentication

### Test Locations

```
tests/
├── unit/
│   ├── test_llm_providers.py      # LLM abstraction
│   ├── test_validation.py         # Input validation
│   ├── test_storage.py            # File storage
│   └── test_secrets.py            # Secret management
├── integration/
│   ├── test_api.py                # API endpoints
│   ├── test_database.py           # DB operations
│   ├── test_worker.py             # Celery tasks
│   └── test_e2e.py                # Complete flows
└── conftest.py                    # Pytest fixtures
```

### Coverage Goals

- **Target**: 80%+ coverage
- **Critical paths** (auth, file upload, LLM calls): 100%
- **Error handling**: 100%
- **Utilities**: 75%+

### CI/CD Pipeline

```yaml
# GitHub Actions / GitLab CI / Jenkins
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - run: pytest --cov=src --cov-report=xml
      - run: npm run lint  # Python linting
      - run: bandit -r src  # Security linting
      - run: docker build .  # Docker build test
```

---

## BOUNDARIES

### Always Do

- ✅ Validate all user input at API boundaries
- ✅ Log all errors with full context
- ✅ Use environment variables for all secrets (never hardcode)
- ✅ Hash API keys before storing
- ✅ Validate file type and size before processing
- ✅ Use prepared statements/ORM for database (already doing this)
- ✅ Add retry logic for external API calls (already doing this)
- ✅ Set rate limits on all public endpoints
- ✅ Use HTTPS in production
- ✅ Test deployments in staging before production
- ✅ Have a rollback plan for every deployment

### Ask First (Requires Approval)

- Changing database schema
- Adding new authentication flows
- Storing new types of PII
- Changing file upload size limits
- Modifying rate limiting rules
- Adding new external service integrations
- Disabling security features

### Never Do

- ❌ Commit secrets, API keys, or credentials to git
- ❌ Expose stack traces in API responses (log, don't return)
- ❌ Trust client-side validation alone
- ❌ Store API keys in plain text in database
- ❌ Log passwords, API keys, or full credit card numbers
- ❌ Use `eval()` or execute user input as code
- ❌ Disable HTTPS or security headers in production
- ❌ Deploy without testing in staging first

---

## SUCCESS CRITERIA

### Security ✅
- [ ] No secrets in code or git history (checked with git-secrets)
- [ ] All API endpoints require authentication
- [ ] File uploads validated (type, size, malware scan)
- [ ] Input validated and sanitized at all boundaries
- [ ] Errors don't expose internal details to users
- [ ] Database queries use ORM (no string concatenation)
- [ ] Rate limiting active on all public endpoints
- [ ] HTTPS enforced in production

### Reliability ✅
- [ ] Database connection pooling configured
- [ ] Retry logic with exponential backoff for external calls
- [ ] Graceful degradation (service can handle partial failures)
- [ ] Error recovery without manual intervention
- [ ] Can rollback any deployment in <5 minutes
- [ ] Health check endpoint responds correctly
- [ ] Worker queue doesn't lose jobs on restart

### Observability ✅
- [ ] All errors logged with stack traces and context
- [ ] Request logging for all API calls
- [ ] Performance metrics tracked (response time, queue depth)
- [ ] Key metrics visible in dashboards
- [ ] Alert thresholds defined (high error rate, slow responses)
- [ ] Can trace a single request through logs

### Scalability ✅
- [ ] Stateless API servers (can add/remove without state issues)
- [ ] Database connection pooling (not leaking connections)
- [ ] Worker queue can scale horizontally
- [ ] No hardcoded paths or local files (use S3 or mounted volume)
- [ ] Can handle 10x current load without code changes

### Operational ✅
- [ ] Deployment process documented and automated
- [ ] Database migrations versioned and tested
- [ ] Secrets managed securely (Vault or AWS Secrets Manager)
- [ ] Configuration via environment variables
- [ ] Can switch between local/staging/prod with one env change
- [ ] Team can deploy without requiring special access
- [ ] Incident response procedure documented

---

## OPEN QUESTIONS

1. **API Key Strategy**: Should we use:
   - Simple API keys (user registers, gets key)?
   - JWT tokens with expiration?
   - OAuth2 with GitHub/Google?
   → Recommendation: API keys for MVP, JWT for scaling

2. **File Storage**: Should we:
   - Start with S3 only (simple, pay-per-use)?
   - Support local storage + S3 (flexibility)?
   - Keep files indefinitely or implement retention policy?
   → Recommendation: S3 only, no deletion policy for now

3. **Database Backups**: Should we:
   - Use managed backups (RDS, Supabase automatic)?
   - Implement custom backup script?
   - Test restore procedure monthly?
   → Recommendation: Use managed backups, test quarterly

4. **Monitoring**: Should we:
   - Start with Sentry + basic logging?
   - Add full APM (Datadog, New Relic)?
   - Build dashboards immediately?
   → Recommendation: Sentry + CloudWatch, dashboards after launch

5. **User Authentication**: Should MVP be:
   - Single hardcoded user (dev mode)?
   - API key-based multi-user?
   - Full user management system?
   → Recommendation: API key-based (easy to expand to web frontend later)

---

## IMPLEMENTATION TASKS

Broken into 6 phases (each phase ~1-2 days):

### Phase 5.1: Secrets & Configuration Management
- [ ] Implement AWS Secrets Manager integration (or Vault)
- [ ] Add validation for all required environment variables
- [ ] Create `.env.production.example` template
- [ ] Add pre-commit hook to prevent secrets from being committed
- [ ] Update deployment docs
- **Verification**: Run app with production `.env`, no secrets in logs

### Phase 5.2: API Authentication & Rate Limiting
- [ ] Implement API key model and authentication middleware
- [ ] Add rate limiting middleware (per IP, per API key)
- [ ] Create API key management endpoints (generate, revoke, list)
- [ ] Add tests for auth and rate limiting
- [ ] Document API key setup
- **Verification**: Unauthorized requests rejected, rate limits enforced

### Phase 5.3: File Upload Validation & Storage
- [ ] Implement file size, type, and malware validation
- [ ] Add S3 storage integration (upload, download, delete)
- [ ] Keep local storage option for testing
- [ ] Add tests for storage layer
- [ ] Document file management
- **Verification**: Invalid files rejected, S3 uploads work, local files work

### Phase 5.4: Error Handling, Logging & Monitoring
- [ ] Implement Sentry integration for error tracking
- [ ] Add structured logging to all major operations
- [ ] Create CloudWatch dashboards for key metrics
- [ ] Add request logging middleware (with sensitive data redaction)
- [ ] Implement health check endpoint with detailed status
- [ ] Add tests for error scenarios
- **Verification**: Errors logged to Sentry, CloudWatch shows metrics

### Phase 5.5: Database Resilience & Migrations
- [ ] Set up Alembic for database migrations
- [ ] Create initial migration from Phase 0-4
- [ ] Add database connection pooling
- [ ] Implement connection retry logic
- [ ] Test migrations (apply, rollback, reapply)
- [ ] Document migration procedure
- **Verification**: Migrations apply/rollback cleanly, no data loss

### Phase 5.6: Deployment & Rollback Strategy
- [ ] Create production Docker Compose (or ECS/K8s templates)
- [ ] Implement feature flag system for safe rollouts
- [ ] Create deployment scripts (automated)
- [ ] Document rollback procedure
- [ ] Create pre-deployment checklist
- [ ] Test full deployment pipeline in staging
- **Verification**: Can deploy to staging, rollback works, no downtime

---

## TASKS DETAIL

### Task 5.1.1: AWS Secrets Manager Integration

**Description**: Implement secure secret management using AWS Secrets Manager.

**Acceptance Criteria**:
- [ ] Can read secrets from AWS Secrets Manager in production
- [ ] Falls back to environment variables for local development
- [ ] Pre-commit hook prevents `.env` files from being committed
- [ ] No secrets appear in logs or error messages
- [ ] Secrets are cached (don't hit AWS on every request)

**Files to Create/Modify**:
- `src/utils/secrets.py` — Secrets loader
- `src/config.py` — Update to use secrets loader
- `.git/hooks/pre-commit` — Secret detection hook
- Tests: `tests/unit/test_secrets.py`

**Verification**:
```bash
pytest tests/unit/test_secrets.py
# Verify: run with AWS credentials, verify secrets loaded
# Verify: run without AWS credentials, verify fallback to env
# Verify: try to commit .env, get blocked
```

### Task 5.1.2: Environment Validation

**Description**: Validate that all required environment variables are set on startup.

**Acceptance Criteria**:
- [ ] App fails to start with clear error message if vars missing
- [ ] Production mode requires all strict vars
- [ ] Development mode has sensible defaults
- [ ] Validation runs on app startup (not first use)

**Files to Create/Modify**:
- `src/config.py` — Add validation logic
- Tests: `tests/unit/test_config.py`

**Verification**:
```bash
# Start without required vars, get clear error message
unset LLM_PROVIDER && uvicorn src.main:app
# Error: "LLM_PROVIDER not set, required in production"
```

### Task 5.2.1: API Key Authentication

**Description**: Implement API key-based authentication for all endpoints.

**Acceptance Criteria**:
- [ ] API key stored hashed in database
- [ ] API key validated on every request
- [ ] Invalid/missing keys return 401 Unauthorized
- [ ] API key rotation supported (generate new, revoke old)
- [ ] Endpoints are protected except `/health` and `/docs`

**Files to Create/Modify**:
- `src/models/api_key.py` — API key model
- `src/middleware/auth.py` — Authentication middleware
- `src/routers/auth.py` — API key management endpoints (NEW)
- `src/main.py` — Register auth middleware
- Tests: `tests/integration/test_api_key_auth.py`

**Verification**:
```bash
# Get API key (requires initial key or setup endpoint)
KEY=$(curl -X POST http://localhost:8000/api/auth/keys -d '{"name": "test"}' | jq -r '.key')

# Use API key
curl -H "Authorization: Bearer $KEY" http://localhost:8000/api/jobs

# Invalid key
curl -H "Authorization: Bearer invalid" http://localhost:8000/api/jobs
# Response: 401 Unauthorized
```

### Task 5.2.2: Rate Limiting

**Description**: Add rate limiting to prevent abuse.

**Acceptance Criteria**:
- [ ] Per-IP rate limit (100 req/min for anonymous)
- [ ] Per-API-key rate limit (1000 req/min for authenticated)
- [ ] Rate limit headers in response (X-RateLimit-Remaining)
- [ ] 429 Too Many Requests when exceeded
- [ ] Limits are per endpoint (stricter for auth, looser for public)
- [ ] Rate limit info in error response

**Files to Create/Modify**:
- `src/middleware/rate_limit.py` — Rate limiting middleware (NEW)
- `src/main.py` — Register rate limit middleware
- Tests: `tests/integration/test_rate_limit.py`

**Verification**:
```bash
# Make 101 requests, 101st returns 429
for i in {1..101}; do
  curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8000/api/jobs
done
# Last response: 429
```

### Task 5.3.1: File Validation

**Description**: Validate uploaded files before processing.

**Acceptance Criteria**:
- [ ] File size limit enforced (max 500MB)
- [ ] File type validation (only audio/video)
- [ ] Malware scan (optional: use ClamAV or VirusTotal API)
- [ ] Descriptive error messages for invalid files
- [ ] File validation happens before storage

**Files to Create/Modify**:
- `src/utils/validation.py` — File validation
- `src/routers/transcribe.py` — Update upload handler
- Tests: `tests/unit/test_file_validation.py`

**Verification**:
```bash
# Valid file: accepted
curl -F "file=@valid.mp3" http://localhost:8000/api/transcribe

# Invalid type: rejected
curl -F "file=@document.pdf" http://localhost:8000/api/transcribe
# Response: 400 Bad Request

# Oversized: rejected
dd if=/dev/zero bs=1M count=501 of=huge.mp3
curl -F "file=@huge.mp3" http://localhost:8000/api/transcribe
# Response: 413 Payload Too Large
```

### Task 5.3.2: S3 Storage Integration

**Description**: Implement S3 storage for uploaded files with local fallback.

**Acceptance Criteria**:
- [ ] Files uploaded to S3 in production
- [ ] Local storage used in development
- [ ] Retrieve files from S3 or local storage
- [ ] Delete files when job is deleted (future)
- [ ] Presigned URLs for secure download
- [ ] No local /tmp files in production
- [ ] Tests pass with both storage backends

**Files to Create/Modify**:
- `src/utils/storage.py` — Storage abstraction (S3 + local)
- `src/config.py` — Add S3 configuration
- `src/routers/transcribe.py` — Update to use storage layer
- `src/workers/transcript_worker.py` — Update to use storage layer
- Tests: `tests/unit/test_storage.py`

**Verification**:
```bash
# Upload file, verify in S3
curl -F "file=@audio.mp3" http://localhost:8000/api/transcribe
# Check S3: file exists

# Retrieve file, verify presigned URL works
curl "https://s3.amazonaws.com/lifetext-prod/.../file.mp3?..."
# File downloads successfully
```

### Task 5.4.1: Sentry Error Tracking

**Description**: Integrate Sentry for error tracking and alerting.

**Acceptance Criteria**:
- [ ] Sentry SDK initialized in FastAPI app
- [ ] Unhandled exceptions sent to Sentry
- [ ] Error context includes user, request, job info
- [ ] Sensitive data (API keys) redacted before sending
- [ ] Alerts configured for critical errors
- [ ] Sentry DSN in environment variables

**Files to Create/Modify**:
- `src/utils/monitoring.py` — Sentry integration (NEW)
- `src/main.py` — Initialize Sentry
- `src/config.py` — Add Sentry DSN
- Tests: `tests/unit/test_monitoring.py`

**Verification**:
```bash
# Trigger error, check Sentry dashboard
curl http://localhost:8000/api/jobs/nonexistent
# Error appears in Sentry within 10 seconds
```

### Task 5.4.2: Structured Logging

**Description**: Add structured logging to all major operations.

**Acceptance Criteria**:
- [ ] All requests logged (method, path, status, duration)
- [ ] All errors logged with stack trace
- [ ] All worker tasks logged (start, end, error)
- [ ] LLM calls logged (provider, model, tokens, duration)
- [ ] File operations logged
- [ ] Sensitive data redacted (API keys, PII)
- [ ] Logs sent to CloudWatch in production
- [ ] JSON format for easy parsing

**Files to Create/Modify**:
- `src/middleware/logging.py` — Request logging middleware (NEW)
- Update existing code to add structured logging
- Tests: `tests/unit/test_logging.py`

**Verification**:
```bash
# Upload file, check logs
curl -F "file=@audio.mp3" http://localhost:8000/api/transcribe
# Logs show: upload started, file validated, job created, worker queued
```

### Task 5.4.3: Health Check Endpoint

**Description**: Implement detailed health check endpoint for monitoring.

**Acceptance Criteria**:
- [ ] `GET /health` returns 200 with status
- [ ] Checks database connectivity
- [ ] Checks Redis connectivity
- [ ] Checks file storage access
- [ ] Reports version and environment
- [ ] Response time < 500ms
- [ ] Used for load balancer health checks

**Files to Create/Modify**:
- `src/routers/health.py` — Health check endpoints (NEW)
- Tests: `tests/integration/test_health.py`

**Verification**:
```bash
curl http://localhost:8000/health
# Response: {
#   "status": "healthy",
#   "version": "1.0.0",
#   "database": "connected",
#   "redis": "connected",
#   "storage": "ready"
# }
```

### Task 5.5.1: Alembic Database Migrations

**Description**: Set up database migrations with Alembic.

**Acceptance Criteria**:
- [ ] Alembic initialized and configured
- [ ] Initial migration created from existing models
- [ ] Migrations can be applied (upgrade)
- [ ] Migrations can be rolled back (downgrade)
- [ ] Migrations run automatically on app startup (or manually)
- [ ] Tested in CI/CD pipeline

**Files to Create/Modify**:
- `migrations/` — Alembic directory
- `alembic.ini` — Alembic configuration
- `migrations/env.py` — Migration environment
- `migrations/versions/001_initial_schema.py` — Initial migration
- Tests: `tests/integration/test_migrations.py`

**Verification**:
```bash
# Apply migrations
alembic upgrade head
# Check database schema

# Rollback
alembic downgrade -1
# Check schema reverted

# Reapply
alembic upgrade head
# Verify schema back
```

### Task 5.5.2: Connection Pooling

**Description**: Configure database connection pooling for resilience.

**Acceptance Criteria**:
- [ ] Connection pool configured (pool size, overflow, timeout)
- [ ] Connections recycled after timeout (prevent stale connections)
- [ ] Pool size appropriate for concurrency level
- [ ] Connection errors handled gracefully
- [ ] Monitored in production (pool size, wait time)

**Files to Create/Modify**:
- `src/db.py` — Update SQLAlchemy engine configuration
- Tests: `tests/integration/test_db_resilience.py`

**Verification**:
```bash
# Monitor connection pool size
# Under load: verify connections are pooled, not creating new ones
```

### Task 5.6.1: Deployment Scripts

**Description**: Create automated deployment process.

**Acceptance Criteria**:
- [ ] Deployment script is idempotent (run multiple times safely)
- [ ] Pre-deployment checks (tests, build, linting)
- [ ] Blue-green deployment or feature flag for zero downtime
- [ ] Database migrations run during deploy
- [ ] Health check verified post-deploy
- [ ] Rollback procedure documented and tested

**Files to Create/Modify**:
- `scripts/deploy.sh` — Deployment script
- `scripts/rollback.sh` — Rollback script
- `DEPLOYMENT.md` — Deployment documentation

**Verification**:
```bash
./scripts/deploy.sh production
# Verify: new code running, health checks pass
# Verify: old version still running (blue-green)
# Verify: traffic switched to new version

./scripts/rollback.sh production
# Verify: old version running again
```

### Task 5.6.2: Feature Flags

**Description**: Implement feature flags for safe rollouts.

**Acceptance Criteria**:
- [ ] Feature flag system implemented (in-memory or Redis)
- [ ] Flags can be enabled/disabled without redeploying
- [ ] Flag state persisted
- [ ] Gradual rollout support (% of users)
- [ ] Flags tested in CI/CD

**Files to Create/Modify**:
- `src/services/feature_flags.py` — Feature flag service (NEW)
- `src/main.py` — Initialize feature flags
- Tests: `tests/unit/test_feature_flags.py`

**Verification**:
```bash
# Enable feature for 10% of users
curl -X POST http://localhost:8000/api/admin/flags \
  -d '{"name": "new_feature", "enabled_percent": 10}'

# Check flag
curl http://localhost:8000/api/admin/flags/new_feature
# Response: {"enabled_percent": 10}

# Gradually increase to 50%
curl -X PATCH http://localhost:8000/api/admin/flags/new_feature \
  -d '{"enabled_percent": 50}'
```

---

## RISKS & MITIGATIONS

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|-----------|
| Database migration fails in production | Data loss, downtime | Medium | Test migrations thoroughly, have rollback plan, blue-green deployments |
| API key leaked in logs | Security breach | Medium | Redact secrets before logging, scan logs for patterns, rotate keys |
| S3 bucket misconfigured (public) | Data breach | Low | IaC for S3 config, access control tests, audit logs |
| Rate limiting too strict | Users blocked | Medium | Start loose, tighten gradually, monitor false positives |
| Secrets not rotated | Key compromise | Low | Automated rotation, audit key usage, expiration dates |
| File upload virus | Server compromise | Medium | Scan files, reject suspicious, isolate uploads, monitor |
| Database connection leak | Resource exhaustion | Low | Connection pooling, monitoring, automated cleanup |
| Deployment goes wrong | Application down | Low | Automated rollback, staging tests, health checks |

---

## DEPENDENCIES BETWEEN TASKS

```
5.1.1 (Secrets) ──┐
5.1.2 (Env Val)   ├─→ 5.2.1 (API Key Auth)
5.2.2 (Rate Lim)  │
                  ├─→ 5.3.1 (File Validation)
                  ├─→ 5.3.2 (S3 Storage)
                  ├─→ 5.4.1 (Sentry)
                  ├─→ 5.4.2 (Logging)
                  ├─→ 5.4.3 (Health Check)
                  │
5.5.1 (Migrations)├─→ 5.5.2 (Connection Pool)
                  │
                  └─→ 5.6.1 (Deploy Script)
                  └─→ 5.6.2 (Feature Flags)
```

---

## VERIFICATION CHECKPOINTS

### Checkpoint: After 5.1 (Secrets & Configuration)
- [ ] App starts without exposing secrets in logs
- [ ] Pre-commit hook prevents secret commits
- [ ] Can switch between dev/staging/prod with env file only
- [ ] All tests pass

### Checkpoint: After 5.2 (Auth & Rate Limiting)
- [ ] API key authentication working
- [ ] Rate limits enforced
- [ ] Unauth requests rejected
- [ ] All tests pass

### Checkpoint: After 5.3 (File Management)
- [ ] Files uploaded and validated
- [ ] S3 storage working (or local fallback)
- [ ] Invalid files rejected with clear errors
- [ ] All tests pass

### Checkpoint: After 5.4 (Monitoring)
- [ ] Errors logged to Sentry
- [ ] Structured logs visible in CloudWatch
- [ ] Health check endpoint responding
- [ ] All tests pass

### Checkpoint: After 5.5 (Database)
- [ ] Migrations apply cleanly
- [ ] Can rollback migrations
- [ ] Connection pooling working
- [ ] All tests pass

### Checkpoint: After 5.6 (Deployment)
- [ ] Can deploy to staging
- [ ] Can rollback smoothly
- [ ] Feature flags working
- [ ] All tests pass
- [ ] Ready for production

---

## ACCEPTANCE CRITERIA (MVP Production Ready)

✅ **Security**
- No secrets in code or git
- All endpoints protected (except /health)
- File uploads validated
- Input validation on all boundaries
- Errors don't expose internals

✅ **Reliability**
- Can handle 24 hours without manual intervention
- Can recover from partial failures (DB restart, file storage hiccup)
- Can rollback any deployment in <5 minutes
- Health check proves system is working

✅ **Observability**
- All errors logged to Sentry
- Request logging in CloudWatch
- Key metrics visible
- Can debug any issue with logs

✅ **Scalability**
- Stateless API servers
- Connection pooling
- Can add workers to increase capacity
- No hardcoded local paths

✅ **Operational**
- Deployment automated
- Migrations versioned
- Secrets managed
- Configuration via environment
- Team can deploy

---

## TIMELINE

| Phase | Tasks | Effort | Days | Status |
|-------|-------|--------|------|--------|
| 5.1 | Secrets & Config | 2 tasks | 1 day | TODO |
| 5.2 | Auth & Rate Limit | 2 tasks | 1 day | TODO |
| 5.3 | File Management | 2 tasks | 1 day | TODO |
| 5.4 | Monitoring | 3 tasks | 1-2 days | TODO |
| 5.5 | Database | 2 tasks | 1 day | TODO |
| 5.6 | Deployment | 2 tasks | 1 day | TODO |
| **Total** | **13 tasks** | | **6-7 days** | |

---

## NEXT STEPS

1. **Review & Approve Spec** — Confirm assumptions and success criteria
2. **Create Implementation Plan** — Break Phase 5 into ordered tasks
3. **Execute Tasks** — Implement 5.1 through 5.6 in order
4. **Verify Each Checkpoint** — Test after each phase
5. **Deploy to Staging** — Test full production setup
6. **Deploy to Production** — Go live!

---

## REFERENCE DOCS

- Security Checklist: See `agent-skills/references/security-checklist.md`
- Performance Checklist: See `agent-skills/references/performance-checklist.md`
- Testing Patterns: See `agent-skills/references/testing-patterns.md`
- Shipping Guide: See `agent-skills/skills/shipping-and-launch/SKILL.md`
- Code Review: See `agent-skills/skills/code-review-and-quality/SKILL.md`

