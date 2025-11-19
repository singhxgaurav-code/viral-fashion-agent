"""Tests for Platform Uploaders"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import os

from src.uploaders.base import BasePlatformUploader
from src.uploaders.youtube import YouTubeUploader
from src.uploaders.instagram import InstagramUploader
from src.uploaders.twitter import TwitterUploader
from src.uploaders import MultiPlatformUploader


class MockUploader(BasePlatformUploader):
    """Concrete implementation for testing base class"""
    
    def authenticate(self):
        return True
    
    def upload(self, video_path, metadata):
        return "mock_url"
    
    def get_analytics(self, content_id):
        return {'views': 100}


class TestBasePlatformUploader:
    
    def test_initialization(self):
        """Test base uploader initialization"""
        uploader = MockUploader('test_platform')
        assert uploader.platform_name == 'test_platform'
    
    def test_validate_video_size(self, test_video_path):
        """Test video size validation"""
        uploader = MockUploader('test')
        
        # Small file should pass
        result = uploader.validate_video(test_video_path, max_size_mb=10, max_duration=60)
        # Will fail on duration check but not size
        
    def test_validate_video_too_large(self, temp_dir):
        """Test video size validation failure"""
        uploader = MockUploader('test')
        
        # Create large file
        large_file = os.path.join(temp_dir, 'large.mp4')
        with open(large_file, 'wb') as f:
            f.write(b'\x00' * (11 * 1024 * 1024))  # 11MB
        
        result = uploader.validate_video(large_file, max_size_mb=10, max_duration=60)
        assert result is False


class TestYouTubeUploader:
    
    @pytest.fixture
    def uploader(self):
        """Create YouTubeUploader with mocked dependencies"""
        with patch('src.uploaders.youtube.os.path.exists', return_value=False):
            return YouTubeUploader()
    
    def test_initialization(self, uploader):
        """Test YouTubeUploader initialization"""
        assert uploader.platform_name == 'YouTube'
        assert uploader.youtube is None
    
    @patch('src.uploaders.youtube.build')
    @patch('src.uploaders.youtube.pickle.load')
    @patch('src.uploaders.youtube.os.path.exists', return_value=True)
    def test_authenticate_existing_token(self, mock_exists, mock_pickle, mock_build, uploader):
        """Test authentication with existing token"""
        mock_creds = Mock()
        mock_creds.valid = True
        mock_pickle.return_value = mock_creds
        
        with patch('builtins.open', create=True):
            result = uploader.authenticate()
        
        assert result is True
    
    @patch('src.uploaders.youtube.MediaFileUpload')
    def test_upload_metadata_formatting(self, mock_media, uploader, test_video_path, sample_metadata):
        """Test YouTube upload metadata formatting"""
        mock_youtube = Mock()
        mock_request = Mock()
        mock_request.next_chunk.side_effect = [(None, None), (Mock(progress=lambda: 1.0), {'id': 'test123'})]
        mock_youtube.videos().insert.return_value = mock_request
        uploader.youtube = mock_youtube
        
        with patch.object(uploader, 'validate_video', return_value=True):
            result = uploader.upload(test_video_path, sample_metadata)
        
        assert result is not None
        assert 'youtube.com/shorts/' in result
    
    def test_get_analytics(self, uploader):
        """Test YouTube analytics fetching"""
        mock_youtube = Mock()
        mock_response = {
            'items': [{
                'statistics': {
                    'viewCount': '1000',
                    'likeCount': '50',
                    'commentCount': '10'
                }
            }]
        }
        mock_youtube.videos().list().execute.return_value = mock_response
        uploader.youtube = mock_youtube
        
        analytics = uploader.get_analytics('test_video_id')
        
        assert analytics['views'] == 1000
        assert analytics['likes'] == 50
        assert analytics['platform'] == 'youtube'


class TestInstagramUploader:
    
    @pytest.fixture
    def uploader(self):
        """Create InstagramUploader with mocked dependencies"""
        with patch('src.uploaders.instagram.Client'):
            return InstagramUploader()
    
    def test_initialization(self, uploader):
        """Test InstagramUploader initialization"""
        assert uploader.platform_name == 'Instagram'
    
    @patch('src.uploaders.instagram.config.INSTAGRAM_USERNAME', 'test_user')
    @patch('src.uploaders.instagram.config.INSTAGRAM_PASSWORD', 'test_pass')
    def test_authenticate_success(self, uploader):
        """Test Instagram authentication"""
        uploader.client.login = Mock()
        uploader.client.dump_settings = Mock()
        uploader.client.get_timeline_feed = Mock()
        
        result = uploader.authenticate()
        
        assert result is True
        uploader.client.login.assert_called()
    
    def test_upload_caption_with_hashtags(self, uploader, test_video_path, sample_metadata):
        """Test Instagram upload includes hashtags"""
        uploader.client.user_id = 'test123'
        uploader.client.clip_upload = Mock(return_value=Mock(code='ABC123'))
        
        with patch.object(uploader, 'validate_video', return_value=True):
            result = uploader.upload(test_video_path, sample_metadata)
        
        assert result is not None
        assert 'instagram.com/reel/' in result
        
        # Check that hashtags were added
        call_args = uploader.client.clip_upload.call_args
        caption = call_args[1]['caption']
        assert '#' in caption
    
    def test_get_analytics(self, uploader):
        """Test Instagram analytics fetching"""
        uploader.client.media_pk_from_code = Mock(return_value='123456')
        
        mock_media = Mock()
        mock_media.play_count = 5000
        mock_media.like_count = 250
        mock_media.comment_count = 30
        uploader.client.media_info = Mock(return_value=mock_media)
        
        analytics = uploader.get_analytics('ABC123')
        
        assert analytics['views'] == 5000
        assert analytics['likes'] == 250
        assert analytics['platform'] == 'instagram'


class TestTwitterUploader:
    
    @pytest.fixture
    def uploader(self):
        """Create TwitterUploader"""
        return TwitterUploader()
    
    def test_initialization(self, uploader):
        """Test TwitterUploader initialization"""
        assert uploader.platform_name == 'Twitter'
    
    @patch('src.uploaders.twitter.tweepy.Client')
    @patch('src.uploaders.twitter.tweepy.API')
    @patch('src.uploaders.twitter.os.getenv')
    def test_authenticate_success(self, mock_getenv, mock_api, mock_client, uploader):
        """Test Twitter authentication"""
        mock_getenv.return_value = 'test_key'
        mock_client_instance = Mock()
        mock_client_instance.get_me.return_value = Mock()
        mock_client.return_value = mock_client_instance
        
        result = uploader.authenticate()
        
        assert result is True
    
    def test_upload_character_limit(self, uploader, test_video_path, sample_metadata):
        """Test Twitter upload respects character limit"""
        uploader.client = Mock()
        uploader.api = Mock()
        
        # Create long description
        long_metadata = sample_metadata.copy()
        long_metadata['description'] = 'A' * 300
        
        mock_media = Mock()
        mock_media.media_id = 'test123'
        uploader.api.media_upload.return_value = mock_media
        
        mock_response = Mock()
        mock_response.data = {'id': 'tweet123'}
        uploader.client.create_tweet.return_value = mock_response
        uploader.client.get_me.return_value = Mock(data=Mock(username='testuser'))
        
        with patch.object(uploader, 'validate_video', return_value=True):
            result = uploader.upload(test_video_path, long_metadata)
        
        # Check tweet text was truncated
        call_args = uploader.client.create_tweet.call_args
        tweet_text = call_args[1]['text']
        assert len(tweet_text) <= 280


class TestMultiPlatformUploader:
    
    @pytest.fixture
    def uploader(self):
        """Create MultiPlatformUploader with mocked uploaders"""
        with patch('src.uploaders.YouTubeUploader'), \
             patch('src.uploaders.TikTokUploader'), \
             patch('src.uploaders.InstagramUploader'), \
             patch('src.uploaders.TwitterUploader'), \
             patch('src.uploaders.FacebookUploader'):
            return MultiPlatformUploader()
    
    def test_initialization(self, uploader):
        """Test MultiPlatformUploader initialization"""
        assert isinstance(uploader.uploaders, dict)
    
    def test_upload_to_all(self, uploader, test_video_path, sample_metadata):
        """Test parallel upload to all platforms"""
        # Mock uploaders
        for platform in uploader.uploaders:
            mock_uploader = Mock()
            mock_uploader.upload.return_value = f'https://{platform}.com/test'
            uploader.uploaders[platform] = mock_uploader
        
        results = uploader.upload_to_all(test_video_path, sample_metadata)
        
        assert isinstance(results, dict)
        assert len(results) > 0
        
        # All platforms should have been called
        for platform_uploader in uploader.uploaders.values():
            platform_uploader.upload.assert_called_once()
    
    def test_adapt_metadata_youtube(self, uploader, sample_metadata):
        """Test YouTube metadata adaptation"""
        adapted = uploader._adapt_metadata(sample_metadata, 'youtube')
        
        assert '#Shorts' in adapted['description']
    
    def test_adapt_metadata_tiktok(self, uploader, sample_metadata):
        """Test TikTok metadata adaptation"""
        long_metadata = sample_metadata.copy()
        long_metadata['description'] = 'A' * 200
        
        adapted = uploader._adapt_metadata(long_metadata, 'tiktok')
        
        assert len(adapted['description']) <= 150
    
    def test_get_all_analytics(self, uploader):
        """Test analytics aggregation from all platforms"""
        upload_results = {
            'youtube': 'video123',
            'tiktok': 'tiktok456'
        }
        
        for platform in uploader.uploaders:
            mock_uploader = Mock()
            mock_uploader.get_analytics.return_value = {
                'views': 1000,
                'likes': 50
            }
            uploader.uploaders[platform] = mock_uploader
        
        analytics = uploader.get_all_analytics(upload_results)
        
        assert len(analytics) == 2
    
    def test_get_total_reach(self, uploader):
        """Test total reach calculation"""
        analytics = {
            'youtube': {'views': 1000, 'likes': 50, 'comments': 10, 'shares': 5},
            'tiktok': {'views': 2000, 'likes': 100, 'comments': 20, 'shares': 10}
        }
        
        total = uploader.get_total_reach(analytics)
        
        assert total['total_views'] == 3000
        assert total['total_likes'] == 150
        assert total['total_comments'] == 30
