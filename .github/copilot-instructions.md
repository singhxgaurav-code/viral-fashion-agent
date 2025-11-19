# Viral Fashion Agent - AI Coding Instructions

## Project Overview
Autonomous multi-platform content creator that generates 10 daily fashion videos, distributing them across YouTube Shorts, TikTok, Instagram Reels, Twitter, and Facebook. The system uses free-tier AI APIs (Groq), scrapes trends from multiple sources, generates scripts, creates videos with TTS/stock media, and auto-uploads to 5+ platforms.

## Architecture Flow
```
TrendDetector → ContentGenerator → MediaCreator → MultiPlatformUploader → Database
```

**Daily Workflow (main.py):**
1. Detect trends from Reddit/Twitter/Google Trends/TikTok
2. Generate AI scripts using Groq LLM (Llama 3.1)
3. Create videos: Edge-TTS voiceover + Pexels/Unsplash media + MoviePy editing
4. Upload to all platforms in parallel (ThreadPoolExecutor)
5. Track analytics in SQLite database

## Key Components

### 1. TrendDetector (src/trend_detector.py)
- **Aggregates** trends from 4 sources with deduplication
- **Filters** by fashion keywords and engagement thresholds (100+ Reddit score, 50+ Twitter engagement)
- **Returns** scored list: `{source, title, keywords, score, timestamp}`
- Uses `praw` for Reddit, `tweepy` for Twitter, `pytrends` for Google

### 2. ContentGenerator (src/content_generator.py)
- **Groq model**: `llama-3.1-70b-versatile` for fast, high-quality scripts
- **Script structure**: Hook (from templates) → 3 tips → CTA (45-sec target, ~112 words)
- **Metadata generation**: Title (60 chars), description, 10 hashtags, 5 keywords
- Platform optimization: `optimize_for_platform()` adapts metadata per platform

### 3. MediaCreator (src/media_creator.py)
- **TTS engine**: Edge-TTS (free Microsoft voices: Jenny, Guy, Sonia, Natasha)
- **Stock media**: Pexels API (videos) → Unsplash API (images fallback)
- **Editing**: MoviePy pipeline - fetch clips → trim to audio duration → add captions → branding
- **Captions**: Word-by-word (3 words/caption), white text with black stroke, bottom 75%
- **Output**: 1080x1920 vertical MP4, 30fps, H.264/AAC

### 4. MultiPlatformUploader (src/uploaders/)
- **Base pattern**: All uploaders inherit `BasePlatformUploader` (authenticate, upload, get_analytics)
- **Parallel uploads**: `ThreadPoolExecutor` uploads to all platforms simultaneously
- **Platform limits**: YouTube (256MB, 60s), TikTok (287MB, 60s), Instagram (100MB, 90s)
- **Authentication**:
  - YouTube: OAuth 2.0 with token refresh (pickle cache: `youtube_token.pickle`)
  - Instagram: Username/password via `instagrapi`
  - Twitter: OAuth 1.0a
  - Facebook: Page access token
  - TikTok: Session ID (no official API)

### 5. Database (src/database.py)
- **SQLite** at `data/agent.db`
- **Tables**: trends, videos, uploads, analytics
- **Key queries**: `get_platform_performance()`, `get_total_analytics()`, `get_recent_uploads()`

## Development Patterns

### Configuration
- **All settings** in `config.py` (imports from `.env`)
- **Platform configs**: `config.PLATFORMS[platform]['enabled']` to toggle platforms
- **Fashion niches**: `config.FASHION_NICHES` list (13 categories)
- **Content templates**: Hooks and CTAs in `config.CONTENT_TEMPLATES`

### Error Handling
- **Try-catch per component**: Each platform upload wrapped in try-except
- **Fallback mechanisms**: If AI fails → use `_fallback_script()`, if Pexels fails → Unsplash → simple slideshow
- **Logging**: `logging.getLogger(__name__)` in all modules, logs to `agent.log` + console

### Running the Agent
```bash
python main.py test      # One-time test run (10 videos)
python main.py analytics # Update metrics from all platforms
python main.py report    # Performance summary
python main.py           # Scheduled mode (daily 6 AM + analytics every 6h)
```

### Testing Workflow
1. **Single trend test**: Modify `config.DAILY_VIDEOS_COUNT = 1` for faster testing
2. **Mock uploads**: Comment out platform uploaders in `src/uploaders/__init__.py`
3. **Check logs**: Tail `agent.log` for detailed execution flow

## Common Tasks

### Adding a New Platform
1. Create `src/uploaders/newplatform.py` inheriting `BasePlatformUploader`
2. Implement `authenticate()`, `upload()`, `get_analytics()`
3. Add to `config.PLATFORMS` with specs (max_file_size_mb, max_duration)
4. Register in `MultiPlatformUploader._initialize_uploaders()`

