# Test Suite for Viral Fashion Agent

Comprehensive unit test suite with 85%+ coverage target.

## Quick Start

```bash
# Install test dependencies
pip install -r requirements.txt

# Run all tests
pytest

# Run with coverage report
pytest --cov=src --cov-report=term-missing

# Run specific test file
pytest tests/test_database.py

# Run tests matching pattern
pytest -k "test_upload"
```

## Test Files

- `conftest.py` - Shared fixtures and test configuration
- `test_trend_detector.py` - Trend scraping and aggregation (15 tests)
- `test_content_generator.py` - AI script generation and metadata (14 tests)
- `test_database.py` - SQLite operations and analytics (14 tests)
- `test_uploaders.py` - Platform upload and authentication (18 tests)
- `test_media_creator.py` - Video creation pipeline (11 tests)
- `test_main.py` - Workflow orchestration (11 tests)

**Total: 83 tests**

## Coverage Target

Minimum 85% code coverage enforced by `pytest.ini`.

View coverage report:
```bash
pytest --cov=src --cov-report=html
open htmlcov/index.html
```

## Common Fixtures

From `conftest.py`:
- `temp_dir` - Temporary directory for file operations
- `sample_trend` - Mock trend data
- `sample_metadata` - Mock video metadata
- `sample_script` - Sample video script
- `mock_groq_client` - Mocked Groq API client
- `mock_video_clip` - Mocked MoviePy VideoFileClip
- `test_video_path` - Dummy video file
- `mock_database` - Temporary test database

## Writing New Tests

1. Create test file: `tests/test_<module>.py`
2. Import module: `from src.<module> import <Class>`
3. Create test class: `class Test<Class>:`
4. Write test methods: `def test_<functionality>(self):`
5. Use fixtures and mocks to isolate unit under test

Example:
```python
def test_upload_success(self, uploader, test_video_path, sample_metadata):
    """Test successful video upload"""
    with patch.object(uploader, 'validate_video', return_value=True):
        result = uploader.upload(test_video_path, sample_metadata)
    
    assert result is not None
    assert 'http' in result
```

## CI/CD Integration

Tests run automatically on:
- Pull requests
- Push to main branch
- Scheduled daily runs

GitHub Actions workflow at `.github/workflows/test.yml`
