"""
Multi-platform upload manager
"""
import os
from typing import Dict, List, Optional
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

from .youtube import YouTubeUploader
from .tiktok import TikTokUploader
from .instagram import InstagramUploader
from .twitter import TwitterUploader
from .facebook import FacebookUploader
import config

logger = logging.getLogger(__name__)


class MultiPlatformUploader:
    """Manages uploads across all platforms"""
    
    def __init__(self):
        self.uploaders = {}
        self._initialize_uploaders()
    
    def _initialize_uploaders(self):
        """Initialize all enabled platform uploaders"""
        for platform, settings in config.PLATFORMS.items():
            if not settings['enabled']:
                continue
            
            try:
                if platform == 'youtube':
                    self.uploaders['youtube'] = YouTubeUploader()
                elif platform == 'tiktok':
                    self.uploaders['tiktok'] = TikTokUploader()
                elif platform == 'instagram':
                    self.uploaders['instagram'] = InstagramUploader()
                elif platform == 'twitter':
                    self.uploaders['twitter'] = TwitterUploader()
                elif platform == 'facebook':
                    self.uploaders['facebook'] = FacebookUploader()
                
                logger.info(f"Initialized {platform} uploader")
            except Exception as e:
                logger.error(f"Failed to initialize {platform} uploader: {e}")
    
    def upload_to_all(self, video_path: str, metadata: Dict) -> Dict[str, Optional[str]]:
        """
        Upload video to all enabled platforms
        
        Args:
            video_path: Path to video file
            metadata: Video metadata (title, description, tags)
        
        Returns:
            Dict mapping platform name to upload URL/ID
        """
        results = {}
        
        logger.info(f"Starting multi-platform upload: {metadata.get('title', 'Untitled')}")
        
        # Upload to all platforms in parallel
        with ThreadPoolExecutor(max_workers=len(self.uploaders)) as executor:
            futures = {}
            
            for platform, uploader in self.uploaders.items():
                # Customize metadata for each platform if needed
                platform_metadata = self._adapt_metadata(metadata, platform)
                
                future = executor.submit(uploader.upload, video_path, platform_metadata)
                futures[future] = platform
            
            for future in as_completed(futures):
                platform = futures[future]
                try:
                    result = future.result()
                    results[platform] = result
                    
                    if result:
                        logger.info(f"✅ {platform}: {result}")
                    else:
                        logger.warning(f"❌ {platform}: Upload failed")
                        
                except Exception as e:
                    logger.error(f"❌ {platform}: Exception - {e}")
                    results[platform] = None
        
        return results
    
    def _adapt_metadata(self, metadata: Dict, platform: str) -> Dict:
        """Adapt metadata for specific platform requirements"""
        adapted = metadata.copy()
        
        if platform == 'youtube':
            # YouTube specific adaptations
            adapted['description'] = f"{metadata['description']}\n\n#Shorts"
            
        elif platform == 'tiktok':
            # TikTok loves short, punchy captions
            desc = metadata['description']
            if len(desc) > 150:
                desc = desc[:147] + "..."
            adapted['description'] = desc
            
        elif platform == 'instagram':
            # Instagram benefits from more hashtags
            tags = metadata.get('tags', [])[:30]
            desc = metadata['description']
            hashtags = ' '.join([f'#{tag}' for tag in tags])
            adapted['description'] = f"{desc}\n\n{hashtags}"
            
        elif platform == 'twitter':
            # Twitter has character limit
            desc = metadata['description']
            if len(desc) > 250:
                desc = desc[:247] + "..."
            adapted['description'] = desc
            
        elif platform == 'facebook':
            # Facebook similar to Instagram
            pass
        
        return adapted
    
    def get_all_analytics(self, upload_results: Dict[str, str]) -> Dict:
        """Get analytics from all platforms"""
        analytics = {}
        
        for platform, content_id in upload_results.items():
            if not content_id or platform not in self.uploaders:
                continue
            
            try:
                stats = self.uploaders[platform].get_analytics(content_id)
                analytics[platform] = stats
            except Exception as e:
                logger.error(f"Failed to get {platform} analytics: {e}")
        
        return analytics
    
    def get_total_reach(self, analytics: Dict) -> Dict:
        """Calculate total reach across all platforms"""
        total = {
            'total_views': 0,
            'total_likes': 0,
            'total_comments': 0,
            'total_shares': 0
        }
        
        for platform, stats in analytics.items():
            total['total_views'] += stats.get('views', 0)
            total['total_likes'] += stats.get('likes', 0)
            total['total_comments'] += stats.get('comments', 0)
            total['total_shares'] += stats.get('retweets', 0) + stats.get('shares', 0)
        
        return total
