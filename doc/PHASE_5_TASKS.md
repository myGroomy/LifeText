# Phase 5: Production Hardening — Detailed Task Breakdown

**Version**: 1.0.0  
**Total Tasks**: 13  
**Estimated Duration**: 6-7 days  
**Coordination**: Sequential (dependencies noted)

---

## QUICK START FOR AGENTS

This document breaks Phase 5 into **13 atomic, testable tasks** that can each be completed in one focused session (1-2 hours per task).

**How to use:**
1. Read the task description
2. Check **Acceptance Criteria** (what DONE means)
3. Implement the code
4. Run **Verification** to confirm it works
5. Commit and move to next task

---

## PHASE 5.1: SECRETS & CONFIGURATION MANAGEMENT

### Task 5.1.1: AWS Secrets Manager Integration

**Description**  
Implement secure secret management that reads from AWS Secrets Manager in production and falls back to environment variables in development.

**Why This First**  
Other tasks depend on secrets being available. Get this right before building on top of it.

**Acceptance Criteria**
- [ ] `SecretManager` class implements secret retrieval from AWS Secrets Manager
- [ ] Falls back to environment variables if AWS not available (dev mode)
- [ ] Secrets are cached in memory (don't hit AWS on every request)
- [ ] Cache invalidation option for manual refresh
- [ ] `get_secret()` function is exported and can be used everywhere
- [ ] Unit tests pass (mock AWS SDK)
- [ ] No secrets printed to stdout/logs
- [ ] Works with both AWS SDK v3 and local boto3

**Files to Create**
- `src/utils/secrets.py` — NEW file with `SecretManager` class

**Files to Modify**
- `src/config.py` — Use `SecretManager` for LLM and database secrets
- `requirements.txt` — Add `boto3` (AWS SDK)

**Files to Reference**
- `src/config.py` (existing) — See current environment setup

**Implementation Notes**
```python
# Pseudocode structure:
class SecretManager:
    def __init__(self):
        self.cache = {}
        self.aws_available = check_aws_credentials()
    
    def get_secret(self, secret_name: str) -> str:
        # Check cache first
        # If not cached, try AWS Secrets Manager
        # If AWS unavailable, fall back to os.getenv()
        # Return value or raise error
        pass
```

**Verification Steps**
```bash
# 1. Test with local environment (no AWS)
export LLM_API_KEY="test-key"
python -c "from src.utils.secrets import get_secret; print(get_secret('llm_api_key'))"
# Should print: test-key

# 2. Run unit tests
pytest tests/unit/test_secrets.py
# All tests pass

# 3. Verify no secrets in logs
python src/main.py 2>&1 | grep -i "test-key"
# Should return nothing
```

**Estimated Time**: 1-1.5 hours

**Dependency**: None (first task)

---

### Task 5.1.2: Environment Validation on Startup

**Description**  
Validate that all required environment variables are set when the application starts. Fail early with clear errors instead of cryptic errors later.

**Why**  
Catches configuration mistakes before they cause production issues.

**Acceptance Criteria**
- [ ] Required env vars validated on app startup (before any processing)
- [ ] Clear error message listing all missing required vars
- [ ] Dev mode allows some vars to have defaults
- [ ] Prod mode requires all critical vars (LLM, database, S3)
- [ ] Env validation happens in `config.py` (during import)
- [ ] Tests pass (both with valid and invalid configs)
- [ ] Error includes suggestion for which `.env` file to use

**Files to Modify**
- `src/config.py` — Add `validate_config()` call at module load
- `tests/unit/test_config.py` — NEW test file

**Implementation Notes**
```python
# In config.py, after defining Settings class:
def validate_config(settings: Settings) -> None:
    """Validate that required config is present."""
    required_in_prod = ["LLM_PROVIDER", "LLM_API_KEY", "DATABASE_URL"]
    if settings.environment == "production":
        for var in required_in_prod:
            if not getattr(settings, var.lower(), None):
                raise ValueError(f"Required: {var}")

# Call at module level:
validate_config(settings)
```

**Verification Steps**
```bash
# 1. Test missing required var
unset LLM_PROVIDER
python -c "from src import config" 2>&1
# Should show: "ERROR: LLM_PROVIDER not configured"

# 2. With valid config, no error
export LLM_PROVIDER="openai"
python -c "from src import config" 2>&1
# Should succeed silently

# 3. Run tests
pytest tests/unit/test_config.py
# All tests pass
```

**Estimated Time**: 1 hour

**Dependency**: Task 5.1.1 (secrets should already be available)

---

## PHASE 5.2: API AUTHENTICATION & RATE LIMITING

### Task 5.2.1: API Key Model & Authentication

**Description**  
Implement API key-based authentication. Users must provide a valid API key in the `Authorization: Bearer <key>` header to access protected endpoints.

**Why**  
Security boundary — prevent unauthorized access before any processing.

**Acceptance Criteria**
- [ ] `APIKey` database model with name, key (hashed), created_at, expires_at, is_active
- [ ] API keys hashed using bcrypt (never stored plaintext)
- [ ] Authentication middleware validates header and key
- [ ] Invalid/missing keys return 401 with clear error message
- [ ] Public endpoints (health, docs) work without auth
- [ ] Protected endpoints require valid key
- [ ] Key can be revoked (set is_active=false)
- [ ] Tests pass (auth success, invalid key, missing key, revoked key)

**Files to Create**
- `src/models/api_key.py` — NEW model for API keys
- `src/middleware/auth.py` — NEW authentication middleware

**Files to Modify**
- `src/db.py` — Add `APIKey` table creation
- `src/main.py` — Register auth middleware
- `tests/integration/test_auth.py` — NEW test file

**Implementation Notes**
```python
# src/models/api_key.py structure:
from sqlalchemy import Column, String, DateTime, Boolean
from datetime import datetime, timedelta

class APIKey(Base):
    __tablename__ = "api_keys"
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    key_hash = Column(String, nullable=False)  # bcrypt hash of actual key
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
```

**Verification Steps**
```bash
# 1. Insert test API key
python -c "
from src.db import SessionLocal
from src.models.api_key import APIKey
import secrets
import bcrypt

session = SessionLocal()
key = secrets.token_urlsafe(32)
key_hash = bcrypt.hashpw(key.encode(), bcrypt.gensalt()).decode()
api_key = APIKey(id='test-1', name='test', key_hash=key_hash)
session.add(api_key)
session.commit()
print(f'Key: {key}')
"

# 2. Test auth with valid key
curl -H "Authorization: Bearer <key>" http://localhost:8000/api/jobs
# Should return 200

# 3. Test auth with invalid key
curl -H "Authorization: Bearer invalid" http://localhost:8000/api/jobs
# Should return 401

# 4. Test without auth header
curl http://localhost:8000/api/jobs
# Should return 401

# 5. Test public endpoint (no auth needed)
curl http://localhost:8000/health
# Should return 200

# 6. Run tests
pytest tests/integration/test_auth.py
```

**Estimated Time**: 1.5-2 hours

**Dependency**: Task 5.1.2 (config validation)

---

### Task 5.2.2: Rate Limiting Middleware

**Description**  
Add rate limiting to prevent abuse. Limit requests per IP (unauthenticated) and per API key (authenticated).

**Why**  
Prevents DoS attacks, protects free tier from abuse.

**Acceptance Criteria**
- [ ] Rate limiter stores request counts (in-memory or Redis)
- [ ] Per-IP limit: 100 requests/minute for unauthenticated
- [ ] Per-key limit: 1000 requests/minute for authenticated
- [ ] Stricter limit for auth endpoints: 10 attempts/15 minutes
- [ ] Returns 429 Too Many Requests when exceeded
- [ ] Response includes headers: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`
- [ ] Different limits per endpoint (e.g., transcribe may have stricter limits)
- [ ] Tests pass (verify limits enforced, headers present)

**Files to Create**
- `src/middleware/rate_limit.py` — NEW rate limiting middleware

**Files to Modify**
- `src/main.py` — Register rate limit middleware
- `src/config.py` — Add rate limit configuration
- `tests/integration/test_rate_limit.py` — NEW test file

**Implementation Notes**
```python
# Rate limiter pseudocode:
class RateLimiter:
    def __init__(self, redis_client=None):
        self.limits = {}  # {key: {"count": N, "reset_at": T}}
        self.redis = redis_client  # Use Redis if available for distributed systems
    
    async def check_rate_limit(self, identifier: str, limit: int, window_seconds: int):
        # Increment counter for identifier
        # Check if exceeded
        # Return (allowed, remaining, reset_at)
```

**Verification Steps**
```bash
# 1. Create a script to make 101 requests
for i in {1..101}; do
  curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8000/api/jobs
done
# First 100: 200 or 401 (depending on auth)
# 101st: 429

# 2. Check rate limit headers
curl -i http://localhost:8000/api/jobs 2>&1 | grep -i "x-ratelimit"
# Should show remaining and reset time

# 3. Run tests
pytest tests/integration/test_rate_limit.py
```

**Estimated Time**: 1.5-2 hours

**Dependency**: Task 5.2.1 (auth must work first)

---

## PHASE 5.3: FILE UPLOAD VALIDATION & STORAGE

### Task 5.3.1: File Validation Service

**Description**  
Validate uploaded files before processing: check size, type, and optionally scan for malware.

**Why**  
Prevents processing of invalid files, protects against certain attacks.

**Acceptance Criteria**
- [ ] File size checked (max 500MB configurable)
- [ ] File type validated (audio/video only)
- [ ] File extension matches MIME type
- [ ] Rejects unknown file types clearly
- [ ] Error messages are user-friendly
- [ ] Validation happens before file storage
- [ ] Optional malware scan (stubbed for now, easy to add VirusTotal later)
- [ ] Tests pass (valid file, oversized, wrong type, etc.)

**Files to Create**
- `src/utils/validation.py` — NEW file with validation functions

**Files to Modify**
- `src/routers/transcribe.py` — Call validation before storing file
- `src/config.py` — Add file size limit config
- `tests/unit/test_validation.py` — NEW test file

**Implementation Notes**
```python
# Validation structure:
ALLOWED_AUDIO_TYPES = ["audio/mpeg", "audio/wav", "audio/ogg", "audio/aac"]
ALLOWED_VIDEO_TYPES = ["video/mp4", "video/mpeg", "video/quicktime"]
ALLOWED_TYPES = ALLOWED_AUDIO_TYPES + ALLOWED_VIDEO_TYPES

def validate_file(file: UploadFile, max_size_mb: int = 500) -> None:
    """Validate file or raise ValidationError."""
    # Check size
    # Check MIME type
    # Check extension matches MIME
    pass
```

**Verification Steps**
```bash
# 1. Valid audio file
curl -F "file=@valid.mp3" http://localhost:8000/api/transcribe
# Should accept

# 2. PDF (wrong type)
curl -F "file=@document.pdf" http://localhost:8000/api/transcribe
# Should reject with 400 and clear error message

# 3. Oversized file
dd if=/dev/zero bs=1M count=501 of=huge.mp3
curl -F "file=@huge.mp3" http://localhost:8000/api/transcribe
# Should reject with 413

# 4. Run tests
pytest tests/unit/test_validation.py
```

**Estimated Time**: 1 hour

**Dependency**: Task 5.2.2 (rate limiting, so upload endpoint protected)

---

### Task 5.3.2: S3 Storage Abstraction Layer

**Description**  
Implement file storage abstraction that uses S3 in production and local filesystem in development.

**Why**  
Separation of concerns — allow different storage backends without changing application code.

**Acceptance Criteria**
- [ ] `FileStorage` abstract base class with upload/download/delete methods
- [ ] `S3Storage` implementation using boto3
- [ ] `LocalStorage` implementation using filesystem
- [ ] Automatic fallback to LocalStorage if S3 config missing (dev mode)
- [ ] Presigned URLs for S3 downloads (secure, time-limited)
- [ ] File paths namespaced by user/job to prevent collisions
- [ ] Tests pass (both backends)
- [ ] S3 error handling (upload fails, bucket not found, etc.)

**Files to Create**
- `src/utils/storage.py` — NEW file with storage abstraction

**Files to Modify**
- `src/config.py` — Add S3 configuration (bucket, region)
- `src/routers/transcribe.py` — Use storage layer instead of direct file ops
- `src/workers/transcript_worker.py` — Use storage layer for reads/writes
- `tests/unit/test_storage.py` — NEW test file

**Implementation Notes**
```python
# Storage abstraction:
from abc import ABC, abstractmethod

class FileStorage(ABC):
    @abstractmethod
    async def upload(self, file_path: str, content: bytes) -> str:
        """Upload file, return storage URL or key."""
        pass
    
    @abstractmethod
    async def download(self, file_key: str) -> bytes:
        """Download file, return content."""
        pass
    
    @abstractmethod
    async def delete(self, file_key: str) -> None:
        """Delete file."""
        pass

class S3Storage(FileStorage):
    # Uses boto3 to interact with S3
    pass

class LocalStorage(FileStorage):
    # Uses filesystem, stores in /tmp or configured path
    pass
```

**Verification Steps**
```bash
# 1. Upload file in dev mode (LocalStorage)
curl -F "file=@audio.mp3" http://localhost:8000/api/transcribe
JOB_ID=$(curl ... | jq -r '.job_id')

# Wait for job, check file stored locally
ls -la /tmp/lifetext/jobs/$JOB_ID/
# Should see audio.mp3

# 2. Configure S3 and restart
export AWS_ACCESS_KEY_ID="..."
export AWS_SECRET_ACCESS_KEY="..."
export S3_BUCKET="lifetext-prod"

# Upload file again
curl -F "file=@audio.mp3" http://localhost:8000/api/transcribe

# Verify file in S3
aws s3 ls s3://lifetext-prod/
# Should see file

# 3. Run tests
pytest tests/unit/test_storage.py
```

**Estimated Time**: 1.5-2 hours

**Dependency**: Task 5.3.1 (validation comes before storage)

---

## PHASE 5.4: ERROR HANDLING, LOGGING & MONITORING

### Task 5.4.1: Sentry Integration for Error Tracking

**Description**  
Integrate Sentry to capture and track errors with full context (user, request, job info).

**Why**  
Catch production errors before users report them, identify trends.

**Acceptance Criteria**
- [ ] Sentry SDK initialized in FastAPI app
- [ ] Unhandled exceptions automatically captured
- [ ] Error context includes user (API key), request path, job_id
- [ ] Sensitive data redacted (API keys, tokens, PII)
- [ ] Sentry DSN configured via environment variable
- [ ] Manual error reporting available (`capture_exception()`)
- [ ] Tests pass (mock Sentry client)
- [ ] Can view errors in Sentry dashboard

**Files to Create**
- `src/utils/monitoring.py` — NEW file with Sentry setup

**Files to Modify**
- `src/main.py` — Initialize Sentry before starting app
- `src/config.py` — Add Sentry DSN config
- `requirements.txt` — Add `sentry-sdk`
- `tests/unit/test_monitoring.py` — NEW test file

**Implementation Notes**
```python
# Sentry setup:
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

def init_sentry(dsn: str, environment: str) -> None:
    """Initialize Sentry for error tracking."""
    if dsn:
        sentry_sdk.init(
            dsn=dsn,
            integrations=[FastApiIntegration()],
            environment=environment,
            traces_sample_rate=0.1,  # 10% of transactions
            before_send=redact_sensitive_data,
        )

def redact_sensitive_data(event, hint):
    """Remove secrets before sending to Sentry."""
    # Remove API keys, tokens, passwords from event
    return event
```

**Verification Steps**
```bash
# 1. Configure Sentry
export SENTRY_DSN="https://key@sentry.io/project"

# 2. Trigger an error
curl http://localhost:8000/api/jobs/nonexistent
# Returns 404

# 3. Check Sentry dashboard (wait ~10 seconds)
# Should see error in Sentry

# 4. Verify no secrets in Sentry
# Event details shouldn't contain API keys, tokens

# 5. Run tests
pytest tests/unit/test_monitoring.py
```

**Estimated Time**: 1-1.5 hours

**Dependency**: Task 5.2.2 (system should be mostly functional)

---

### Task 5.4.2: Structured Logging

**Description**  
Add comprehensive structured logging (JSON format) to all major operations.

**Why**  
Enables debugging in production, tracks performance, identifies issues early.

**Acceptance Criteria**
- [ ] All API requests logged (method, path, status, duration_ms, user)
- [ ] All errors logged with stack trace and context
- [ ] All Celery tasks logged (start, end, result, error)
- [ ] All LLM calls logged (provider, model, tokens, duration_ms)
- [ ] All file operations logged (upload, download, delete)
- [ ] Sensitive data redacted (API keys, auth tokens, password hashes)
- [ ] Logs are JSON format (not plain text)
- [ ] Can filter logs by job_id, user_id, operation
- [ ] Tests pass

**Files to Create**
- `src/middleware/logging.py` — NEW request logging middleware

**Files to Modify**
- `src/main.py` — Register logging middleware
- `src/config.py` — Configure logging level and format
- All service/worker files — Add structured logging statements
- `tests/unit/test_logging.py` — NEW test file

**Implementation Notes**
```python
# Logging setup:
import logging
import json
from datetime import datetime

class JsonFormatter(logging.Formatter):
    """Format logs as JSON for easy parsing."""
    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if hasattr(record, "job_id"):
            log_data["job_id"] = record.job_id
        return json.dumps(log_data)

# Usage:
logger = logging.getLogger(__name__)
logger.info("Processing job", extra={
    "job_id": job_id,
    "duration_ms": 1234,
    "provider": "openai",
})
```

**Verification Steps**
```bash
# 1. Upload file and check logs
curl -F "file=@audio.mp3" http://localhost:8000/api/transcribe
# Check application logs

# 2. Verify JSON format
# Each log line should be valid JSON

# 3. Verify sensitive data redacted
# No API keys, tokens, or passwords in logs
grep -i "api" logs.json
# Should not contain actual key values

# 4. Run tests
pytest tests/unit/test_logging.py

# 5. Send logs to CloudWatch (future task, for now just file/stdout)
```

**Estimated Time**: 1.5-2 hours

**Dependency**: Task 5.4.1 (monitoring infrastructure in place)

---

### Task 5.4.3: Health Check Endpoint

**Description**  
Implement detailed health check endpoint that verifies all systems are operational.

**Why**  
Load balancers and orchestration platforms use health checks to route traffic and restart failed containers.

**Acceptance Criteria**
- [ ] `GET /health` returns 200 with status JSON
- [ ] Checks database connectivity (quick query)
- [ ] Checks Redis connectivity
- [ ] Checks file storage access
- [ ] Reports component status (up, down, degraded)
- [ ] Includes app version and environment
- [ ] Response time < 500ms
- [ ] Detailed health check at `GET /health/detailed` (for debugging)
- [ ] Tests pass

**Files to Create**
- `src/routers/health.py` — NEW health check endpoints

**Files to Modify**
- `src/main.py` — Register health endpoints
- `tests/integration/test_health.py` — NEW test file

**Implementation Notes**
```python
# Health check response:
{
    "status": "healthy",  # healthy | degraded | unhealthy
    "version": "1.0.0",
    "environment": "production",
    "components": {
        "database": {"status": "up", "response_time_ms": 5},
        "redis": {"status": "up", "response_time_ms": 2},
        "storage": {"status": "up", "type": "s3"}
    },
    "timestamp": "2025-01-20T12:34:56Z"
}
```

**Verification Steps**
```bash
# 1. Check health endpoint
curl http://localhost:8000/health
# Should return 200 with status JSON

# 2. Verify all components up
# Status should be "healthy" if all components ok

# 3. Verify response time
time curl http://localhost:8000/health
# Should be < 500ms

# 4. Test with down component (e.g., shut down Redis)
# Health should become "degraded"

# 5. Run tests
pytest tests/integration/test_health.py
```

**Estimated Time**: 1 hour

**Dependency**: Task 5.4.2 (logging in place)

---

## PHASE 5.5: DATABASE RESILIENCE & MIGRATIONS

### Task 5.5.1: Alembic Database Migrations

**Description**  
Set up Alembic for versioned database migrations. Create initial migration from existing database schema.

**Why**  
Enables safe schema changes, version control for database, rollback capability.

**Acceptance Criteria**
- [ ] Alembic initialized and configured
- [ ] Initial migration created from existing Job model
- [ ] Migration can be applied (upgrade to new version)
- [ ] Migration can be rolled back (downgrade)
- [ ] Migrations run automatically on app startup (or manually)
- [ ] Tested in CI/CD pipeline
- [ ] Can track schema version
- [ ] Multiple migrations can be stacked

**Files to Create**
- `alembic/` directory
- `alembic.ini` — Alembic configuration
- `alembic/env.py` — Migration environment
- `alembic/versions/001_initial_schema.py` — Initial migration

**Files to Modify**
- `src/db.py` — Configure SQLAlchemy engine for migrations
- `.gitignore` — Ignore alembic version cache
- `tests/integration/test_migrations.py` — NEW test file

**Implementation Notes**
```bash
# Initialize Alembic:
alembic init alembic

# Create initial migration:
alembic revision --autogenerate -m "Initial schema"

# Apply migration:
alembic upgrade head

# Rollback:
alembic downgrade -1

# Check current version:
alembic current
```

**Verification Steps**
```bash
# 1. Initialize Alembic
alembic init alembic

# 2. Create initial migration
alembic revision --autogenerate -m "Initial schema"
# Check alembic/versions/001_*.py was created

# 3. Apply migration
alembic upgrade head
# Should succeed

# 4. Verify schema
psql -d lifetext_db -c "\dt"
# Should show tables

# 5. Rollback
alembic downgrade -1
# Should succeed

# 6. Reapply
alembic upgrade head

# 7. Run tests
pytest tests/integration/test_migrations.py
```

**Estimated Time**: 1.5 hours

**Dependency**: Task 5.4.3 (health checks in place)

---

### Task 5.5.2: Connection Pooling & Resilience

**Description**  
Configure database connection pooling with resilience strategies (retry, timeout, recycle).

**Why**  
Prevents connection exhaustion, improves reliability under load.

**Acceptance Criteria**
- [ ] Connection pool configured (pool_size, max_overflow, pool_pre_ping)
- [ ] Connection recycled after timeout (prevents stale connections)
- [ ] Connection failures handled gracefully (retry with backoff)
- [ ] Pool size appropriate for expected concurrency
- [ ] Monitored in production (connection count, wait time)
- [ ] Tests pass (load, failure scenarios)
- [ ] No connection leaks

**Files to Modify**
- `src/db.py` — Update SQLAlchemy engine configuration
- `src/config.py` — Add connection pool config
- `tests/integration/test_db_resilience.py` — NEW test file

**Implementation Notes**
```python
# SQLAlchemy engine with pooling:
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,              # Keep 20 connections open
    max_overflow=10,           # Allow up to 10 additional connections
    pool_timeout=30,           # Wait max 30 seconds for a connection
    pool_recycle=3600,         # Recycle connection after 1 hour
    pool_pre_ping=True,        # Test connection before using (detect stale)
)
```

**Verification Steps**
```bash
# 1. Run app under moderate load
# Monitor connection count: should stay ~20, not grow unbounded

