"""
Trend detection across multiple platforms
"""
from typing import List, Dict
import logging
from datetime import datetime, timedelta
import praw
from pytrends.request import TrendReq
import tweepy
import requests
from bs4 import BeautifulSoup

import config

logger = logging.getLogger(__name__)


class TrendDetector:
    """Detect fashion trends from multiple sources"""
    
    def __init__(self):
        self.reddit = None
        self.twitter = None
        self.pytrends = TrendReq(hl='en-US', tz=360)
        self._initialize_apis()
    
    def _initialize_apis(self):
        """Initialize API clients"""
        # Reddit
        try:
            if config.REDDIT_CLIENT_ID and config.REDDIT_CLIENT_SECRET:
                self.reddit = praw.Reddit(
                    client_id=config.REDDIT_CLIENT_ID,
                    client_secret=config.REDDIT_CLIENT_SECRET,
                    user_agent=config.REDDIT_USER_AGENT
                )
                logger.info("Reddit API initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Reddit: {e}")
        
        # Twitter
        try:
            if config.TWITTER_BEARER_TOKEN:
                self.twitter = tweepy.Client(bearer_token=config.TWITTER_BEARER_TOKEN)
                logger.info("Twitter API initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Twitter: {e}")
    
    def get_fashion_trends(self, num_trends: int = 10) -> List[Dict]:
        """
        Aggregate fashion trends from all sources
        
        Returns:
            List of trend dicts with keys: source, title, score, keywords, url
        """
        all_trends = []
        
        # Get trends from each source
        all_trends.extend(self._get_reddit_trends())
        all_trends.extend(self._get_google_trends())
        all_trends.extend(self._get_twitter_trends())
        all_trends.extend(self._get_tiktok_trends())
        
        # Sort by score/relevance
        all_trends.sort(key=lambda x: x.get('score', 0), reverse=True)
        
        # Remove duplicates and return top N
        unique_trends = self._deduplicate_trends(all_trends)
        
        logger.info(f"Found {len(unique_trends)} unique trends")
        return unique_trends[:num_trends]
    
    def _get_reddit_trends(self) -> List[Dict]:
        """Get trending topics from fashion subreddits"""
        trends = []
        
        if not self.reddit:
            return trends
        
        try:
            subreddit_str = '+'.join(config.REDDIT_SUBREDDITS)
            subreddit = self.reddit.subreddit(subreddit_str)
            
            for submission in subreddit.hot(limit=50):
                # Filter for relevant fashion content
                if submission.score < 100:  # Minimum threshold
                    continue
                
                trends.append({
                    'source': 'reddit',
                    'title': submission.title,
                    'description': submission.selftext[:500] if submission.selftext else '',
                    'score': submission.score,
                    'url': submission.url,
                    'keywords': self._extract_keywords(submission.title),
                    'timestamp': datetime.fromtimestamp(submission.created_utc)
                })
            
            logger.info(f"Found {len(trends)} Reddit trends")
        except Exception as e:
            logger.error(f"Error fetching Reddit trends: {e}")
        
        return trends
    
    def _get_google_trends(self) -> List[Dict]:
        """Get trending fashion searches from Google"""
        trends = []
        
        try:
            # Real-time trending searches
            trending_searches = self.pytrends.trending_searches(pn='united_states')
            
            for keyword in trending_searches.head(20)[0].values:
                # Filter for fashion-related terms
                if self._is_fashion_related(keyword):
                    trends.append({
                        'source': 'google_trends',
                        'title': keyword,
                        'keywords': [keyword],
                        'score': 80,  # Default score for Google Trends
                        'timestamp': datetime.now()
                    })
            
            # Also check specific fashion keywords
            fashion_keywords = ['fashion trends', 'street style', 'outfit ideas', 'fashion 2025']
            self.pytrends.build_payload(fashion_keywords, timeframe='now 1-d')
            
            interest = self.pytrends.interest_over_time()
            if not interest.empty:
                for keyword in fashion_keywords:
                    if keyword in interest.columns:
                        score = int(interest[keyword].mean())
                        if score > 20:
                            trends.append({
                                'source': 'google_trends',
                                'title': f"Growing interest in {keyword}",
                                'keywords': [keyword],
                                'score': score,
                                'timestamp': datetime.now()
                            })
            
            logger.info(f"Found {len(trends)} Google Trends")
        except Exception as e:
            logger.error(f"Error fetching Google Trends: {e}")
        
        return trends
    
    def _get_twitter_trends(self) -> List[Dict]:
        """Get trending fashion topics from Twitter"""
        trends = []
        
        if not self.twitter:
            return trends
        
        try:
            # Search for fashion hashtags
            for hashtag in config.TWITTER_HASHTAGS[:5]:  # Limit API calls
                query = f"{hashtag} -is:retweet lang:en"
                tweets = self.twitter.search_recent_tweets(
                    query=query,
                    max_results=10,
                    tweet_fields=['public_metrics', 'created_at']
                )
                
                if not tweets.data:
                    continue
                
                for tweet in tweets.data:
                    metrics = tweet.public_metrics
                    engagement = metrics['like_count'] + metrics['retweet_count']
                    
                    if engagement > 50:  # Minimum threshold
                        trends.append({
                            'source': 'twitter',
                            'title': tweet.text[:100],
                            'description': tweet.text,
                            'score': engagement,
                            'keywords': self._extract_keywords(tweet.text),
                            'timestamp': tweet.created_at
                        })
            
            logger.info(f"Found {len(trends)} Twitter trends")
        except Exception as e:
            logger.error(f"Error fetching Twitter trends: {e}")
        
        return trends
    
    def _get_tiktok_trends(self) -> List[Dict]:
        """
        Get trending fashion content from TikTok
        Note: Uses web scraping as TikTok API is restricted
        """
        trends = []
        
        try:
            # Scrape TikTok trending hashtags (public data)
            url = "https://www.tiktok.com/tag/fashion"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # This is a simplified example - actual scraping would need more robust parsing
                # Consider using TikTok's official API if available or alternative data sources
                
                trends.append({
                    'source': 'tiktok',
                    'title': 'Check TikTok trending manually',
                    'keywords': ['fashion', 'tiktok'],
                    'score': 50,
                    'timestamp': datetime.now()
                })
            
            logger.info(f"Found {len(trends)} TikTok trends")
        except Exception as e:
            logger.error(f"Error fetching TikTok trends: {e}")
        
        return trends
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract relevant keywords from text"""
        # Simple keyword extraction - could be enhanced with NLP
        import re
        
        # Remove URLs, mentions, hashtags symbols
        cleaned = re.sub(r'http\S+|@\S+|#', '', text.lower())
        
        # Extract words
        words = re.findall(r'\b\w+\b', cleaned)
        
        # Filter for fashion-related terms
        fashion_terms = []
        for word in words:
            if len(word) > 3 and self._is_fashion_related(word):
                fashion_terms.append(word)
        
        return fashion_terms[:5]
    
    def _is_fashion_related(self, text: str) -> bool:
        """Check if text is fashion-related"""
        fashion_keywords = [
            'fashion', 'style', 'outfit', 'clothing', 'wear', 'dress', 'shoes',
            'sneakers', 'streetwear', 'designer', 'brand', 'trend', 'look',
            'aesthetic', 'fit', 'drip', 'ootd', 'vintage', 'luxury', 'casual',
            'formal', 'accessories', 'jewelry', 'bag', 'jacket', 'coat', 'pants',
            'jeans', 'shirt', 'hoodie', 'sweater', 'boots', 'sustainable'
        ]
        
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in fashion_keywords)
    
    def _deduplicate_trends(self, trends: List[Dict]) -> List[Dict]:
        """Remove duplicate or very similar trends"""
        unique = []
        seen_titles = set()
        
        for trend in trends:
            title = trend['title'].lower()
            
            # Check for exact duplicates
            if title in seen_titles:
                continue
            
            # Check for very similar titles (simple similarity)
            is_similar = False
            for seen_title in seen_titles:
                # If 70% of words match, consider it similar
                title_words = set(title.split())
                seen_words = set(seen_title.split())
                
                if len(title_words) > 0:
                    overlap = len(title_words & seen_words) / len(title_words)
                    if overlap > 0.7:
                        is_similar = True
                        break
            
            if not is_similar:
                unique.append(trend)
                seen_titles.add(title)
        
        return unique
    
    def get_niche_trends(self, niche: str, limit: int = 5) -> List[Dict]:
        """Get trends for a specific fashion niche"""
        all_trends = self.get_fashion_trends(num_trends=50)
        
        # Filter for niche-specific trends
        niche_trends = []
        niche_keywords = niche.lower().split()
        
        for trend in all_trends:
            trend_text = f"{trend['title']} {' '.join(trend.get('keywords', []))}".lower()
            
            if any(keyword in trend_text for keyword in niche_keywords):
                niche_trends.append(trend)
                
                if len(niche_trends) >= limit:
                    break
        
        return niche_trends
