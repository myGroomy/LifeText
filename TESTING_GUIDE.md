# LifeText Testing Guide

**Status**: Ready to Test  
**Date**: May 17, 2026  
**Your .env**: Already created and configured

---

## 📋 Quick Summary

| Question | Answer |
|----------|--------|
| **What should I test?** | The LifeText application |
| **What do I submit?** | Test results (NOT .env file) |
| **What's .env for?** | Holds API keys and configuration (keep SECRET) |
| **Can I commit .env?** | NO! It's in .gitignore for security |
| **What's .env.example for?** | Template showing what variables needed (SAFE to commit) |
| **How long to test?** | 5-15 minutes depending on option chosen |

---

## 🎯 Choose Your Testing Option

### **OPTION 1: Quick Test (5 min) - Recommended for first time**

No setup needed. Tests code logic without external services.

```bash
cd LifeText
pip install pytest pytest-cov
pip install -r requirements.txt
pytest tests/ -v --cov=src
```

**What it tests:**
- ✅ Whisper ASR functionality
- ✅ File validation
- ✅ API response structure
- ✅ LLM provider integration
- ✅ Code quality

**Expected result:** All tests pass ✅

---

### **OPTION 2: Full System Test (15 min) - Complete testing**

Tests entire system including database and queue.

#### Step 1: Install Docker
Download from: https://www.docker.com/products/docker-desktop

#### Step 2: Start Services
```bash
cd LifeText
docker-compose up
```

Wait until you see:
```
api-1   | Uvicorn running on http://0.0.0.0:8000
worker-1 | celery@... ready to accept tasks
```

#### Step 3: Initialize Database (NEW TERMINAL)
```bash
cd LifeText
docker-compose exec api python scripts/init_db.py
```

#### Step 4: Run Tests
```bash
docker-compose exec api pytest tests/ -v --cov=src
```

#### Step 5: Test API Manually
```bash
# Check health
curl http://localhost:8000/health

# View API docs (in browser)
http://localhost:8000/docs

# Or use curl to test endpoints
curl -X POST http://localhost:8000/api/transcribe \
  -F "file=@/path/to/audio.mp3"
```

#### Step 6: Stop Services
```bash
docker-compose down
```

**What it tests:**
- ✅ Everything from Option 1
- ✅ Database connectivity
- ✅ Redis queue
- ✅ Celery workers
- ✅ Full transcription pipeline
- ✅ API endpoints
- ✅ File storage

**Expected result:** All services running, tests pass ✅

---

### **OPTION 3: Interactive API Testing**

Test the running API with real requests.

#### Prerequisites
- Option 2 running (docker-compose up)
- cURL or Postman installed

#### API Endpoints to Test