# 2. Kill database connection (simulate failure)
# App should recover and create new connection

# 3. Run tests
pytest tests/integration/test_db_resilience.py

# 4. Check connection pool stats
# (May need to add monitoring endpoint)
```

**Estimated Time**: 1 hour

**Dependency**: Task 5.5.1 (migrations in place)

---

## PHASE 5.6: DEPLOYMENT & ROLLBACK STRATEGY

### Task 5.6.1: Automated Deployment Scripts

**Description**  
Create automated deployment scripts for safe, repeatable deployments with rollback capability.

**Why**  
Manual deployments are error-prone. Automation ensures consistency and enables fast rollback.

**Acceptance Criteria**
- [ ] `scripts/deploy.sh` can deploy to any environment (staging, production)
- [ ] Pre-deployment checks: tests pass, build succeeds, no uncommitted changes
- [ ] Deployment is idempotent (safe to run multiple times)
- [ ] Database migrations run automatically during deploy
- [ ] Health check verified post-deploy
- [ ] `scripts/rollback.sh` can rollback to previous version
- [ ] Rollback procedure documented
- [ ] Can deploy from CI/CD pipeline

**Files to Create**
- `scripts/deploy.sh` — NEW deployment script
- `scripts/rollback.sh` — NEW rollback script
- `DEPLOYMENT.md` — NEW deployment guide

**Implementation Notes**
```bash
# Deploy script pseudocode:
#!/bin/bash
set -e  # Exit on error

