"""
Twitter/X video uploader
"""
from typing import Dict, Optional
import os
import tweepy

from .base import BasePlatformUploader
import config


class TwitterUploader(BasePlatformUploader):
    """Upload videos to Twitter/X"""
    
    def __init__(self):
        super().__init__('Twitter')
        self.client = None
        self.api = None
    
    def authenticate(self) -> bool:
        """Authenticate with Twitter API v2"""
        try:
            # Twitter API v2 client
            self.client = tweepy.Client(
                consumer_key=os.getenv('TWITTER_CONSUMER_KEY'),
                consumer_secret=os.getenv('TWITTER_CONSUMER_SECRET'),
                access_token=os.getenv('TWITTER_ACCESS_TOKEN_POST'),
                access_token_secret=os.getenv('TWITTER_ACCESS_SECRET_POST')
            )
            
            # API v1.1 for media upload
            auth = tweepy.OAuth1UserHandler(
                os.getenv('TWITTER_CONSUMER_KEY'),
                os.getenv('TWITTER_CONSUMER_SECRET'),
                os.getenv('TWITTER_ACCESS_TOKEN_POST'),
                os.getenv('TWITTER_ACCESS_SECRET_POST')
            )
            self.api = tweepy.API(auth)
            
            # Verify credentials
            self.client.get_me()
            self.logger.info("Twitter authentication successful")
            return True
            
        except Exception as e:
            self.logger.error(f"Twitter authentication failed: {e}")
            return False
    
    def upload(self, video_path: str, metadata: Dict) -> Optional[str]:
        """Upload video to Twitter"""
        if not self.api or not self.client:
            if not self.authenticate():
                return None
        
        platform_config = config.PLATFORMS['twitter']
        if not self.validate_video(
            video_path,
            platform_config['max_file_size_mb'],
            platform_config['max_duration']
        ):
            return None
        
        try:
            # Upload media (uses v1.1 API)
            media = self.api.media_upload(
                filename=video_path,
                media_category='tweet_video'
            )
            
            # Create tweet with video (v2 API)
            tweet_text = metadata.get('description', '')[:280]  # Twitter max 280 chars
            
            # Add hashtags if space allows
            tags = metadata.get('tags', [])
            for tag in tags:
                test_text = f"{tweet_text} #{tag}"
                if len(test_text) <= 280:
                    tweet_text = test_text
                else:
                    break
            
            response = self.client.create_tweet(
                text=tweet_text,
                media_ids=[media.media_id]
            )
            
            tweet_id = response.data['id']
            username = self.client.get_me().data.username
            tweet_url = f"https://twitter.com/{username}/status/{tweet_id}"
            
            self.logger.info(f"✅ Twitter video uploaded: {tweet_url}")
            return tweet_url
            
        except Exception as e:
            self.logger.error(f"Twitter upload failed: {e}")
            return None
    
    def get_analytics(self, tweet_id: str) -> Dict:
        """Get tweet analytics"""
        try:
            tweet = self.client.get_tweet(
                tweet_id,
                tweet_fields=['public_metrics']
            )
            
            metrics = tweet.data.public_metrics
            return {
                'views': metrics.get('impression_count', 0),
                'likes': metrics.get('like_count', 0),
                'retweets': metrics.get('retweet_count', 0),
                'replies': metrics.get('reply_count', 0),
                'platform': 'twitter'
            }
        except Exception as e:
            self.logger.error(f"Failed to get Twitter analytics: {e}")
            return {}