### Changing AI Model
- **Edit**: `ContentGenerator.model = "llama-3.1-70b-versatile"` (other options: `mixtral-8x7b`, `llama-3.1-8b-instant`)
- **Groq free tier**: 14,400 requests/day across all models

### Customizing Video Style
- **Captions**: Modify `MediaCreator.add_captions()` for font/position/animation
- **Branding**: Edit `MediaCreator.add_branding()` watermark text/position
- **Transitions**: Add between clips in `create_video()` before `concatenate_videoclips()`

### API Rate Limit Handling
- **Pexels**: 200 req/hr → if exceeded, falls back to Unsplash (50 req/hr)
- **YouTube**: 10K quota/day (~6 uploads) → request increase at Google Console
- **Twitter**: 1,500 tweets/month free → upgrade to Basic ($100/mo) if needed
- **Groq**: 14,400 req/day → each video uses 2 requests (script + metadata)

## Critical File Paths
- **OAuth tokens**: `youtube_token.pickle`, `instagram_session.json` (git-ignored)
- **Client secrets**: `client_secrets.json` for YouTube OAuth (download from Google Console)
- **Environment**: `.env` loaded via `python-dotenv` in `config.py`
- **Output**: Videos saved to `config.OUTPUT_DIR` (`output/videos/` by default)

## Dependencies
- **Video**: `moviepy`, `opencv-python`, `Pillow`, `imageio-ffmpeg` (requires FFmpeg installed)
- **AI**: `groq`, `openai` (fallback)
- **TTS**: `edge-tts` (async), `TTS` (Coqui), `gTTS` (simple)
- **Uploads**: `google-api-python-client`, `instagrapi`, `TikTokApi`, `tweepy`, `facebook-sdk`

## Debugging Tips
- **MoviePy errors**: Ensure FFmpeg installed (`brew install ffmpeg` on macOS)
- **API auth failures**: Check `.env` keys, regenerate tokens if expired
- **Video upload failures**: Validate file size/duration with `BasePlatformUploader.validate_video()`
- **Trend deduplication**: Adjust similarity threshold in `TrendDetector._deduplicate_trends()` (currently 0.7)

## Code Style Conventions
- **Imports**: Standard lib → third-party → local (with blank lines between)
- **Logging**: Use `logger.info()` for progress, `logger.error()` for failures, include emojis for user-facing logs (✅❌📊)
- **Type hints**: Function signatures include types: `def function(arg: Type) -> ReturnType`
- **Config access**: Always use `config.VARIABLE`, never hardcode values
- **Database**: Use context managers (`with sqlite3.connect()`) for auto-commit/close

## Testing & Quality

### Running Tests
```bash
# Run all tests with coverage
pytest

# Run specific test file
pytest tests/test_database.py

# Run with verbose output
pytest -v

# Run and show coverage report
pytest --cov=src --cov-report=term-missing

# Generate HTML coverage report
pytest --cov=src --cov-report=html
```

### Test Structure
- **Location**: All tests in `tests/` directory
- **Naming**: Test files: `test_*.py`, Test classes: `Test*`, Test functions: `test_*`
- **Coverage target**: 85% minimum (enforced by `pytest.ini`)
- **Fixtures**: Common fixtures in `tests/conftest.py` (sample_trend, sample_metadata, mock clients)

### Writing Tests
- **Unit tests**: Mock external dependencies (APIs, file I/O, database)
- **Use fixtures**: Leverage `conftest.py` fixtures for consistent test data
- **Mock patterns**:
  - Groq API: `@patch('src.content_generator.Groq')`
  - MoviePy: `@patch('src.media_creator.VideoFileClip')`
  - Platform APIs: Mock `authenticate()` and `upload()` methods
- **Test categories**:
  - Happy path (successful operations)
  - Error handling (API failures, invalid input)
  - Edge cases (empty data, rate limits, validation failures)

### Coverage by Component
- **TrendDetector**: Trend fetching, deduplication, keyword extraction
- **ContentGenerator**: Script generation, metadata formatting, platform optimization
- **MediaCreator**: TTS generation, video assembly, caption/branding
- **Database**: CRUD operations, analytics aggregation
- **Uploaders**: Platform-specific upload logic, authentication, analytics fetching
- **Main**: Workflow orchestration, command-line interface

## Security Notes
- **Never commit** `.env`, `*_token.pickle`, `*_session.json` (in `.gitignore`)
- **API keys**: Rotate periodically, use read-only scopes where possible
- **GitHub Actions**: Use repository secrets for CI/CD environment variables
