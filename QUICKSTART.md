# Quick Start Guide - Running the Viral Fashion Agent

## ✅ Setup Complete!

Your environment is now ready with:
- Python 3.12 with virtual environment (`venv/`)
- All dependencies installed (99 packages)
- FFmpeg installed for video processing

## 🚀 Quick Demo (No API Keys Needed Initially)

### Option 1: Try the Simple Demo
```bash
# Activate virtual environment
source venv/bin/activate

# Run simple demo (generates 1 video, no uploads)
python demo.py
```

This will:
1. Use a sample fashion trend
2. Try to generate AI script (requires GROQ_API_KEY)
3. Create a video with TTS and stock media
4. Save to `output/videos/`

### Option 2: Full Test Run
```bash
# Activate virtual environment
source venv/bin/activate

# Run full test (10 videos, attempts uploads)
python main.py test
```

## 🔑 Required API Keys

### Minimum for Video Generation:
1. **Groq** (Free, Required for AI scripts)
   - Sign up: https://console.groq.com/
   - Get API key (14,400 requests/day free)
   - Add to `.env`: `GROQ_API_KEY=gsk_your_key_here`

2. **Pexels** (Free, for stock videos)
   - Sign up: https://www.pexels.com/api/
   - Get API key (200 requests/hour free)
   - Add to `.env`: `PEXELS_API_KEY=your_key_here`

3. **Unsplash** (Free, fallback for images)
   - Sign up: https://unsplash.com/developers
   - Get access key (50 requests/hour free)
   - Add to `.env`: `UNSPLASH_ACCESS_KEY=your_key_here`

### Optional for Platform Uploads:

#### YouTube Shorts
- Set up OAuth 2.0 at Google Cloud Console
- Download `client_secrets.json`
- Run: `python main.py test` (will open browser for auth)

#### Instagram Reels
- Add to `.env`:
  ```
  INSTAGRAM_USERNAME=your_username
  INSTAGRAM_PASSWORD=your_password
  ```

#### TikTok
- Get session ID from browser (complex, see SETUP_GUIDE.md)
- Add to `.env`: `TIKTOK_SESSION_ID=your_session_id`

#### Twitter/X
- Create app at https://developer.twitter.com/
- Add credentials to `.env`:
  ```
  TWITTER_CONSUMER_KEY=your_key
  TWITTER_CONSUMER_SECRET=your_secret
  TWITTER_ACCESS_TOKEN_POST=your_token
  TWITTER_ACCESS_SECRET_POST=your_secret
  ```

#### Facebook Reels
- Get Page access token from Meta for Developers
- Add to `.env`:
  ```
  FACEBOOK_PAGE_ID=your_page_id
  FACEBOOK_ACCESS_TOKEN=your_token
  ```

## 📝 Setup Environment File

```bash
# Copy demo template
cp .env.demo .env

# Edit with your API keys
nano .env
# or
code .env
```

**Minimum .env for testing:**
```env
# Required for AI content
GROQ_API_KEY=gsk_your_groq_key

# Required for video media
PEXELS_API_KEY=your_pexels_key
UNSPLASH_ACCESS_KEY=your_unsplash_key

# Agent settings
DAILY_VIDEOS_COUNT=1
LOG_LEVEL=INFO
OUTPUT_DIR=output/videos
```

## 🎬 Running the Agent

### 1. Test Mode (One-time, 10 videos)
```bash
source venv/bin/activate
python main.py test
```

### 2. Analytics Update
```bash
python main.py analytics
```

### 3. Performance Report
```bash
python main.py report
```

### 4. Scheduled Mode (Daily at 6 AM)
```bash
python main.py
```

## 🧪 Running Tests

```bash
# Activate environment
source venv/bin/activate

# Run all tests with coverage
pytest

# Run specific test file
pytest tests/test_content_generator.py

# Run with verbose output
pytest -v

# Generate HTML coverage report
pytest --cov=src --cov-report=html
open htmlcov/index.html
```

## 📁 Project Structure

```
viral-fashion-agent/
├── venv/                    # Virtual environment ✅
├── output/videos/           # Generated videos
├── data/agent.db           # SQLite database
├── .env                    # Your API keys (create this)
├── .env.demo              # Template ✅
├── demo.py                # Simple demo script ✅
├── main.py                # Main agent
├── config.py              # Configuration
├── src/
│   ├── trend_detector.py
│   ├── content_generator.py
│   ├── media_creator.py
│   ├── database.py
│   └── uploaders/
└── tests/                 # 87 unit tests ✅

✅ = Already set up
```

## 🎯 Next Steps

1. **Get Groq API Key** (5 minutes)
   - Visit: https://console.groq.com/
   - Sign up with email
   - Click "API Keys" → "Create API Key"
   - Copy key to `.env`

2. **Get Pexels API Key** (2 minutes)
   - Visit: https://www.pexels.com/api/
   - Sign up
   - Copy API key to `.env`

3. **Get Unsplash Access Key** (2 minutes)
   - Visit: https://unsplash.com/developers
   - Create application
   - Copy access key to `.env`

4. **Run Demo**
   ```bash
   source venv/bin/activate
   python demo.py
   ```

## 🐛 Troubleshooting

### "ModuleNotFoundError"
```bash
source venv/bin/activate  # Activate venv first!
```

### "FFmpeg not found"
```bash
which ffmpeg  # Should show: /opt/homebrew/bin/ffmpeg
```

### "API key invalid"
- Check `.env` file exists in project root
- Verify no spaces around `=` in `.env`
- Restart terminal/reload environment

### "No videos generated"
- Check logs: `tail -f agent.log`
- Verify API keys are valid
- Check internet connection

## 📊 Expected Output

After running `python demo.py` successfully:

```
🎬 Viral Fashion Agent - Demo Mode
==================================================

📊 Step 1: Detecting fashion trends...
✅ Found trend: Oversized Blazers Fall 2024

✍️  Step 2: Generating AI script...
✅ Generated script: '3 Ways to Style Oversized Blazers This Fall'

📝 Script Preview:
--------------------------------------------------
Want to know the secret to looking effortlessly 
chic this fall? Let me show you how to style...
--------------------------------------------------
📊 Metadata:
  - Hashtags: #fashion, #style, #ootd, #falltrends, #blazer
  - Duration: ~45s

🎥 Step 3: Creating video...
✅ Video created: output/videos/video_123456.mp4

📹 Video Details:
  - Path: output/videos/video_123456.mp4
  - Size: 8.45 MB
  - Format: 1080x1920 (vertical)
  - Database ID: 1

📤 Step 4: Platform Upload (DEMO - SKIPPED)
  ⏭️  Skipping uploads

==================================================
✅ Demo completed successfully!

🎉 Your video is ready: output/videos/video_123456.mp4
```

## 🎉 Success!

You're now ready to generate viral fashion content! 🚀
