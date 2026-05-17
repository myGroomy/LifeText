# LLM Configuration Guide

LifeText supports ANY LLM provider. Choose based on your needs, cost, and preferences.

## Supported Providers

### 1. OpenAI (GPT-4, GPT-3.5)
```bash
# Install
pip install openai

# Configure in .env
LLM_PROVIDER=openai
LLM_API_KEY=sk-xxxxx
LLM_MODEL=gpt-4  # or gpt-3.5-turbo
```

**Pros:**
- Most capable, consistent output
- Widely used, mature ecosystem
- Good documentation

**Cons:**
- Most expensive ($0.01-0.03 per 1K tokens)
- API rate limits
- Requires internet

**Best for:** Production, high reliability needs

---

### 2. Anthropic (Claude)
```bash
# Install
pip install anthropic

# Configure in .env
LLM_PROVIDER=anthropic
LLM_API_KEY=sk-ant-xxxxx
LLM_MODEL=claude-sonnet-4-20250514  # or claude-opus, claude-haiku
```

**Pros:**
- Excellent reasoning, instruction following
- Good balance of cost vs capability
- Long context window

**Cons:**
- Moderate cost ($0.003-0.02 per 1K tokens)
- Slightly slower than GPT
- Requires internet

**Best for:** Default choice, good cost-benefit

---

### 3. Google (Gemini)
```bash
# Install
pip install google-generativeai

# Configure in .env
LLM_PROVIDER=gemini
LLM_API_KEY=your-api-key
LLM_MODEL=gemini-2.0-flash-exp  # or gemini-pro, gemini-1.5-pro
```

**Pros:**
- Fast, good quality
- Competitive pricing
- Good for multimodal (images, etc)

**Cons:**
- Newer, less tested than OpenAI/Claude
- API still evolving
- Requires internet

**Best for:** Cost-conscious, fast processing

---

### 4. DeepSeek (OpenAI-compatible)
```bash
# Install
pip install openai

# Configure in .env
LLM_PROVIDER=deepseek
LLM_API_KEY=sk-xxxxx
LLM_MODEL=deepseek-chat
```

**Pros:**
- Very cheap ($0.0001-0.0003 per 1K tokens!)
- Decent quality for price
- OpenAI-compatible API

**Cons:**
- Lower quality than GPT/Claude
- Smaller context window
- Requires internet

**Best for:** Budget-conscious, high volume

---

### 5. Ollama (Local, Free)
```bash
# Install Ollama first (ollama.ai)
ollama pull llama2  # or mistral, neural-chat, etc

# Start Ollama
ollama serve

# Configure in .env
LLM_PROVIDER=openai-compatible
LLM_API_KEY=ollama
LLM_MODEL=llama2  # or mistral, neural-chat
LLM_BASE_URL=http://localhost:11434/v1
```

**Pros:**
- Completely free
- No internet needed (private)
- Full control over model
- No rate limits

**Cons:**
- Requires local GPU/powerful CPU
- Quality lower than cloud models
- Setup overhead

**Best for:** Development, offline, privacy-critical

---

### 6. LM Studio (Local, Free)
```bash
# Download LM Studio (lmstudio.ai)
# Load a model (e.g., mistral-7b)
# Start local server (default: http://localhost:1234/v1)

# Configure in .env
LLM_PROVIDER=openai-compatible
LLM_API_KEY=not-needed
LLM_MODEL=model-name
LLM_BASE_URL=http://localhost:1234/v1
```

**Pros:**
- Free, easy UI
- Good for development/testing
- Works offline

**Cons:**
- Requires GPU
- Lower quality than cloud models

**Best for:** Development, experimentation

---

### 7. Any OpenAI-Compatible API
```bash
# Examples: LocalAI, text-generation-webui, llama-cpp-python, etc

LLM_PROVIDER=openai-compatible
LLM_API_KEY=your-api-key-if-required
LLM_MODEL=model-name
LLM_BASE_URL=http://your-server/v1
```

---

## Quick Decision Matrix

| Use Case | Provider | Cost | Quality | Speed |
|----------|----------|------|---------|-------|
| **Production** | OpenAI GPT-4 | $$$ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Best Default** | Claude Sonnet | $$ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Cost-Sensitive** | DeepSeek | $ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Fast & Good** | Gemini | $$ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Development** | Ollama (local) | Free | ⭐⭐⭐ | ⭐⭐⭐ |
| **Privacy** | Ollama (local) | Free | ⭐⭐⭐ | ⭐⭐ |

---

## Setup Examples

### Example 1: Using OpenAI GPT-4