ENVIRONMENT=$1

# Pre-deployment checks
echo "Running tests..."
pytest tests/

echo "Building Docker image..."
docker build -t lifetext-api:latest .

# Deploy
echo "Deploying to $ENVIRONMENT..."
docker tag lifetext-api:latest lifetext-api:$ENVIRONMENT
docker push lifetext-api:$ENVIRONMENT

# Update service (e.g., ECS, K8s)
# ... orchestration-specific code ...

# Run migrations
docker exec lifetext-api alembic upgrade head

# Health check
curl -f http://localhost:8000/health || exit 1

echo "Deployment successful!"
```

**Verification Steps**
```bash
# 1. Deploy to staging
./scripts/deploy.sh staging
# Should succeed

# 2. Verify app is running
curl http://staging.lifetext.com/health
# Should return 200

# 3. Rollback
./scripts/rollback.sh staging
# Should succeed

# 4. Verify old version running
curl http://staging.lifetext.com/health
# Should return 200 (old version)

# 5. Deploy again to production (after testing on staging)
./scripts/deploy.sh production
```

**Estimated Time**: 1.5-2 hours

**Dependency**: Task 5.5.2 (connection pooling)

---

### Task 5.6.2: Feature Flags for Gradual Rollout

**Description**  
Implement feature flags to enable gradual rollouts without redeploying.

**Why**  
Reduces risk of deployments, enables A/B testing, allows quick disabling of problematic features.

**Acceptance Criteria**
- [ ] Feature flag model in database
- [ ] Flags can be enabled/disabled without redeploying
- [ ] Gradual rollout support (enable for X% of users)
- [ ] Flags evaluated per-request (not cached, or cached with short TTL)
- [ ] Admin endpoints to manage flags (create, update, delete)
- [ ] Flags can target by user, API key, or percentage
- [ ] Tests pass
- [ ] Used in at least one code path (e.g., new intelligence endpoint)

**Files to Create**
- `src/models/feature_flag.py` — NEW feature flag model
- `src/services/feature_flags.py` — NEW feature flag service
- `src/routers/admin.py` — NEW admin endpoints for flag management (if not exists)

**Files to Modify**
- `src/db.py` — Add feature flag table
- `src/main.py` — Register admin router
- `tests/unit/test_feature_flags.py` — NEW test file

**Implementation Notes**
```python
# Feature flag model:
class FeatureFlag(Base):
    __tablename__ = "feature_flags"
    id = Column(String, primary_key=True)
    name = Column(String, unique=True)
    enabled_percent = Column(Integer, default=0)  # 0-100
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

