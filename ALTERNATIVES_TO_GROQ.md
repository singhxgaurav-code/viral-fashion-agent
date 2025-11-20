# Alternative AI Providers for Corporate Networks

## Problem
Your corporate network (Zscaler) is blocking external API calls to:
- `api.groq.com` (Groq AI)
- `api-inference.huggingface.co` (HuggingFace)
- Potentially other cloud AI services

## Solutions

### Option 1: OpenAI (Recommended for Corporate Networks) ✅
**Why it works:** OpenAI has better corporate network compatibility and is less likely to be blocked.

**Cost:** $5 free credits for new accounts, then pay-as-you-go
- GPT-3.5-Turbo: ~$0.002 per 1K tokens (cheap)
- For 10 videos/day: ~$0.50-1.00/month

**Setup:**
```bash
# 1. Get API key from https://platform.openai.com/api-keys
# 2. Add to .env
echo "OPENAI_API_KEY=sk-your-key-here" >> .env

# 3. Test connection
python -c "import openai; client = openai.OpenAI(api_key='your-key'); print(client.models.list())"
```

**Already integrated!** The code now automatically tries:
1. Groq (if available)
2. **OpenAI** ← This will work through Zscaler
3. HuggingFace (if not blocked)
4. Ollama (local)
5. Fallback templates (no AI)

### Option 2: Ollama (Completely Offline) 🏠
**Why it works:** Runs 100% locally, no internet required.

**Cost:** Free forever

**Setup:**
```bash
# 1. Install Ollama (Mac)
brew install ollama

# 2. Start Ollama service
ollama serve

# 3. Download a model (in another terminal)
ollama pull llama2
# or for better quality:
ollama pull mistral

# 4. Enable in .env
echo "OLLAMA_ENABLED=true" >> .env
echo "OLLAMA_BASE_URL=http://localhost:11434" >> .env

# 5. Test
curl http://localhost:11434/api/generate -d '{
  "model": "llama2",
  "prompt": "Write a fashion tip"
}'
```

**Trade-offs:**
- ✅ No network issues
- ✅ Free forever
- ✅ Private (data never leaves your machine)
- ❌ Slower than cloud APIs (depends on your Mac's CPU/GPU)
- ❌ Requires ~4GB disk space per model

### Option 3: VPN/Proxy Bypass (If Allowed) ⚠️
**WARNING:** Check your company's IT policy first!

```bash
# If using VPN
export https_proxy=http://your-vpn:port

# Or run in Docker without corporate proxy
docker run -it --network=host viral-fashion-agent python main.py
```

### Option 4: Template-Only Mode (No AI) 📝
**Already built-in!** If all providers fail, the system uses hardcoded templates:

```python
# Automatic fallback happens in:
# - src/content_generator.py::_fallback_script()
# - src/content_generator.py::_fallback_metadata()
```

**Trade-offs:**
- ✅ Works anywhere
- ✅ Fast
- ❌ Less viral/engaging content
- ❌ Repetitive

## Testing Which Providers Work

Run this diagnostic:
```bash
cd /Users/gaurav.singh/Downloads/viral-fashion-agent
source venv/bin/activate

# Test Groq
python -c "from groq import Groq; print(Groq(api_key='test').models.list())" 2>&1 | grep -q "Zscaler" && echo "❌ Groq BLOCKED" || echo "✅ Groq OK"

# Test OpenAI
python -c "import openai; openai.OpenAI(api_key='sk-test').models.list()" 2>&1 | grep -q "Zscaler" && echo "❌ OpenAI BLOCKED" || echo "✅ OpenAI OK"

# Test Ollama (if installed)
curl -s http://localhost:11434/api/tags 2>&1 | grep -q "error" && echo "❌ Ollama NOT RUNNING" || echo "✅ Ollama OK"
```

## Recommended Setup for Corporate Networks

**Best combination:**
1. **Primary:** OpenAI (add API key to `.env`)
2. **Fallback:** Ollama (install locally for offline use)
3. **Emergency:** Built-in templates (automatic)

**Steps:**
```bash
# 1. Get OpenAI key
open https://platform.openai.com/api-keys

# 2. Add to .env
nano .env
# Add: OPENAI_API_KEY=sk-proj-...

# 3. (Optional) Install Ollama for offline backup
brew install ollama
ollama serve &
ollama pull mistral

# 4. Test the agent
python main.py test
```

## Current Provider Priority

After these changes, the system tries providers in this order:

```
1. Groq (llama-3.1-70b-versatile)
   ↓ fails
2. OpenAI (gpt-3.5-turbo) ← ADD YOUR KEY HERE
   ↓ fails
3. HuggingFace (mistralai/Mistral-7B)
   ↓ fails
4. Ollama (llama2/mistral - local)
   ↓ fails
5. Template fallback (no AI)
```

## Cost Comparison

| Provider | Setup Cost | Monthly Cost (10 videos/day) | Network |
|----------|------------|------------------------------|---------|
| Groq | Free | Free (14,400 req/day) | ❌ Blocked |
| OpenAI | $5 credit | ~$0.50-1.00 | ✅ Usually works |
| HuggingFace | Free | Free (rate limited) | ❌ Blocked |
| Ollama | Free | Free | ✅ Offline |
| Templates | Free | Free | ✅ Always works |

## Next Steps

1. **Try OpenAI first** - Most likely to work through Zscaler
2. **Install Ollama as backup** - For complete offline capability  
3. **Test with:** `python main.py test` (generates 1 video)
4. **Monitor logs** in `agent.log` to see which provider succeeded

## Questions?

- OpenAI API issues: https://platform.openai.com/docs
- Ollama setup: https://ollama.ai/
- Check provider status in logs: `tail -f agent.log | grep "provider"`
