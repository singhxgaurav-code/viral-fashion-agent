"""
Multi-platform uploader base class
"""
from abc import ABC, abstractmethod
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class BasePlatformUploader(ABC):
    """Base class for all platform uploaders"""
    
    def __init__(self, platform_name: str):
        self.platform_name = platform_name
        self.logger = logging.getLogger(f"{__name__}.{platform_name}")
    
    @abstractmethod
    def authenticate(self) -> bool:
        """Authenticate with the platform"""
        pass
    
    @abstractmethod
    def upload(self, video_path: str, metadata: Dict) -> Optional[str]:
        """
        Upload video to platform
        
        Args:
            video_path: Path to video file
            metadata: Dict containing title, description, tags, etc.
        
        Returns:
            URL or ID of uploaded content, None if failed
        """
        pass
    
    @abstractmethod
    def get_analytics(self, content_id: str) -> Dict:
        """Get analytics for uploaded content"""
        pass
    
    def validate_video(self, video_path: str, max_size_mb: int, max_duration: int) -> bool:
        """Validate video meets platform requirements"""
        import os
        from moviepy.editor import VideoFileClip
        
        # Check file size
        file_size_mb = os.path.getsize(video_path) / (1024 * 1024)
        if file_size_mb > max_size_mb:
            self.logger.error(f"Video too large: {file_size_mb:.2f}MB > {max_size_mb}MB")
            return False
        
        # Check duration
        try:
            clip = VideoFileClip(video_path)
            duration = clip.duration
            clip.close()
            
            if duration > max_duration:
                self.logger.error(f"Video too long: {duration}s > {max_duration}s")
                return False
        except Exception as e:
            self.logger.error(f"Error validating video: {e}")
            return False
        
        return True
