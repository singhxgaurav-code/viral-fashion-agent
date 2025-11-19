"""Tests for TrendDetector"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from src.trend_detector import TrendDetector


class TestTrendDetector:
    
    @pytest.fixture
    def detector(self):
        """Create TrendDetector instance"""
        with patch('src.trend_detector.praw.Reddit'), \
             patch('src.trend_detector.tweepy.Client'), \
             patch('src.trend_detector.TrendReq'):
            return TrendDetector()
    
    def test_initialization(self, detector):
        """Test TrendDetector initialization"""
        assert detector is not None
        assert detector.pytrends is not None
    
    def test_is_fashion_related_positive(self, detector):
        """Test fashion keyword detection - positive cases"""
        assert detector._is_fashion_related('streetwear outfit ideas')
        assert detector._is_fashion_related('FASHION trends 2025')
        assert detector._is_fashion_related('Check out my new sneakers')
        assert detector._is_fashion_related('sustainable clothing brands')
    
    def test_is_fashion_related_negative(self, detector):
        """Test fashion keyword detection - negative cases"""
        assert not detector._is_fashion_related('cooking recipes')
        assert not detector._is_fashion_related('tech news')
        assert not detector._is_fashion_related('gaming tips')
    
    def test_extract_keywords(self, detector):
        """Test keyword extraction from text"""
        text = "Check out this amazing streetwear outfit with vintage sneakers"
        keywords = detector._extract_keywords(text)
        
        assert isinstance(keywords, list)
        assert len(keywords) <= 5
        assert any('streetwear' in k or 'outfit' in k or 'vintage' in k for k in keywords)
    
    def test_extract_keywords_with_urls(self, detector):
        """Test keyword extraction removes URLs"""
        text = "Fashion tips https://example.com @user #trending"
        keywords = detector._extract_keywords(text)
        
        # Should not contain URL parts
        assert not any('http' in k or 'example' in k for k in keywords)
    
    def test_deduplicate_trends_exact_match(self, detector):
        """Test deduplication removes exact duplicates"""
        trends = [
            {'title': 'Sustainable Fashion Tips', 'keywords': []},
            {'title': 'sustainable fashion tips', 'keywords': []},  # Duplicate
            {'title': 'Vintage Style Guide', 'keywords': []}
        ]
        
        unique = detector._deduplicate_trends(trends)
        assert len(unique) == 2
    
    def test_deduplicate_trends_similar(self, detector):
        """Test deduplication removes similar trends"""
        trends = [
            {'title': 'Top 5 Fashion Trends 2025', 'keywords': []},
            {'title': 'Top 5 Fashion Trends', 'keywords': []},  # Similar
            {'title': 'Completely Different Topic', 'keywords': []}
        ]
        
        unique = detector._deduplicate_trends(trends)
        assert len(unique) <= 2
    
    @patch('src.trend_detector.praw.Reddit')
    def test_get_reddit_trends(self, mock_reddit, detector):
        """Test Reddit trend fetching"""
        # Mock Reddit submission
        mock_submission = Mock()
        mock_submission.title = 'Trending Streetwear Style'
        mock_submission.selftext = 'Check out this cool outfit'
        mock_submission.score = 250
        mock_submission.url = 'https://reddit.com/test'
        mock_submission.created_utc = datetime.now().timestamp()
        
        mock_subreddit = Mock()
        mock_subreddit.hot.return_value = [mock_submission]
        
        mock_reddit_instance = Mock()
        mock_reddit_instance.subreddit.return_value = mock_subreddit
        detector.reddit = mock_reddit_instance
        
        trends = detector._get_reddit_trends()
        
        assert isinstance(trends, list)
        assert len(trends) == 1
        assert trends[0]['source'] == 'reddit'
        assert trends[0]['score'] == 250
    
    @patch('src.trend_detector.praw.Reddit')
    def test_get_reddit_trends_low_score_filtered(self, mock_reddit, detector):
        """Test Reddit trends filters low-score posts"""
        mock_submission = Mock()
        mock_submission.title = 'Low engagement post'
        mock_submission.score = 50  # Below threshold
        mock_submission.created_utc = datetime.now().timestamp()
        
        mock_subreddit = Mock()
        mock_subreddit.hot.return_value = [mock_submission]
        
        mock_reddit_instance = Mock()
        mock_reddit_instance.subreddit.return_value = mock_subreddit
        detector.reddit = mock_reddit_instance
        
        trends = detector._get_reddit_trends()
        assert len(trends) == 0
    
    @patch('src.trend_detector.tweepy.Client')
    def test_get_twitter_trends(self, mock_twitter, detector):
        """Test Twitter trend fetching"""
        mock_tweet = Mock()
        mock_tweet.text = 'Amazing fashion outfit #ootd'
        mock_tweet.public_metrics = {
            'like_count': 100,
            'retweet_count': 50
        }
        mock_tweet.created_at = datetime.now()
        
        mock_response = Mock()
        mock_response.data = [mock_tweet]
        
        mock_twitter_instance = Mock()
        mock_twitter_instance.search_recent_tweets.return_value = mock_response
        detector.twitter = mock_twitter_instance
        
        trends = detector._get_twitter_trends()
        
        assert isinstance(trends, list)
        if len(trends) > 0:
            assert trends[0]['source'] == 'twitter'
    
    @patch('src.trend_detector.requests.get')
    def test_get_tiktok_trends(self, mock_get, detector):
        """Test TikTok trend scraping"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b'<html><body>Fashion content</body></html>'
        mock_get.return_value = mock_response
        
        trends = detector._get_tiktok_trends()
        
        assert isinstance(trends, list)
    
    def test_get_fashion_trends_integration(self, detector):
        """Test full trend aggregation"""
        with patch.object(detector, '_get_reddit_trends', return_value=[
            {'source': 'reddit', 'title': 'Reddit Trend', 'score': 100, 'keywords': []}
        ]), \
        patch.object(detector, '_get_google_trends', return_value=[
            {'source': 'google', 'title': 'Google Trend', 'score': 80, 'keywords': []}
        ]), \
        patch.object(detector, '_get_twitter_trends', return_value=[]), \
        patch.object(detector, '_get_tiktok_trends', return_value=[]):
            
            trends = detector.get_fashion_trends(num_trends=5)
            
            assert isinstance(trends, list)
            assert len(trends) <= 5
    
    def test_get_niche_trends(self, detector):
        """Test niche-specific trend filtering"""
        all_trends = [
            {'title': 'Streetwear Style Guide', 'keywords': ['streetwear'], 'score': 100},
            {'title': 'Luxury Brand Review', 'keywords': ['luxury'], 'score': 90},
            {'title': 'Tech Gadgets', 'keywords': ['tech'], 'score': 80}
        ]
        
        with patch.object(detector, 'get_fashion_trends', return_value=all_trends):
            niche_trends = detector.get_niche_trends('streetwear', limit=5)
            
            assert len(niche_trends) >= 1
            assert 'streetwear' in niche_trends[0]['title'].lower()
