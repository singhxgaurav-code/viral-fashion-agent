"""
YouTube Shorts uploader
"""
from typing import Dict, Optional
import os
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import pickle

from .base import BasePlatformUploader
import config


class YouTubeUploader(BasePlatformUploader):
    """Upload videos to YouTube Shorts"""
    
    SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
    
    def __init__(self):
        super().__init__('YouTube')
        self.youtube = None
    
    def authenticate(self) -> bool:
        """Authenticate with YouTube API"""
        creds = None
        token_file = 'youtube_token.pickle'
        
        # Load existing credentials
        if os.path.exists(token_file):
            with open(token_file, 'rb') as token:
                creds = pickle.load(token)
        
        # Refresh or get new credentials
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(config.YOUTUBE_CLIENT_SECRETS):
                    self.logger.error("YouTube client secrets file not found")
                    return False
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    config.YOUTUBE_CLIENT_SECRETS, self.SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save credentials
            with open(token_file, 'wb') as token:
                pickle.dump(creds, token)
        
        try:
            self.youtube = build('youtube', 'v3', credentials=creds)
            self.logger.info("YouTube authentication successful")
            return True
        except Exception as e:
            self.logger.error(f"YouTube authentication failed: {e}")
            return False
    
    def upload(self, video_path: str, metadata: Dict) -> Optional[str]:
        """Upload video as YouTube Short"""
        if not self.youtube:
            if not self.authenticate():
                return None
        
        # Validate video
        platform_config = config.PLATFORMS['youtube']
        if not self.validate_video(
            video_path, 
            platform_config['max_file_size_mb'],
            platform_config['max_duration']
        ):
            return None
        
        # Prepare metadata
        title = metadata.get('title', 'Fashion Trend')[:100]  # YouTube max 100 chars
        description = metadata.get('description', '')
        tags = metadata.get('tags', [])[:500]  # Max 500 chars total
        
        # Add #Shorts to description to mark as Short
        if '#Shorts' not in description:
            description = f"{description}\n\n#Shorts"
        
        body = {
            'snippet': {
                'title': title,
                'description': description,
                'tags': tags,
                'categoryId': '26',  # Howto & Style
            },
            'status': {
                'privacyStatus': 'public',
                'selfDeclaredMadeForKids': False,
            }
        }
        
        try:
            media = MediaFileUpload(
                video_path,
                chunksize=-1,
                resumable=True,
                mimetype='video/mp4'
            )
            
            request = self.youtube.videos().insert(
                part='snippet,status',
                body=body,
                media_body=media
            )
            
            response = None
            while response is None:
                status, response = request.next_chunk()
                if status:
                    self.logger.info(f"Upload progress: {int(status.progress() * 100)}%")
            
            video_id = response['id']
            video_url = f"https://youtube.com/shorts/{video_id}"
            self.logger.info(f"✅ YouTube upload successful: {video_url}")
            return video_url
            
        except Exception as e:
            self.logger.error(f"YouTube upload failed: {e}")
            return None
    
    def get_analytics(self, video_id: str) -> Dict:
        """Get video analytics"""
        if not self.youtube:
            return {}
        
        try:
            response = self.youtube.videos().list(
                part='statistics,snippet',
                id=video_id
            ).execute()
            
            if response['items']:
                stats = response['items'][0]['statistics']
                return {
                    'views': int(stats.get('viewCount', 0)),
                    'likes': int(stats.get('likeCount', 0)),
                    'comments': int(stats.get('commentCount', 0)),
                    'platform': 'youtube'
                }
        except Exception as e:
            self.logger.error(f"Failed to get analytics: {e}")
        
        return {}
