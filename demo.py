#!/usr/bin/env python3
"""
Demo script to test the viral fashion agent workflow locally.
This generates a single video without uploading to platforms.
"""

# Fix SSL certificates BEFORE any other imports
import os
import ssl
import certifi
os.environ['SSL_CERT_FILE'] = certifi.where()
os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()
os.environ['CURL_CA_BUNDLE'] = certifi.where()

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from trend_detector import TrendDetector
from content_generator import ContentGenerator
from media_creator import MediaCreator
from database import Database
import config


def main():
    """Run a simple demo workflow."""
    print("🎬 Viral Fashion Agent - Demo Mode")
    print("=" * 50)
    
    # Initialize components
    db = Database()
    trend_detector = TrendDetector()
    content_generator = ContentGenerator()
    media_creator = MediaCreator()
    
    # Step 1: Detect trends (or use a sample trend)
    print("\n📊 Step 1: Detecting fashion trends...")
    try:
        trends = trend_detector.get_fashion_trends(num_trends=1)
        if trends:
            trend = trends[0]
            print(f"✅ Found trend: {trend['title']}")
        else:
            # Fallback to sample trend
            print("⚠️  No trends detected, using sample trend")
            trend = {
                'source': 'demo',
                'title': 'Oversized Blazers Fall 2024',
                'keywords': ['oversized blazers', 'fall fashion', 'business casual'],
                'score': 100,
                'url': 'demo'
            }
    except Exception as e:
        print(f"⚠️  Trend detection failed ({e}), using sample trend")
        trend = {
            'source': 'demo',
            'title': 'Oversized Blazers Fall 2024',
            'keywords': ['oversized blazers', 'fall fashion', 'business casual'],
            'score': 100,
            'url': 'demo'
        }
    
    # Step 2: Generate content
    print("\n✍️  Step 2: Generating AI script...")
    try:
        script = content_generator.generate_script(trend)
        metadata = content_generator.generate_metadata(script, trend)
        metadata['script'] = script
        metadata['estimated_duration'] = len(script.split()) / 2.5  # ~2.5 words per second
        print(f"✅ Generated script: '{metadata['title']}'")
        print(f"\n📝 Script Preview:")
        print("-" * 50)
        print(script[:200] + "...")
        print("-" * 50)
        print(f"📊 Metadata:")
        print(f"  - Hashtags: {', '.join(metadata['hashtags'][:5])}")
        print(f"  - Duration: ~{int(metadata['estimated_duration'])}s")
    except Exception as e:
        print(f"❌ Script generation failed: {e}")
        print("\n💡 To fix this:")
        print("  1. Sign up at https://console.groq.com/")
        print("  2. Get a free API key")
        print("  3. Add to .env: GROQ_API_KEY=your_key_here")
        return 1
    
    # Step 3: Create video
    print("\n🎥 Step 3: Creating video...")
    try:
        # Create output directory
        os.makedirs(config.OUTPUT_DIR, exist_ok=True)
        
        # Generate output path
        from datetime import datetime
        timestamp = int(datetime.now().timestamp())
        output_path = os.path.join(config.OUTPUT_DIR, f"video_{timestamp}.mp4")
        
        # Create video with correct API
        success = media_creator.create_video(
            script=script,
            metadata=metadata,
            output_path=output_path
        )
        
        if success:
            print(f"✅ Video created: {output_path}")
        
            # Get video info
            file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
            print(f"\n📹 Video Details:")
            print(f"  - Path: {output_path}")
            print(f"  - Size: {file_size_mb:.2f} MB")
            print(f"  - Format: 1080x1920 (vertical)")
        
            # Save to database
            video_id = db.add_video(
                trend_id=db.add_trend(
                    source=trend['source'],
                    title=trend['title'],
                    keywords=trend['keywords'],
                    score=trend['score'],
                    url=trend.get('url', 'demo')
                ),
                title=metadata['title'],
                description=metadata['description'],
                script=script,
                hashtags=metadata['hashtags'],
                file_path=output_path,
                duration=metadata.get('estimated_duration', 45)
            )
            print(f"  - Database ID: {video_id}")
        else:
            print("❌ Video creation returned False")
            return 1
        
    except Exception as e:
        print(f"❌ Video creation failed: {e}")
        print("\n💡 Common issues:")
        print("  - FFmpeg not installed: brew install ffmpeg")
        print("  - Missing API keys: PEXELS_API_KEY or UNSPLASH_ACCESS_KEY in .env")
        print("  - Edge-TTS issue: Check internet connection")
        return 1
    
    # Step 4: Platform upload (skipped in demo)
    print("\n📤 Step 4: Platform Upload (DEMO - SKIPPED)")
    print("  ⏭️  Skipping uploads to YouTube, TikTok, Instagram, Twitter, Facebook")
    print("  💡 To enable uploads, configure platform credentials in .env")
    
    print("\n" + "=" * 50)
    print("✅ Demo completed successfully!")
    print(f"\n🎉 Your video is ready: {output_path}")
    print(f"\n📁 Open the video:")
    print(f"  open {output_path}")
    print("\n💡 Next steps:")
    print("  1. Configure platform credentials in .env")
    print("  2. Run: python main.py test (full workflow with uploads)")
    print("  3. Run: python main.py (scheduled daily mode)")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