# Usage:
if is_feature_enabled("new_intelligence", user_id=user_id):
    # New code path
    return get_advanced_intelligence(job_id)
else:
    # Old code path
    return get_basic_intelligence(job_id)
```

**Verification Steps**
```bash
# 1. Create feature flag
curl -X POST http://localhost:8000/api/admin/flags \
  -H "Authorization: Bearer <admin-key>" \
  -d '{"name": "new_intelligence", "enabled_percent": 0}'

# 2. Check it's disabled
curl http://localhost:8000/api/admin/flags/new_intelligence
# Response: {"enabled_percent": 0}

# 3. Enable for 10% of users
curl -X PATCH http://localhost:8000/api/admin/flags/new_intelligence \
  -d '{"enabled_percent": 10}'

# 4. Gradually increase
curl -X PATCH http://localhost:8000/api/admin/flags/new_intelligence \
  -d '{"enabled_percent": 50}'

# 5. Disable if needed
curl -X PATCH http://localhost:8000/api/admin/flags/new_intelligence \
  -d '{"enabled_percent": 0}'

# 6. Run tests
pytest tests/unit/test_feature_flags.py
```

**Estimated Time**: 1.5 hours

**Dependency**: Task 5.6.1 (deployment scripts)

---

## CHECKPOINTS & VERIFICATION

### ✅ Checkpoint 1: After 5.1 (Secrets & Configuration)
- Run these commands:
  ```bash
  pytest tests/unit/test_secrets.py
  pytest tests/unit/test_config.py
  ```
- Verify: App starts without secrets in logs
- Verify: Pre-commit hook blocks `.env` files
- **Can proceed to**: Phase 5.2

### ✅ Checkpoint 2: After 5.2 (Auth & Rate Limiting)
- Run these commands:
  ```bash
  pytest tests/integration/test_auth.py
  pytest tests/integration/test_rate_limit.py
  ```
- Verify: Can generate API key and use it
- Verify: Invalid keys rejected with 401
- Verify: Rate limits enforced with 429
- **Can proceed to**: Phase 5.3

### ✅ Checkpoint 3: After 5.3 (File Management)
- Run these commands:
  ```bash
  pytest tests/unit/test_validation.py
  pytest tests/unit/test_storage.py
  ```
- Verify: Invalid files rejected before storage
- Verify: Valid files uploaded to S3 or local storage
- **Can proceed to**: Phase 5.4

### ✅ Checkpoint 4: After 5.4 (Monitoring)
- Run these commands:
  ```bash
  pytest tests/unit/test_monitoring.py
  pytest tests/unit/test_logging.py
  pytest tests/integration/test_health.py
  ```
- Verify: Errors sent to Sentry
- Verify: Structured logs in JSON
- Verify: Health endpoint returns 200 with status
- **Can proceed to**: Phase 5.5

### ✅ Checkpoint 5: After 5.5 (Database)
- Run these commands:
  ```bash
  alembic upgrade head
  alembic downgrade -1
  alembic upgrade head
  pytest tests/integration/test_migrations.py
  pytest tests/integration/test_db_resilience.py
  ```
- Verify: Migrations apply and rollback cleanly
- Verify: No data loss during rollback
- **Can proceed to**: Phase 5.6

### ✅ Checkpoint 6: After 5.6 (Deployment)
- Run these commands:
  ```bash
  ./scripts/deploy.sh staging
  curl http://localhost:8000/health
  ./scripts/rollback.sh staging
  pytest tests/unit/test_feature_flags.py
  ```
- Verify: Can deploy to staging
- Verify: Health check passes after deploy
- Verify: Rollback works
- Verify: Feature flags work
- **Status**: Ready for production deployment!

---

## TASK DEPENDENCY GRAPH

```
5.1.1 Secrets ──────┐
5.1.2 Env Validation┤
                    ├──→ 5.2.1 API Key Auth
