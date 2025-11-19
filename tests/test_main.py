"""Tests for main orchestrator"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import sys

from main import ViralFashionAgent


class TestViralFashionAgent:
    
    @pytest.fixture
    def agent(self):
        """Create ViralFashionAgent with mocked dependencies"""
        with patch('main.TrendDetector'), \
             patch('main.ContentGenerator'), \
             patch('main.MediaCreator'), \
             patch('main.MultiPlatformUploader'), \
             patch('main.Database'), \
             patch('main.os.makedirs'):
            return ViralFashionAgent()
    
    def test_initialization(self, agent):
        """Test agent initialization"""
        assert agent.trend_detector is not None
        assert agent.content_generator is not None
        assert agent.media_creator is not None
        assert agent.uploader is not None
        assert agent.db is not None
    
    def test_extract_content_id_youtube(self, agent):
        """Test extracting YouTube video ID"""
        url = 'https://youtube.com/shorts/ABC123'
        content_id = agent._extract_content_id(url, 'youtube')
        
        assert content_id == 'ABC123'
    
    def test_extract_content_id_instagram(self, agent):
        """Test extracting Instagram reel code"""
        url = 'https://www.instagram.com/reel/XYZ789/'
        content_id = agent._extract_content_id(url, 'instagram')
        
        assert content_id == 'XYZ789'
    
    def test_extract_content_id_twitter(self, agent):
        """Test extracting Twitter tweet ID"""
        url = 'https://twitter.com/user/status/12345678'
        content_id = agent._extract_content_id(url, 'twitter')
        
        assert content_id == '12345678'
    
    def test_extract_content_id_invalid(self, agent):
        """Test content ID extraction with invalid URL"""
        content_id = agent._extract_content_id(None, 'youtube')
        assert content_id is None
    
    @patch('main.config.DAILY_VIDEOS_COUNT', 2)
    def test_daily_workflow_success(self, agent, sample_trend, sample_script, sample_metadata):
        """Test successful daily workflow"""
        # Mock trend detection
        agent.trend_detector.get_fashion_trends.return_value = [sample_trend, sample_trend]
        
        # Mock content generation
        agent.content_generator.generate_batch_content.return_value = [
            {'script': sample_script, 'metadata': sample_metadata, 'trend': sample_trend, 'status': 'ready'},
            {'script': sample_script, 'metadata': sample_metadata, 'trend': sample_trend, 'status': 'ready'}
        ]
        
        # Mock video creation
        agent.media_creator.create_video.return_value = True
        
        # Mock uploads
        agent.uploader.upload_to_all.return_value = {
            'youtube': 'https://youtube.com/test',
            'tiktok': 'https://tiktok.com/test'
        }
        
        # Mock database
        agent.db.save_trend.return_value = 1
        agent.db.save_video.return_value = 1
        agent.db.save_upload.return_value = 1
        agent.db.get_total_analytics.return_value = {
            'total_views': 1000,
            'total_likes': 50,
            'total_comments': 10,
            'total_uploads': 2
        }
        
        with patch('main.time.sleep'):  # Skip sleep delays
            agent.daily_workflow()
        
        # Verify calls
        agent.trend_detector.get_fashion_trends.assert_called_once()
        agent.content_generator.generate_batch_content.assert_called_once()
        assert agent.media_creator.create_video.call_count == 2
    
    def test_daily_workflow_no_trends(self, agent):
        """Test daily workflow with no trends detected"""
        agent.trend_detector.get_fashion_trends.return_value = []
        
        agent.daily_workflow()
        
        # Should abort early
        agent.content_generator.generate_batch_content.assert_not_called()
    
    def test_daily_workflow_content_generation_failure(self, agent, sample_trend):
        """Test daily workflow with content generation failure"""
        agent.trend_detector.get_fashion_trends.return_value = [sample_trend]
        agent.content_generator.generate_batch_content.return_value = []
        
        agent.daily_workflow()
        
        # Should abort after content generation
        agent.media_creator.create_video.assert_not_called()
    
    def test_daily_workflow_video_creation_failure(self, agent, sample_trend, sample_script, sample_metadata):
        """Test daily workflow handles video creation failure"""
        agent.trend_detector.get_fashion_trends.return_value = [sample_trend]
        agent.content_generator.generate_batch_content.return_value = [
            {'script': sample_script, 'metadata': sample_metadata, 'trend': sample_trend}
        ]
        agent.media_creator.create_video.return_value = False
        agent.db.get_total_analytics.return_value = {'total_views': 0}
        
        agent.daily_workflow()
        
        # Should continue despite failure
        agent.media_creator.create_video.assert_called_once()
    
    def test_update_analytics(self, agent):
        """Test analytics update"""
        agent.db.get_recent_uploads.return_value = [
            {
                'id': 1,
                'platform': 'youtube',
                'url': 'https://youtube.com/shorts/ABC123'
            }
        ]
        
        mock_youtube_uploader = Mock()
        mock_youtube_uploader.get_analytics.return_value = {
            'views': 1000,
            'likes': 50
        }
        agent.uploader.uploaders = {'youtube': mock_youtube_uploader}
        
        agent.db.get_platform_performance.return_value = []
        
        agent.update_analytics()
        
        agent.db.update_analytics.assert_called()
    
    def test_generate_report(self, agent):
        """Test report generation"""
        agent.db.get_total_analytics.return_value = {
            'total_views': 10000,
            'total_likes': 500,
            'total_comments': 100,
            'total_uploads': 50
        }
        
        agent.db.get_platform_performance.return_value = [
            {
                'platform': 'youtube',
                'uploads': 25,
                'total_views': 6000,
                'avg_views': 240
            },
            {
                'platform': 'tiktok',
                'uploads': 25,
                'total_views': 4000,
                'avg_views': 160
            }
        ]
        
        agent.generate_report()
        
        # Should call database methods
        agent.db.get_total_analytics.assert_called()
        agent.db.get_platform_performance.assert_called()


class TestMainFunction:
    
    @patch('main.ViralFashionAgent')
    def test_main_test_command(self, mock_agent_class):
        """Test main with 'test' command"""
        mock_agent = Mock()
        mock_agent_class.return_value = mock_agent
        
        with patch.object(sys, 'argv', ['main.py', 'test']):
            from main import main
            main()
        
        mock_agent.daily_workflow.assert_called_once()
    
    @patch('main.ViralFashionAgent')
    def test_main_analytics_command(self, mock_agent_class):
        """Test main with 'analytics' command"""
        mock_agent = Mock()
        mock_agent_class.return_value = mock_agent
        
        with patch.object(sys, 'argv', ['main.py', 'analytics']):
            from main import main
            main()
        
        mock_agent.update_analytics.assert_called_once()
        mock_agent.generate_report.assert_called_once()
    
    @patch('main.ViralFashionAgent')
    def test_main_report_command(self, mock_agent_class):
        """Test main with 'report' command"""
        mock_agent = Mock()
        mock_agent_class.return_value = mock_agent
        
        with patch.object(sys, 'argv', ['main.py', 'report']):
            from main import main
            main()
        
        mock_agent.generate_report.assert_called_once()
