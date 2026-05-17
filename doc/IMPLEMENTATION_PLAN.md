# LifeText MVP Implementation Plan

## Overview

Backend FastAPI + worker pipeline untuk LifeText MVP. System menerima file audio/video, menghasilkan transcript bersih, dan mengembalikannya ke client — end-to-end, tanpa intervensi manual.

## Phase 0: Setup ✅ DONE

- ✅ Create project structure
- ✅ Setup FastAPI + Celery + PostgreSQL
- ✅ Database models (Job)
- ✅ Configuration (.env, docker-compose)
- ✅ Create all prompt files
- ✅ Basic tests

**Verification:**
- ✅ `docker-compose up` starts all services
- ✅ API responds at http://localhost:8000/health
- ✅ PostgreSQL and Redis are healthy

## Phase 1: ASR Service 🔄 IN PROGRESS

**Objective**: Whisper integration untuk transcribe audio/video files

**Tasks:**

1. **Implement ASR service**
   - ✅ `services/asr.py` dengan Whisper integration
   - ✅ Audio extraction dari video (ffmpeg)
   - ✅ Model caching
   - ✅ Format detection

2. **Create transcribe endpoint**
   - ✅ `POST /transcribe` untuk file upload
   - ✅ Store file, create job record
   - ✅ Enqueue Celery task
   - ✅ Return job_id immediately

3. **Implement worker**
   - ✅ `transcript_worker.py` - Main transcription task
   - Extract audio jika perlu
   - Transcribe dengan Whisper
   - Store raw transcript

4. **Create status endpoint**
   - ✅ `GET /jobs/{job_id}` untuk polling
   - Return job status, transcript, quality_score

5. **Test ASR**
   - ✅ Test format detection
   - [ ] Test Whisper integration (manual - requires audio file)
   - [ ] Test worker task (manual - requires Redis)
   - Test API endpoints

**Acceptance Criteria:**
- [ ] Can upload MP3 and MP4 files
- [ ] Whisper transcribes to raw_transcript
- [ ] Job polling returns current status
- [ ] Tests pass: `pytest tests/test_asr.py`

**Verification:**
```bash
pytest tests/test_asr.py -v
pytest tests/test_api.py -v
```

## Phase 2: Post-process & Quality

**Objective**: Claude post-processing untuk clean transcript + quality scoring

**Tasks:**

1. **Post-process service**
   - Load `prompts/system_transcription.txt`
   - Call Claude API dengan raw_transcript
   - Handle filler removal, punctuation, ASR error correction
   - Return clean_transcript

2. **Quality check service**
   - Load quality check prompt
   - Analyze clean_transcript
   - Return quality_score (1-10)
   - Flag ambiguous sections (flag_review=true)

3. **Integrate into worker**
   - After Whisper, call post-process
   - After post-process, call quality check
   - Update job.clean_transcript, quality_score, flag_review

4. **Test post-process**
   - Test Claude API integration
   - Test quality scoring
   - Test error handling (API rate limits, timeouts)

**Acceptance Criteria:**
- [ ] clean_transcript is polished (no fillers, proper punctuation)
- [ ] quality_score between 1-10
- [ ] flag_review set for low-quality segments
- [ ] Tests pass

## Phase 3: Job System

**Objective**: PostgreSQL job tracking + Celery async processing

**Tasks:**

1. **Database schema**
   - ✅ Job model created
   - Ensure all fields present (see CLAUDE.md)

2. **Update job helper**
   - Create `models/job.py` helper functions
   - `update_job(job_id, status, fields)`
   - Handle transactions safely

3. **Celery worker**
   - ✅ Basic worker created
   - Add error handling + retry logic
   - Exponential backoff untuk Claude API

4. **API routes**
   - ✅ `POST /transcribe` - upload + enqueue
   - ✅ `GET /jobs/{job_id}` - status + result
   - Status: queued → processing → done/failed

5. **Test job system**
   - Test job creation
   - Test status transitions
   - Test error handling

**Acceptance Criteria:**
- [ ] File upload → job created → queued
- [ ] Job polling shows progress
- [ ] Job completes: status=done, clean_transcript available
- [ ] Tests pass

## Phase 4: Intelligence Endpoints

**Objective**: Smart features (meeting notes, quotes, dll)

**Tasks:**

1. **Intelligence service**
   - Mode routing: meeting_notes, quotes, translate, etc
   - Load appropriate prompt dari `prompts/`
   - Call Claude dengan clean_transcript
   - Return mode-specific output

2. **Intelligence router**
   - `POST /intelligence/{mode}` endpoint
   - Validate job exists + has clean_transcript
   - Enqueue intelligence task

3. **Test intelligence**
   - Test each mode: meeting_notes, quotes, etc
   - Test output format

**Acceptance Criteria:**
- [ ] Meeting notes mode extracts action items
- [ ] Quotes mode returns 5-10 quotable statements
- [ ] All modes return properly formatted output

## Phase 5: In-App Chat

**Objective**: In-app AI assistant untuk user guidance

**Tasks:**

1. **Chat endpoint**
   - `POST /chat` - Send message
   - Stateless (no conversation history for MVP)

2. **Chat service**
   - Load `prompts/system_qa_chat.txt`
   - Call Claude dengan user message
   - Validate response scope (only LifeText topics)
   - Return response

3. **Test chat**
   - Test various user queries
   - Verify scope boundaries (reject off-topic questions)

**Acceptance Criteria:**
- [ ] Chat responds to LifeText-related questions
- [ ] Rejects off-topic questions politely
- [ ] Tests pass

## Success Criteria (MVP Done)

- [ ] Can upload MP3 and MP4 files
- [ ] Whisper transcribes end-to-end
- [ ] Clean transcript available immediately after processing
- [ ] Quality score calculated + low-quality flagged
- [ ] Meeting notes mode works
- [ ] Job polling accurate (queued → processing → done)
- [ ] All tests passing
- [ ] No prompts hardcoded (all loaded from files)

## Timeline

- **Phase 0**: ✅ DONE
- **Phase 1**: 🔄 IN PROGRESS (tests passing, manual verification needed)
- **Phase 2**: TODO (2-3 days)
- **Phase 3**: TODO (1-2 days)
- **Phase 4**: TODO (2-3 days)
- **Phase 5**: TODO (1 day)

**Total MVP**: ~7-10 days

## Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| Whisper model large (1GB) | Use smaller model for MVP (base), cache on disk |
| Claude API rate limits | Implement retry with exponential backoff |
| File uploads large | Stream uploads, validate size early, timeout protection |
| Database connection issues | Pool management, connection health checks |
| Worker crashes | Task persistence in Redis, retry mechanism |