**Health Check**
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "environment": "development"
}
```

**Upload File** (need an audio file)
```bash
curl -X POST http://localhost:8000/api/transcribe \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/audio.mp3"
```

Expected response:
```json
{
  "job_id": "abc-123-def",
  "status": "queued"
}
```

**Get Job Status**
```bash
curl http://localhost:8000/api/jobs/abc-123-def
```

Wait for status to change from "queued" → "processing" → "done"

**Get Meeting Notes**
```bash
curl http://localhost:8000/api/intelligence/meeting-notes/abc-123-def
```

**Interactive Docs**
Visit in browser: http://localhost:8000/docs

This shows all endpoints with interactive testing UI.

---

## 📝 Understanding .env File

### What is .env?
- File containing environment variables (configuration)
- Holds API keys, database credentials, secrets
- NOT committed to git (in .gitignore)
- Each developer has their own .env with their own keys

### What's in Your .env?

```
DATABASE_URL=postgresql://lifetext:lifetext@localhost:5432/lifetext
REDIS_URL=redis://localhost:6379
LLM_PROVIDER=openai-compatible
LLM_API_KEY=ollama
LLM_MODEL=llama2
LLM_BASE_URL=http://localhost:11434/v1
WHISPER_MODEL_SIZE=base
APP_ENV=development
```

### What's in .env.example? (COMMITTED to git)

Template showing what variables are needed:
- No real API keys
- Placeholder values
- Safe to commit
- Shows other examples (OpenAI, Claude, Gemini)

### What Should You Submit?

✅ **DO SUBMIT:**
- Test results (console output)
- Screenshots of passing tests
- Health check response
- API documentation URL

❌ **DON'T SUBMIT:**
- Your .env file (contains your secrets)
- Any API keys or credentials
- Passwords or tokens

---

## 🔐 Security: Never Commit .env

The `.env` file is in `.gitignore` for a reason:

```
# In .gitignore:
.env              ← Your actual secrets (NEVER commit)
.env.example      ← Template (safe to commit)
```

If you accidentally commit .env:
1. Remove it: `git rm --cached .env`
2. Rotate your API keys
3. Never do it again!

---

## 🔄 Using Different LLM Providers

Your `.env` is configured for **Ollama** (free, local).

To use a different provider, edit `.env`:

### Option 1: OpenAI GPT-4
```env
LLM_PROVIDER=openai
LLM_API_KEY=sk-proj-YOUR-KEY-HERE
LLM_MODEL=gpt-4
```

### Option 2: Claude (Anthropic)
```env
LLM_PROVIDER=anthropic
LLM_API_KEY=sk-ant-YOUR-KEY-HERE
LLM_MODEL=claude-sonnet-4-20250514
```

### Option 3: Gemini
```env
LLM_PROVIDER=gemini
LLM_API_KEY=YOUR-GEMINI-API-KEY
LLM_MODEL=gemini-2.0-flash-exp
```

### Option 4: DeepSeek
```env
LLM_PROVIDER=deepseek
LLM_API_KEY=sk-YOUR-DEEPSEEK-KEY
LLM_MODEL=deepseek-chat
```

### Option 5: Ollama (Free, Local)
```env
LLM_PROVIDER=openai-compatible
LLM_API_KEY=ollama
LLM_MODEL=llama2
LLM_BASE_URL=http://localhost:11434/v1
```

---

## 📊 Expected Test Results

### Quick Test (Option 1)
```
collected 10 items
tests/test_api.py::test_health_check PASSED
tests/test_api.py::test_root_endpoint PASSED
tests/test_api.py::test_file_format_validation PASSED
tests/test_api.py::test_mp3_upload PASSED
tests/test_asr.py::test_format_detection PASSED
tests/test_asr.py::test_video_file_detection PASSED
tests/test_asr.py::test_whisper_model_loading PASSED
tests/test_asr.py::test_model_caching PASSED

====== 10 passed in 2.45s ======
```

### Full System Test (Option 2)
```
docker-compose up
  ✓ api service running
  ✓ worker service running
  ✓ database service running
  ✓ redis service running

docker-compose exec api pytest tests/ -v
  ====== 10 passed in 5.23s ======

Health check:
  curl http://localhost:8000/health
  ✓ {"status": "healthy"}
```

---

## 🆘 Troubleshooting

### Issue: "Module not found" error
**Fix**: Install dependencies
```bash
pip install -r requirements.txt
```

### Issue: "Database connection refused"
**Fix**: Make sure docker-compose is running
```bash
docker-compose up
```

### Issue: "No module named 'pytest'"
**Fix**: Install test dependencies
```bash
pip install pytest pytest-cov
```

### Issue: "LLM_API_KEY not found"
**Fix**: Make sure .env file exists in LifeText folder
```bash
cd LifeText
ls -la .env  # Should exist
```

### Issue: Docker port 5432 already in use
**Fix**: Stop conflicting service
```bash
docker ps
docker stop <container_id>
docker-compose up
```

---

## ✅ Submission Checklist

When you're done testing, submit:

- [ ] Test results (console output from pytest)
- [ ] Screenshot of passing tests
- [ ] Health check response
- [ ] Working API endpoint test
- [ ] Brief description of what was tested

**DO NOT SUBMIT:**
- [ ] .env file (keep it secret!)
- [ ] API keys
- [ ] Database credentials
- [ ] Any secrets or passwords

---

## 🎯 Next Steps After Testing

1. **Tests Pass? ✅**
   - Great! The application is working
   - Commit results to GitHub
   - Continue with Phase 5 implementation

2. **Tests Fail? ❌**
   - Check the error message
   - Refer to troubleshooting section
   - Ask for help with specific error

3. **Want to Test Phase 5?**
   - See: `doc/PHASE_5_TASKS.md`
   - Start with Task 5.1.1
   - Follow the implementation guide

---

## 📚 Additional Resources

- **Documentation**: See `doc/` folder
- **API Docs (live)**: http://localhost:8000/docs
- **Configuration**: `doc/LLM_CONFIGURATION.md`
- **Setup Guide**: `doc/COMPLETE_SETUP_GUIDE.md`
- **Phase 5**: `doc/PHASE_5_TASKS.md`

---

## 🎉 You're Ready to Test!

Choose Option 1, 2, or 3 above and start testing.

If you have questions, refer to this guide or check the documentation in `doc/` folder.

**Happy testing!** 🚀
