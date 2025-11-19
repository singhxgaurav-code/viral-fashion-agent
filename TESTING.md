# Testing Documentation

## Test Suite Overview

The Viral Fashion Agent has a comprehensive test suite with **90+ unit tests** across all major components, targeting **85% code coverage**.

## Test Coverage by Module

| Module | Tests | Coverage Focus |
|--------|-------|----------------|
| `test_trend_detector.py` | 15 | Reddit/Twitter/Google Trends scraping, deduplication, keyword extraction |
| `test_content_generator.py` | 14 | Groq AI integration, script generation, metadata optimization |
| `test_database.py` | 14 | SQLite CRUD operations, analytics aggregation, trend tracking |
| `test_uploaders.py` | 20 | Multi-platform uploads, authentication, metadata adaptation |
| `test_media_creator.py` | 12 | TTS generation, video editing, captions, stock media |
| `test_main.py` | 12 | Workflow orchestration, CLI commands, error handling |

**Total: 90+ tests**

## Running Tests

### Basic Usage

```bash
# Install dependencies (includes pytest)
pip install -r requirements.txt

# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_database.py

# Run specific test class
pytest tests/test_database.py::TestDatabase

# Run specific test function
pytest tests/test_database.py::TestDatabase::test_save_trend

# Run tests matching keyword
pytest -k "upload"
```

### Coverage Reports

```bash
# Run with coverage
pytest --cov=src

# Detailed coverage with missing lines
pytest --cov=src --cov-report=term-missing

# Generate HTML coverage report
pytest --cov=src --cov-report=html
open htmlcov/index.html

# Generate XML for CI/CD
pytest --cov=src --cov-report=xml

# Fail if coverage below 85%
pytest --cov=src --cov-fail-under=85
```

### Watch Mode (for TDD)

```bash
# Install pytest-watch
pip install pytest-watch

# Auto-run tests on file changes
ptw
```

## Test Structure

### Fixtures (`conftest.py`)

Reusable test data and mocks:

- **`temp_dir`**: Temporary directory for file operations
- **`sample_trend`**: Mock trend data from Reddit/Twitter
- **`sample_metadata`**: Mock video metadata (title, description, tags)
- **`sample_script`**: Sample 45-second video script
- **`mock_groq_client`**: Mocked Groq API client
- **`mock_video_clip`**: Mocked MoviePy VideoFileClip
- **`mock_audio_clip`**: Mocked MoviePy AudioFileClip
- **`test_video_path`**: Dummy video file (1KB)
- **`mock_database`**: Temporary test database

### Mock Patterns

#### API Mocking
```python
@patch('src.content_generator.Groq')
def test_generate_script(self, mock_groq, generator):
    mock_groq.return_value.chat.completions.create.return_value.choices[0].message.content = "Test script"
    script = generator.generate_script(sample_trend)
    assert "Test script" in script
```

#### File I/O Mocking
```python
@patch('src.media_creator.VideoFileClip')
def test_create_video(self, mock_clip, creator):
    mock_clip.return_value.duration = 45.0
    result = creator.create_video(script, metadata, output_path)
    assert result is True
```

#### Database Mocking
```python
def test_save_trend(self, db, sample_trend):
    trend_id = db.save_trend(sample_trend)
    assert isinstance(trend_id, int)
```

## Writing New Tests

### Step-by-Step Guide

1. **Create test file**: `tests/test_<module_name>.py`

2. **Import dependencies**:
   ```python
   import pytest
   from unittest.mock import Mock, patch
   from src.<module> import <Class>
   ```

3. **Create test class**:
   ```python
   class Test<ClassName>:
       @pytest.fixture
       def instance(self):
           return <ClassName>()
   ```

4. **Write test methods**:
   ```python
   def test_<functionality>(self, instance, sample_fixture):
       """Test description"""
       # Arrange
       input_data = "test"
       
       # Act
       result = instance.method(input_data)
       
       # Assert
       assert result == expected
   ```

### Test Naming Conventions

- **Test files**: `test_<module>.py`
- **Test classes**: `Test<ClassName>`
- **Test methods**: `test_<method_name>_<scenario>`

Examples:
- `test_upload_success`
- `test_upload_invalid_file_size`
- `test_authenticate_expired_token`

### Test Categories

1. **Happy Path**: Test successful operations
   ```python
   def test_upload_success(self, uploader, test_video_path):
       result = uploader.upload(test_video_path, metadata)
       assert result is not None
   ```

2. **Error Handling**: Test failure scenarios
   ```python
   def test_upload_api_failure(self, uploader, test_video_path):
       with patch.object(uploader.client, 'upload', side_effect=Exception("API Error")):
           result = uploader.upload(test_video_path, metadata)
           assert result is None
   ```

3. **Edge Cases**: Test boundary conditions
   ```python
   def test_upload_empty_metadata(self, uploader, test_video_path):
       result = uploader.upload(test_video_path, {})
       assert result is not None
   ```

## CI/CD Integration

### GitHub Actions

Tests run automatically on:
- **Push to main/develop**: Ensures code quality
- **Pull requests**: Blocks merging if tests fail
- **Daily schedule**: Catches integration issues

Configuration: `.github/workflows/test.yml`

Features:
- Runs on Python 3.10, 3.11, 3.12
- Installs FFmpeg for video processing
- Caches pip packages for speed
- Uploads coverage to Codecov
- Enforces 85% coverage minimum

### Coverage Badge

Add to README:
```markdown
![Coverage](https://img.shields.io/badge/coverage-85%25-brightgreen)
```

## Debugging Tests

### Run Single Test with Print Statements
```bash
pytest tests/test_database.py::test_save_trend -s
```

### Use PDB Debugger
```python
def test_something(self):
    import pdb; pdb.set_trace()
    result = function_under_test()
```

### Show Full Diff on Assertion Failures
```bash
pytest -vv
```

### Run Last Failed Tests
```bash
pytest --lf
```

### Show Slowest Tests
```bash
pytest --durations=10
```

## Best Practices

### ✅ DO

- **Mock external dependencies**: APIs, file I/O, network calls
- **Use fixtures**: Reuse test data and setup
- **Test one thing**: Each test should verify one behavior
- **Clear assertions**: Use descriptive assertion messages
- **Isolate tests**: No test should depend on another

### ❌ DON'T

- **Don't test implementation details**: Test behavior, not internals
- **Don't skip cleanup**: Use fixtures with teardown
- **Don't hardcode paths**: Use `temp_dir` fixture
- **Don't test external APIs**: Always mock
- **Don't ignore warnings**: Fix deprecation warnings

## Troubleshooting

### Import Errors
```bash
# Ensure src is in PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:${PWD}"
pytest
```

### Fixture Not Found
```bash
# Check conftest.py is in tests/
ls tests/conftest.py

# Ensure pytest discovers it
pytest --fixtures
```

### Coverage Not Matching
```bash
# Clear cache and re-run
rm -rf .pytest_cache .coverage
pytest --cov=src
```

### Slow Tests
```bash
# Run in parallel (requires pytest-xdist)
pip install pytest-xdist
pytest -n auto
```

## Resources

- **Pytest Documentation**: https://docs.pytest.org/
- **Coverage.py**: https://coverage.readthedocs.io/
- **Python Mock**: https://docs.python.org/3/library/unittest.mock.html
- **Testing Best Practices**: https://testdriven.io/blog/testing-best-practices/
