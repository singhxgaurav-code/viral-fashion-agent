"""Tests for MediaCreator"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import os

from src.media_creator import MediaCreator


class TestMediaCreator:
    
    @pytest.fixture
    def creator(self):
        """Create MediaCreator instance"""
        return MediaCreator()
    
    def test_initialization(self, creator):
        """Test MediaCreator initialization"""
        assert creator.tts_engine == 'edge'
        assert creator.pexels_key is not None
    
    def test_get_video_specs_vertical(self, creator):
        """Test vertical video specs"""
        specs = creator._get_video_specs('9:16')
        
        assert specs['width'] == 1080
        assert specs['height'] == 1920
        assert specs['fps'] == 30
    
    def test_get_video_specs_square(self, creator):
        """Test square video specs"""
        specs = creator._get_video_specs('1:1')
        
        assert specs['width'] == 1080
        assert specs['height'] == 1080
    
    def test_get_video_specs_horizontal(self, creator):
        """Test horizontal video specs"""
        specs = creator._get_video_specs('16:9')
        
        assert specs['width'] == 1920
        assert specs['height'] == 1080
    
    @patch('src.media_creator.edge_tts')
    @patch('src.media_creator.asyncio')
    def test_generate_voiceover_edge_tts(self, mock_asyncio, mock_edge_tts, creator, temp_dir):
        """Test Edge-TTS voiceover generation"""
        output_path = os.path.join(temp_dir, 'test_audio.mp3')
        script = "Test voiceover script"
        
        # Mock async run
        mock_asyncio.run = Mock()
        
        result = creator.generate_voiceover(script, output_path)
        
        mock_asyncio.run.assert_called_once()
    
    @patch('src.media_creator.requests.get')
    def test_fetch_stock_videos_success(self, mock_get, creator):
        """Test stock video fetching from Pexels"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'videos': [{
                'video_files': [{
                    'link': 'https://example.com/video1.mp4',
                    'quality': 'hd'
                }],
                'duration': 10
            }]
        }
        mock_response.content = b'fake_video_data'
        mock_get.return_value = mock_response
        
        with patch('src.media_creator.VideoFileClip') as mock_clip_class:
            mock_clip = Mock()
            mock_clip.duration = 10.0
            mock_clip.resize.return_value = mock_clip
            mock_clip.subclip.return_value = mock_clip
            mock_clip_class.return_value = mock_clip
            
            clips = creator.fetch_stock_videos(['fashion'], 45.0, '9:16')
            
            # Should attempt to fetch videos
            assert mock_get.called
    
    @patch('src.media_creator.requests.get')
    def test_fetch_stock_videos_api_error(self, mock_get, creator):
        """Test stock video fetching with API error"""
        mock_get.return_value.status_code = 401
        
        clips = creator.fetch_stock_videos(['fashion'], 45.0, '9:16')
        
        assert clips == []
    
    @patch('src.media_creator.requests.get')
    def test_create_slideshow_from_images(self, mock_get, creator, temp_dir):
        """Test slideshow creation from images"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'results': [{
                'urls': {'regular': 'https://example.com/image1.jpg'}
            }]
        }
        mock_response.content = b'fake_image_data'
        mock_get.return_value = mock_response
        
        with patch('src.media_creator.ImageClip') as mock_clip_class:
            mock_clip = Mock()
            mock_clip.duration = 5.0
            mock_clip.resize.return_value = mock_clip
            mock_clip_class.return_value = mock_clip
            
            clips = creator.create_slideshow_from_images(['fashion'], 30.0, '9:16')
            
            # Should fetch images
            assert mock_get.called
    
    @patch('src.media_creator.TextClip')
    def test_add_captions(self, mock_text_clip, creator, mock_video_clip):
        """Test adding captions to video"""
        mock_text_instance = Mock()
        mock_text_instance.set_position.return_value = mock_text_instance
        mock_text_instance.set_start.return_value = mock_text_instance
        mock_text_instance.set_duration.return_value = mock_text_instance
        mock_text_clip.return_value = mock_text_instance
        
        with patch('src.media_creator.CompositeVideoClip') as mock_composite:
            script = "This is a test script for captions"
            result = creator.add_captions(mock_video_clip, script, '9:16')
            
            # Should create text clips
            assert mock_text_clip.called
            assert mock_composite.called
    
    @patch('src.media_creator.TextClip')
    @patch('src.media_creator.CompositeVideoClip')
    def test_add_branding(self, mock_composite, mock_text_clip, creator, mock_video_clip):
        """Test adding branding watermark"""
        mock_watermark = Mock()
        mock_watermark.set_position.return_value = mock_watermark
        mock_watermark.set_duration.return_value = mock_watermark
        mock_watermark.set_opacity.return_value = mock_watermark
        mock_text_clip.return_value = mock_watermark
        
        result = creator.add_branding(mock_video_clip, '9:16')
        
        assert mock_text_clip.called
        assert mock_composite.called
    
    @patch('src.media_creator.MediaCreator.generate_voiceover')
    @patch('src.media_creator.MediaCreator.fetch_stock_videos')
    @patch('src.media_creator.AudioFileClip')
    @patch('src.media_creator.concatenate_videoclips')
    def test_create_video_full_pipeline(
        self, mock_concat, mock_audio_clip, mock_fetch, mock_voiceover,
        creator, temp_dir, sample_script, sample_metadata
    ):
        """Test full video creation pipeline"""
        output_path = os.path.join(temp_dir, 'output.mp4')
        
        # Mock voiceover generation
        mock_voiceover.return_value = True
        
        # Mock audio clip
        mock_audio_instance = Mock()
        mock_audio_instance.duration = 45.0
        mock_audio_instance.close = Mock()
        mock_audio_clip.return_value = mock_audio_instance
        
        # Mock video clips
        mock_clip = Mock()
        mock_clip.set_audio.return_value = mock_clip
        mock_clip.write_videofile = Mock()
        mock_clip.close = Mock()
        mock_fetch.return_value = [mock_clip]
        
        # Mock concatenated video
        mock_concat.return_value = mock_clip
        
        with patch.object(creator, 'add_captions', return_value=mock_clip), \
             patch.object(creator, 'add_branding', return_value=mock_clip):
            
            result = creator.create_video(
                sample_script,
                sample_metadata,
                output_path,
                aspect_ratio='9:16'
            )
        
        assert mock_voiceover.called
        assert mock_fetch.called
    
    @patch('src.media_creator.MediaCreator.generate_voiceover')
    def test_create_video_voiceover_failure(
        self, mock_voiceover, creator, temp_dir, sample_script, sample_metadata
    ):
        """Test video creation with voiceover failure"""
        output_path = os.path.join(temp_dir, 'output.mp4')
        mock_voiceover.return_value = False
        
        result = creator.create_video(
            sample_script,
            sample_metadata,
            output_path
        )
        
        assert result is False
