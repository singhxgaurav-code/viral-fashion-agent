"""
Instagram Reels uploader
"""
from typing import Dict, Optional
import time
from instagrapi import Client
from instagrapi.exceptions import LoginRequired

from .base import BasePlatformUploader
import config


class InstagramUploader(BasePlatformUploader):
    """Upload videos to Instagram Reels"""
    
    def __init__(self):
        super().__init__('Instagram')
        self.client = Client()
        self.session_file = 'instagram_session.json'
    
    def authenticate(self) -> bool:
        """Authenticate with Instagram"""
        try:
            # Try to load existing session
            try:
                self.client.load_settings(self.session_file)
                self.client.login(config.INSTAGRAM_USERNAME, config.INSTAGRAM_PASSWORD)
                
                # Check if session is valid
                self.client.get_timeline_feed()
                self.logger.info("Instagram session loaded successfully")
                return True
                
            except (LoginRequired, FileNotFoundError):
                # Fresh login required
                self.logger.info("Performing fresh Instagram login")
                
                self.client.login(config.INSTAGRAM_USERNAME, config.INSTAGRAM_PASSWORD)
                self.client.dump_settings(self.session_file)
                
                self.logger.info("Instagram authentication successful")
                return True
                
        except Exception as e:
            self.logger.error(f"Instagram authentication failed: {e}")
            return False
    
    def upload(self, video_path: str, metadata: Dict) -> Optional[str]:
        """Upload video as Instagram Reel"""
        if not self.client.user_id:
            if not self.authenticate():
                return None
        
        platform_config = config.PLATFORMS['instagram']
        if not self.validate_video(
            video_path,
            platform_config['max_file_size_mb'],
            platform_config['max_duration']
        ):
            return None
        
        try:
            caption = metadata.get('description', '')[:2200]  # Instagram max 2200 chars
            
            # Add hashtags
            tags = metadata.get('tags', [])
            hashtag_str = ' '.join([f'#{tag}' for tag in tags[:30]])  # Max 30 hashtags
            full_caption = f"{caption}\n\n{hashtag_str}"
            
            # Upload as Reel
            media = self.client.clip_upload(
                video_path,
                caption=full_caption,
                extra_data={
                    "custom_accessibility_caption": metadata.get('title', ''),
                    "like_and_view_counts_disabled": False,
                    "disable_comments": False,
                }
            )
            
            media_url = f"https://www.instagram.com/reel/{media.code}/"
            self.logger.info(f"✅ Instagram Reel uploaded: {media_url}")
            return media_url
            
        except Exception as e:
            self.logger.error(f"Instagram upload failed: {e}")
            return None
    
    def get_analytics(self, media_code: str) -> Dict:
        """Get Reel analytics"""
        try:
            media_pk = self.client.media_pk_from_code(media_code)
            media_info = self.client.media_info(media_pk)
            
            return {
                'views': media_info.play_count or 0,
                'likes': media_info.like_count or 0,
                'comments': media_info.comment_count or 0,
                'platform': 'instagram'
            }
        except Exception as e:
            self.logger.error(f"Failed to get Instagram analytics: {e}")
            return {}
