"""Pytest configuration and fixtures"""
import os
import sys
import pytest
from unittest.mock import Mock, MagicMock
import tempfile
import shutil

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


@pytest.fixture
def temp_dir():
    """Create temporary directory for tests"""
    temp_path = tempfile.mkdtemp()
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def sample_trend():
    """Sample trend data for testing"""
    return {
        'source': 'reddit',
        'title': 'Sustainable Fashion Trends 2025',
        'description': 'Eco-friendly fashion is taking over',
        'keywords': ['sustainable', 'fashion', 'eco-friendly'],
        'score': 150,
        'url': 'https://reddit.com/r/fashion/test',
        'timestamp': '2025-11-19T10:00:00'
    }


@pytest.fixture
def sample_metadata():
    """Sample video metadata for testing"""
    return {
        'title': 'Top 3 Sustainable Fashion Tips',
        'description': 'Learn how to build an eco-friendly wardrobe',
        'tags': ['fashion', 'sustainable', 'ecofriendly', 'style', 'ootd'],
        'hashtags': ['#fashion', '#sustainable', '#ecofriendly'],
        'keywords': ['sustainable fashion', 'eco-friendly', 'wardrobe']
    }


@pytest.fixture
def sample_script():
    """Sample video script for testing"""
    return """Did you know sustainable fashion is trending?

Here are 3 tips:
• Buy second-hand clothing
• Choose natural fabrics
• Support ethical brands

Save this for later!"""


@pytest.fixture
def mock_groq_client():
    """Mock Groq API client"""
    mock = Mock()
    mock_response = Mock()
    mock_response.choices = [Mock(message=Mock(content='Generated script content'))]
    mock.chat.completions.create.return_value = mock_response
    return mock


@pytest.fixture
def mock_video_clip():
    """Mock MoviePy VideoFileClip"""
    mock = MagicMock()
    mock.duration = 45.0
    mock.fps = 30
    mock.size = (1080, 1920)
    return mock


@pytest.fixture
def mock_audio_clip():
    """Mock MoviePy AudioFileClip"""
    mock = MagicMock()
    mock.duration = 45.0
    return mock


@pytest.fixture
def test_video_path(temp_dir):
    """Create a dummy video file for testing"""
    video_path = os.path.join(temp_dir, 'test_video.mp4')
    # Create empty file
    with open(video_path, 'wb') as f:
        f.write(b'\x00' * 1024)  # 1KB dummy file
    return video_path


@pytest.fixture
def mock_database(temp_dir):
    """Create temporary test database"""
    db_path = os.path.join(temp_dir, 'test_agent.db')
    return db_path


@pytest.fixture(autouse=True)
def mock_env_vars(monkeypatch):
    """Mock environment variables for all tests"""
    env_vars = {
        'GROQ_API_KEY': 'test_groq_key',
        'REDDIT_CLIENT_ID': 'test_reddit_id',
        'REDDIT_CLIENT_SECRET': 'test_reddit_secret',
        'TWITTER_BEARER_TOKEN': 'test_twitter_token',
        'PEXELS_API_KEY': 'test_pexels_key',
        'UNSPLASH_ACCESS_KEY': 'test_unsplash_key',
        'INSTAGRAM_USERNAME': 'test_user',
        'INSTAGRAM_PASSWORD': 'test_pass',
        'YOUTUBE_CLIENT_SECRETS_FILE': 'test_secrets.json',
        'DATABASE_PATH': 'data/test_agent.db',
        'OUTPUT_DIR': 'test_output',
        'LOG_LEVEL': 'ERROR',  # Reduce noise in tests
    }
    
    for key, value in env_vars.items():
        monkeypatch.setenv(key, value)
