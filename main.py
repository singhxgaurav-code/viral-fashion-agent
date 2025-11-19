"""
Main orchestrator - coordinates the entire workflow
"""
import os
import sys
import logging
import time
from datetime import datetime
from typing import List, Dict
import schedule

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from trend_detector import TrendDetector
from content_generator import ContentGenerator
from media_creator import MediaCreator
from uploaders import MultiPlatformUploader
from database import Database
import config

# Setup logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('agent.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class ViralFashionAgent:
    """Main agent orchestrating the entire workflow"""
    
    def __init__(self):
        logger.info("Initializing Viral Fashion Agent")
        
        self.trend_detector = TrendDetector()
        self.content_generator = ContentGenerator()
        self.media_creator = MediaCreator()
        self.uploader = MultiPlatformUploader()
        self.db = Database()
        
        # Ensure output directory exists
        os.makedirs(config.OUTPUT_DIR, exist_ok=True)
        
        logger.info("✅ Agent initialized successfully")
    
    def daily_workflow(self):
        """Main daily workflow - generate and upload videos"""
        try:
            logger.info("=" * 60)
            logger.info(f"🚀 Starting daily workflow: {datetime.now()}")
            logger.info("=" * 60)
            
            # Step 1: Detect trends
            logger.info("📊 Step 1: Detecting fashion trends...")
            trends = self.trend_detector.get_fashion_trends(num_trends=config.DAILY_VIDEOS_COUNT)
            
            if not trends:
                logger.error("❌ No trends detected, aborting workflow")
                return
            
            logger.info(f"✅ Detected {len(trends)} trends")
            
            # Save trends to database
            for trend in trends:
                self.db.save_trend(trend)
            
            # Step 2: Generate content for each trend
            logger.info("✍️  Step 2: Generating AI content...")
            content_batch = self.content_generator.generate_batch_content(trends)
            
            if not content_batch:
                logger.error("❌ Content generation failed, aborting workflow")
                return
            
            logger.info(f"✅ Generated {len(content_batch)} video scripts")
            
            # Step 3: Create videos and upload
            successful_uploads = 0
            
            for i, content in enumerate(content_batch, 1):
                logger.info(f"\n{'='*60}")
                logger.info(f"📹 Processing video {i}/{len(content_batch)}")
                logger.info(f"{'='*60}")
                
                try:
                    # Create video
                    video_filename = f"fashion_short_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{i}.mp4"
                    video_path = os.path.join(config.OUTPUT_DIR, video_filename)
                    
                    logger.info(f"🎬 Creating video: {content['metadata']['title']}")
                    
                    success = self.media_creator.create_video(
                        script=content['script'],
                        metadata=content['metadata'],
                        output_path=video_path,
                        aspect_ratio='9:16'  # Vertical for Shorts/Reels/TikTok
                    )
                    
                    if not success:
                        logger.error(f"❌ Video creation failed for item {i}")
                        continue
                    
                    # Save video to database
                    trend_id = None  # Would link to trend if saved
                    video_id = self.db.save_video({
                        'script': content['script'],
                        'metadata': content['metadata'],
                        'file_path': video_path
                    }, trend_id)
                    
                    # Upload to all platforms
                    logger.info("📤 Uploading to all platforms...")
                    
                    upload_results = self.uploader.upload_to_all(
                        video_path,
                        content['metadata']
                    )
                    
                    # Save upload results
                    for platform, url in upload_results.items():
                        if url:
                            self.db.save_upload(video_id, platform, {
                                'url': url,
                                'content_id': self._extract_content_id(url, platform)
                            })
                            successful_uploads += 1
                    
                    # Display results
                    logger.info(f"\n📊 Upload Results for Video {i}:")
                    for platform, url in upload_results.items():
                        status = "✅" if url else "❌"
                        logger.info(f"  {status} {platform.capitalize()}: {url or 'Failed'}")
                    
                    # Clean up video file to save space (optional)
                    # os.remove(video_path)
                    
                    # Stagger uploads
                    if i < len(content_batch):
                        wait_minutes = config.UPLOAD_STAGGER_MINUTES
                        logger.info(f"\n⏸️  Waiting {wait_minutes} minutes before next video...")
                        time.sleep(wait_minutes * 60)
                    
                except Exception as e:
                    logger.error(f"❌ Error processing video {i}: {e}", exc_info=True)
                    continue
            
            # Final summary
            logger.info(f"\n{'='*60}")
            logger.info("📈 DAILY WORKFLOW SUMMARY")
            logger.info(f"{'='*60}")
            logger.info(f"Videos created: {len(content_batch)}")
            logger.info(f"Successful uploads: {successful_uploads}")
            logger.info(f"Total platforms: {len(config.PLATFORMS)}")
            logger.info(f"Completion time: {datetime.now()}")
            logger.info(f"{'='*60}\n")
            
            # Get total analytics
            total_stats = self.db.get_total_analytics()
            logger.info(f"📊 All-time stats: {total_stats}")
            
        except Exception as e:
            logger.error(f"❌ Fatal error in daily workflow: {e}", exc_info=True)
    
    def update_analytics(self):
        """Update analytics for recent uploads"""
        logger.info("📊 Updating analytics...")
        
        try:
            recent_uploads = self.db.get_recent_uploads(limit=50)
            
            for upload in recent_uploads:
                platform = upload['platform']
                content_id = self._extract_content_id(upload['url'], platform)
                
                if content_id and platform in self.uploader.uploaders:
                    stats = self.uploader.uploaders[platform].get_analytics(content_id)
                    
                    if stats:
                        self.db.update_analytics(upload['id'], stats)
                        logger.info(f"Updated {platform} analytics: {stats}")
            
            # Show platform performance
            performance = self.db.get_platform_performance()
            logger.info("\n📊 Platform Performance:")
            for platform in performance:
                logger.info(f"  {platform['platform']}: {platform['total_views']} views, {platform['uploads']} uploads")
                
        except Exception as e:
            logger.error(f"Error updating analytics: {e}")
    
    def _extract_content_id(self, url: str, platform: str) -> str:
        """Extract content ID from URL"""
        if not url:
            return None
        
        try:
            if platform == 'youtube':
                return url.split('/shorts/')[-1]
            elif platform == 'instagram':
                return url.split('/reel/')[-1].rstrip('/')
            elif platform == 'twitter':
                return url.split('/status/')[-1]
            elif platform == 'facebook':
                return url.split('/reel/')[-1]
            elif platform == 'tiktok':
                return url.split('/')[-1]
        except:
            pass
        
        return None
    
    def generate_report(self):
        """Generate performance report"""
        logger.info("\n" + "="*60)
        logger.info("📊 PERFORMANCE REPORT")
        logger.info("="*60)
        
        total_stats = self.db.get_total_analytics()
        platform_stats = self.db.get_platform_performance()
        
        logger.info(f"\n🎯 Total Performance:")
        logger.info(f"  Total Views: {total_stats['total_views']:,}")
        logger.info(f"  Total Likes: {total_stats['total_likes']:,}")
        logger.info(f"  Total Comments: {total_stats['total_comments']:,}")
        logger.info(f"  Total Uploads: {total_stats['total_uploads']}")
        
        logger.info(f"\n📱 By Platform:")
        for platform in platform_stats:
            logger.info(f"  {platform['platform'].capitalize()}:")
            logger.info(f"    Uploads: {platform['uploads']}")
            logger.info(f"    Total Views: {platform['total_views'] or 0:,}")
            logger.info(f"    Avg Views: {platform['avg_views'] or 0:.0f}")
        
        logger.info("="*60 + "\n")


def main():
    """Main entry point"""
    agent = ViralFashionAgent()
    
    # Check command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'test':
            logger.info("Running test workflow...")
            agent.daily_workflow()
        
        elif command == 'analytics':
            agent.update_analytics()
            agent.generate_report()
        
        elif command == 'report':
            agent.generate_report()
        
        else:
            logger.error(f"Unknown command: {command}")
            logger.info("Available commands: test, analytics, report")
    
    else:
        # Schedule daily runs
        logger.info("Starting scheduled agent (daily at 6 AM)")
        
        # Run daily at 6 AM
        schedule.every().day.at("06:00").do(agent.daily_workflow)
        
        # Update analytics every 6 hours
        schedule.every(6).hours.do(agent.update_analytics)
        
        # Generate report weekly
        schedule.every().monday.at("09:00").do(agent.generate_report)
        
        logger.info("Agent is now running. Press Ctrl+C to stop.")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)
        except KeyboardInterrupt:
            logger.info("\n👋 Agent stopped by user")


if __name__ == "__main__":
    main()
