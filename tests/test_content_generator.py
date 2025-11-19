"""Tests for ContentGenerator"""
import pytest
from unittest.mock import Mock, patch
import json

from src.content_generator import ContentGenerator


class TestContentGenerator:
    
    @pytest.fixture
    def generator(self, mock_groq_client):
        """Create ContentGenerator instance with mocked Groq"""
        with patch('src.content_generator.Groq', return_value=mock_groq_client):
            return ContentGenerator()
    
    def test_initialization(self, generator):
        """Test ContentGenerator initialization"""
        assert generator is not None
        assert generator.model == "llama-3.1-70b-versatile"
        assert generator.client is not None
    
    def test_generate_script_success(self, generator, sample_trend, mock_groq_client):
        """Test script generation success"""
        mock_groq_client.chat.completions.create.return_value.choices[0].message.content = \
            "Did you know sustainable fashion is trending? Here are 3 tips..."
        
        script = generator.generate_script(sample_trend)
        
        assert isinstance(script, str)
        assert len(script) > 0
        mock_groq_client.chat.completions.create.assert_called_once()
    
    def test_generate_script_with_duration(self, generator, sample_trend, mock_groq_client):
        """Test script generation with custom duration"""
        script = generator.generate_script(sample_trend, duration=60)
        
        # Check that prompt included duration
        call_args = mock_groq_client.chat.completions.create.call_args
        assert '60-second' in call_args[1]['messages'][0]['content']
    
    def test_generate_script_failure_fallback(self, generator, sample_trend, mock_groq_client):
        """Test fallback script on API failure"""
        mock_groq_client.chat.completions.create.side_effect = Exception("API Error")
        
        script = generator.generate_script(sample_trend)
        
        assert isinstance(script, str)
        assert len(script) > 0
        assert sample_trend['title'] in script
    
    def test_generate_metadata_success(self, generator, sample_script, sample_trend, mock_groq_client):
        """Test metadata generation success"""
        metadata_json = json.dumps({
            'title': 'Sustainable Fashion Tips',
            'description': 'Learn eco-friendly style',
            'hashtags': ['#fashion', '#sustainable'],
            'keywords': ['fashion', 'sustainable']
        })
        mock_groq_client.chat.completions.create.return_value.choices[0].message.content = metadata_json
        
        metadata = generator.generate_metadata(sample_script, sample_trend)
        
        assert isinstance(metadata, dict)
        assert 'title' in metadata
        assert 'description' in metadata
        assert 'tags' in metadata
    
    def test_generate_metadata_with_code_block(self, generator, sample_script, sample_trend, mock_groq_client):
        """Test metadata extraction from code block"""
        metadata_json = {
            'title': 'Test Title',
            'description': 'Test Description',
            'hashtags': ['#test'],
            'keywords': ['test']
        }
        response_with_code_block = f"```json\n{json.dumps(metadata_json)}\n```"
        mock_groq_client.chat.completions.create.return_value.choices[0].message.content = response_with_code_block
        
        metadata = generator.generate_metadata(sample_script, sample_trend)
        
        assert metadata['title'] == 'Test Title'
        assert 'tags' in metadata
    
    def test_generate_metadata_failure_fallback(self, generator, sample_script, sample_trend, mock_groq_client):
        """Test fallback metadata on parsing failure"""
        mock_groq_client.chat.completions.create.side_effect = Exception("API Error")
        
        metadata = generator.generate_metadata(sample_script, sample_trend)
        
        assert isinstance(metadata, dict)
        assert 'title' in metadata
        assert 'tags' in metadata
    
    def test_generate_batch_content(self, generator, sample_trend, mock_groq_client):
        """Test batch content generation"""
        mock_groq_client.chat.completions.create.return_value.choices[0].message.content = \
            json.dumps({
                'title': 'Test',
                'description': 'Test',
                'hashtags': ['#test'],
                'keywords': ['test']
            })
        
        trends = [sample_trend, sample_trend]
        batch = generator.generate_batch_content(trends)
        
        assert isinstance(batch, list)
        assert len(batch) == 2
        assert all('script' in item for item in batch)
        assert all('metadata' in item for item in batch)
    
    def test_optimize_for_youtube(self, generator, sample_metadata):
        """Test YouTube metadata optimization"""
        optimized = generator.optimize_for_platform(sample_metadata, 'youtube')
        
        assert '#Shorts' in optimized['title'] or '#Shorts' in optimized['description']
    
    def test_optimize_for_tiktok(self, generator, sample_metadata):
        """Test TikTok metadata optimization"""
        long_description = 'A' * 200
        metadata = sample_metadata.copy()
        metadata['description'] = long_description
        
        optimized = generator.optimize_for_platform(metadata, 'tiktok')
        
        assert len(optimized['description']) <= 105  # 100 + "..."
    
    def test_optimize_for_instagram(self, generator, sample_metadata):
        """Test Instagram metadata optimization"""
        optimized = generator.optimize_for_platform(sample_metadata, 'instagram')
        
        # Should have hashtags in description
        assert '#' in optimized['description']
    
    def test_optimize_for_twitter(self, generator, sample_metadata):
        """Test Twitter metadata optimization"""
        long_description = 'A' * 300
        metadata = sample_metadata.copy()
        metadata['description'] = long_description
        
        optimized = generator.optimize_for_platform(metadata, 'twitter')
        
        # Should be truncated
        assert len(optimized['description']) <= 250
    
    def test_fallback_script_structure(self, generator, sample_trend):
        """Test fallback script has proper structure"""
        script = generator._fallback_script(sample_trend)
        
        assert sample_trend['title'] in script
        assert 'Follow' in script or 'tips' in script
    
    def test_fallback_metadata_structure(self, generator, sample_script, sample_trend):
        """Test fallback metadata has proper structure"""
        metadata = generator._fallback_metadata(sample_script, sample_trend)
        
        assert 'title' in metadata
        assert 'description' in metadata
        assert 'tags' in metadata
        assert len(metadata['hashtags']) > 0
    
    def test_generate_viral_hook(self, generator, sample_trend):
        """Test viral hook generation"""
        hook = generator.generate_viral_hook(sample_trend)
        
        assert isinstance(hook, str)
        assert len(hook) > 0
        assert sample_trend['title'] in hook