5.2.2 Rate Limiting ┤    (Auth middleware)
                    │
                    ├──→ 5.3.1 File Validation
                    ├──→ 5.3.2 S3 Storage
                    │
5.4.1 Sentry ──────┤    ├──→ 5.4.2 Logging
5.4.3 Health Check┤    │    ├──→ 5.5.1 Migrations
                    │    ├──→ 5.5.2 Connection Pool
5.6.1 Deploy ──────├────├──→ 5.6.2 Feature Flags
5.6.2 Feature Flags┤
```

**Key Dependencies:**
- Everything depends on 5.1 (secrets)
- 5.3 depends on 5.2 (auth must be in place before file operations)
- 5.5 depends on 5.4 (monitoring)
- 5.6 depends on 5.5 (migrations must work)

---

## IMPLEMENTATION APPROACH

**Sequential Order** (recommended for single agent):
1. 5.1.1 → 5.1.2 → 5.2.1 → 5.2.2 → 5.3.1 → 5.3.2
2. → 5.4.1 → 5.4.2 → 5.4.3 → 5.5.1 → 5.5.2
3. → 5.6.1 → 5.6.2

**Parallel Opportunities** (if multiple agents):
- While one agent does 5.1-5.2, another can start 5.4-5.5 prep
- Phase 5.6 tasks can start after 5.5 (no hard blocking dependency)

**Timeline**:
- ~1 hour per task
- 13 tasks × 1 hour = **~13 hours total**
- **Realistic estimate: 2-3 days** (accounting for debugging and testing)

---

## SUMMARY

Each of the 13 tasks above:
- ✅ Has clear acceptance criteria
- ✅ Is completable in 1-2 hours
- ✅ Includes verification steps
- ✅ Depends only on previous tasks in sequence
- ✅ Leaves the system in a working state

After completing all 13 tasks, LifeText will be **production-ready**.

**Next phase after Phase 5**: Phase 6 (Multi-user support, advanced features)