```bash
# 1. Install dependencies
pip install openai

# 2. Get API key from platform.openai.com
# 3. Update .env
LLM_PROVIDER=openai
LLM_API_KEY=sk-proj-xxxxx
LLM_MODEL=gpt-4

# 4. Start services
docker-compose up

# 5. Test
curl -X POST "http://localhost:8000/api/transcribe" -F "file=@audio.mp3"
```

### Example 2: Using Claude (Anthropic)

```bash
# Already installed! Just configure:
LLM_PROVIDER=anthropic
LLM_API_KEY=sk-ant-xxxxx
LLM_MODEL=claude-sonnet-4-20250514

# Run
docker-compose up
```

### Example 3: Using Local Ollama

```bash
# 1. Install Ollama (ollama.ai)
# 2. Start Ollama server
ollama serve

# 3. In new terminal, pull model
ollama pull mistral

# 4. Configure .env
LLM_PROVIDER=openai-compatible
LLM_API_KEY=ollama
LLM_MODEL=mistral
LLM_BASE_URL=http://localhost:11434/v1

# 5. Start LifeText
docker-compose up

# 6. Test
curl -X POST "http://localhost:8000/api/transcribe" -F "file=@audio.mp3"
```

### Example 4: Using DeepSeek (Cheapest)

```bash
# 1. Get API key from deepseek.com
# 2. Configure .env
LLM_PROVIDER=deepseek
LLM_API_KEY=sk-xxxxx
LLM_MODEL=deepseek-chat

# 3. Run
docker-compose up
```

---

## Provider Features Matrix

| Feature | OpenAI | Claude | Gemini | DeepSeek | Ollama | LM Studio |
|---------|--------|--------|--------|----------|--------|-----------|
| **Vision (images)** | ✅ | ❌ | ✅ | ❌ | ❌ | ❌ |
| **Long context** | ❌ | ✅ (200K) | ✅ (128K) | ✅ (8K) | ✅ | ✅ |
| **Function calling** | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| **Streaming** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Batch processing** | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Internet required** | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |

---

## Cost Comparison (per 1M tokens)

| Provider | Input | Output | Notes |
|----------|-------|--------|-------|
| **OpenAI GPT-4** | $30 | $60 | Most expensive |
| **OpenAI GPT-3.5** | $0.50 | $1.50 | Budget option |
| **Claude Sonnet** | $3 | $15 | Good default |
| **Claude Haiku** | $0.25 | $1.25 | Cheapest Claude |
| **Gemini Pro** | $0.50 | $1.50 | Competitive |
| **DeepSeek** | $0.10 | $0.30 | Cheapest |
| **Ollama** | Free | Free | Requires GPU |

---

## Switching Providers

To switch providers, just edit `.env`:

```bash
# Before (Claude)
LLM_PROVIDER=anthropic
LLM_API_KEY=sk-ant-xxxxx
LLM_MODEL=claude-sonnet-4-20250514

# After (GPT-4)
LLM_PROVIDER=openai
LLM_API_KEY=sk-proj-xxxxx
LLM_MODEL=gpt-4
```

No code changes needed! Restart the API and it uses the new provider.

---

## Troubleshooting

### "Module not found" error
**Solution**: Install the provider's package
```bash
pip install openai anthropic google-generativeai
```

### API key invalid
**Solution**: Check your API key format and that it's in .env correctly
```bash
# Check .env syntax
cat .env | grep LLM_API_KEY
```

### Rate limit error
**Solution**: Add retry logic (already in worker, uses exponential backoff)

### Model not found
**Solution**: Check model name is correct for your provider
```bash
# OpenAI: gpt-4, gpt-3.5-turbo
# Claude: claude-sonnet-4-20250514, claude-opus, claude-haiku
# Gemini: gemini-2.0-flash-exp, gemini-pro, gemini-1.5-pro
```

### Local Ollama connection refused
**Solution**: Make sure Ollama is running
```bash
# Start Ollama
ollama serve

# In another terminal, test
curl http://localhost:11434/api/tags
```

---

## Production Recommendations

1. **Use Claude or OpenAI** for reliability
2. **Set up monitoring** for API usage and errors
3. **Use exponential backoff** for retries (already implemented)
4. **Cache responses** when possible (future feature)
5. **Test failover** to another provider
6. **Monitor costs** - track API spending

---

## Adding New Providers

To add a new provider (e.g., Azure OpenAI):

1. Create class in `src/services/llm_provider.py`:
```python
class AzureOpenAIProvider(LLMProvider):
    def __init__(self, api_key: str, model: str, endpoint: str):
        # Initialize Azure client
        
    def complete(self, system_prompt, user_prompt, temperature, max_tokens):
        # Call Azure API
```

2. Add to `get_llm_provider()` factory function

3. Update `.env.example` with new settings

4. Test end-to-end

---

**Done!** You can now use any LLM provider with LifeText.
