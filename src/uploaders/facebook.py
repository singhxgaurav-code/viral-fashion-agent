"""
Facebook Reels uploader
"""
from typing import Dict, Optional
import requests
import os

from .base import BasePlatformUploader
import config


class FacebookUploader(BasePlatformUploader):
    """Upload videos to Facebook Reels"""
    
    def __init__(self):
        super().__init__('Facebook')
        self.page_id = config.FACEBOOK_PAGE_ID
        self.access_token = config.FACEBOOK_ACCESS_TOKEN
        self.api_version = 'v18.0'
    
    def authenticate(self) -> bool:
        """Verify Facebook access token"""
        try:
            url = f"https://graph.facebook.com/{self.api_version}/me"
            params = {'access_token': self.access_token}
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                self.logger.info("Facebook authentication successful")
                return True
            else:
                self.logger.error(f"Facebook auth failed: {response.text}")
                return False
                
        except Exception as e:
            self.logger.error(f"Facebook authentication failed: {e}")
            return False
    
    def upload(self, video_path: str, metadata: Dict) -> Optional[str]:
        """Upload video as Facebook Reel"""
        if not self.authenticate():
            return None
        
        platform_config = config.PLATFORMS['facebook']
        if not self.validate_video(
            video_path,
            platform_config['max_file_size_mb'],
            platform_config['max_duration']
        ):
            return None
        
        try:
            # Step 1: Initialize upload
            init_url = f"https://graph.facebook.com/{self.api_version}/{self.page_id}/video_reels"
            
            description = metadata.get('description', '')
            tags = metadata.get('tags', [])
            full_description = f"{description}\n\n{' '.join(['#' + tag for tag in tags])}"
            
            init_params = {
                'access_token': self.access_token,
                'upload_phase': 'start',
                'description': full_description[:1000]  # Facebook limit
            }
            
            init_response = requests.post(init_url, params=init_params)
            
            if init_response.status_code != 200:
                self.logger.error(f"Facebook upload init failed: {init_response.text}")
                return None
            
            video_id = init_response.json().get('video_id')
            upload_session_id = init_response.json().get('upload_session_id')
            
            # Step 2: Upload video file
            with open(video_path, 'rb') as video_file:
                upload_url = f"https://graph.facebook.com/{self.api_version}/{self.page_id}/video_reels"
                upload_params = {
                    'access_token': self.access_token,
                    'upload_phase': 'transfer',
                    'upload_session_id': upload_session_id
                }
                
                files = {'video_file_chunk': video_file}
                upload_response = requests.post(upload_url, params=upload_params, files=files)
                
                if upload_response.status_code != 200:
                    self.logger.error(f"Facebook upload transfer failed: {upload_response.text}")
                    return None
            
            # Step 3: Finalize upload
            finish_params = {
                'access_token': self.access_token,
                'upload_phase': 'finish',
                'upload_session_id': upload_session_id
            }
            
            finish_response = requests.post(init_url, params=finish_params)
            
            if finish_response.status_code == 200:
                reel_url = f"https://www.facebook.com/reel/{video_id}"
                self.logger.info(f"✅ Facebook Reel uploaded: {reel_url}")
                return reel_url
            else:
                self.logger.error(f"Facebook upload finish failed: {finish_response.text}")
                return None
                
        except Exception as e:
            self.logger.error(f"Facebook upload failed: {e}")
            return None
    
    def get_analytics(self, video_id: str) -> Dict:
        """Get Reel analytics"""
        try:
            url = f"https://graph.facebook.com/{self.api_version}/{video_id}"
            params = {
                'fields': 'views,likes.summary(true),comments.summary(true)',
                'access_token': self.access_token
            }
            
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'views': data.get('views', 0),
                    'likes': data.get('likes', {}).get('summary', {}).get('total_count', 0),
                    'comments': data.get('comments', {}).get('summary', {}).get('total_count', 0),
                    'platform': 'facebook'
                }
        except Exception as e:
            self.logger.error(f"Failed to get Facebook analytics: {e}")
        
        return {}
