# 🧪 Testing Quick Reference

## Essential Commands

```bash
# Basic Testing
pytest                          # Run all tests
pytest -v                       # Verbose output
pytest -s                       # Show print statements
pytest -x                       # Stop on first failure
pytest --lf                     # Run last failed tests
pytest --ff                     # Failed first, then rest

# Coverage
pytest --cov=src                                    # Basic coverage
pytest --cov=src --cov-report=term-missing         # Show missing lines
pytest --cov=src --cov-report=html                 # HTML report
pytest --cov=src --cov-fail-under=85               # Fail if < 85%

# Specific Tests
pytest tests/test_database.py                      # Run one file
pytest tests/test_database.py::TestDatabase        # Run one class
pytest tests/test_database.py::test_save_trend     # Run one test
pytest -k "upload"                                 # Tests matching pattern

# Performance
pytest --durations=10           # Show 10 slowest tests
pytest -n auto                  # Parallel (requires pytest-xdist)

# Debugging
pytest --pdb                    # Drop to debugger on failure
pytest --trace                  # Trace execution
pytest -vv                      # Extra verbose (full diffs)

# Test Runner Script
./run_tests.sh                  # All tests with coverage
./run_tests.sh quick            # No coverage
./run_tests.sh coverage         # HTML report
./run_tests.sh watch            # Auto-run on changes
./run_tests.sh clean            # Remove artifacts
```

## Test File Structure

```python
import pytest
from unittest.mock import Mock, patch
from src.module import Class

class TestClass:
    
    @pytest.fixture
    def instance(self):
        return Class()
    
    def test_method_success(self, instance, sample_fixture):
        """Test successful operation"""
        # Arrange
        input_data = "test"
        
        # Act
        result = instance.method(input_data)
        
        # Assert
        assert result == expected
    
    def test_method_failure(self, instance):
        """Test error handling"""
        with pytest.raises(ValueError):
            instance.method(None)
    
    @patch('src.module.external_api')
    def test_with_mock(self, mock_api, instance):
        """Test with mocked dependency"""
        mock_api.return_value = "mocked"
        result = instance.method()
        assert result == "mocked"
```

## Common Fixtures (from conftest.py)

```python
# Use in test functions by adding parameter:
def test_something(sample_trend, mock_groq_client, temp_dir):
    # sample_trend, mock_groq_client, temp_dir available
    pass
```

Available fixtures:
- `temp_dir` - Temporary directory
- `sample_trend` - Mock trend data
- `sample_metadata` - Mock video metadata
- `sample_script` - Sample script
- `mock_groq_client` - Mocked Groq API
- `mock_video_clip` - Mocked video clip
- `test_video_path` - Dummy video file
- `mock_database` - Temp database

## Mock Patterns

### API Mocking
```python
@patch('src.module.api_client')
def test_api_call(mock_api):
    mock_api.return_value.get.return_value = {"data": "test"}
```

### Function Mocking
```python
@patch('src.module.function_name')
def test_function(mock_func):
    mock_func.return_value = "mocked"
```

### Object Mocking
```python
@patch.object(instance, 'method')
def test_method(mock_method):
    mock_method.return_value = True
```

### Side Effects
```python
mock.side_effect = Exception("Error")
mock.side_effect = [1, 2, 3]  # Sequential returns
```

## Assertion Examples

```python
# Equality
assert result == expected
assert result != wrong

# Membership
assert item in collection
assert item not in collection

# Type checking
assert isinstance(result, dict)
assert type(result) is str

# Truthiness
assert result
assert not result

# Exceptions
with pytest.raises(ValueError):
    function()

with pytest.raises(ValueError, match="error message"):
    function()

# Approximate equality
assert result == pytest.approx(3.14, rel=0.01)

# Mock assertions
mock.assert_called()
mock.assert_called_once()
mock.assert_called_with(arg1, arg2)
mock.assert_not_called()
assert mock.call_count == 3
```

## Coverage Tips

```bash
# Find untested code
pytest --cov=src --cov-report=term-missing

# Focus on one module
pytest --cov=src.database --cov-report=term-missing

# Generate detailed HTML report
pytest --cov=src --cov-report=html
open htmlcov/index.html

# Check coverage percentage
pytest --cov=src | grep TOTAL
```

## Debugging Failed Tests

```bash
# Show full diff
pytest -vv

# Show print statements
pytest -s

# Stop on first failure
pytest -x

# Drop to debugger on failure
pytest --pdb

# Run only failed tests
pytest --lf

# Add breakpoint in test
def test_something():
    import pdb; pdb.set_trace()
    result = function()
```

## CI/CD

Tests run automatically on:
- Push to main/develop
- Pull requests
- Daily at 6 AM UTC

Check results:
1. Go to GitHub → Actions tab
2. Click on latest workflow run
3. View test results and coverage

## Coverage Report Locations

- **Terminal**: `pytest --cov=src --cov-report=term-missing`
- **HTML**: `htmlcov/index.html` (after `pytest --cov=src --cov-report=html`)
- **XML**: `coverage.xml` (for CI/CD)

## Test Statistics

- **Total tests**: 87
- **Total test code**: 1,424 lines
- **Coverage target**: 85%+
- **Test files**: 8
- **Components tested**: 6 major components

## Resources

- Full guide: `TESTING.md`
- Test README: `tests/README.md`
- Pytest docs: https://docs.pytest.org/
- Coverage docs: https://coverage.readthedocs.io/
