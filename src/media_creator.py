"""
Media creation: TTS, video editing, captions
"""
from typing import Dict, Optional, List
import logging
import os
import random
from moviepy.editor import (
    VideoFileClip, AudioFileClip, ImageClip, TextClip,
    CompositeVideoClip, concatenate_videoclips
)
from moviepy.video.fx import resize
import requests
from PIL import Image, ImageDraw, ImageFont
import numpy as np

import config

logger = logging.getLogger(__name__)


class MediaCreator:
    """Create videos with voiceover, visuals, and captions"""
    
    def __init__(self):
        self.tts_engine = 'edge'  # 'edge', 'coqui', or 'gtts'
        self.pexels_key = config.PEXELS_API_KEY
        self.unsplash_key = config.UNSPLASH_ACCESS_KEY
    
    def create_video(
        self,
        script: str,
        metadata: Dict,
        output_path: str,
        aspect_ratio: str = '9:16',
        platform: str = 'youtube'
    ) -> bool:
        """
        Create complete short-form video
        
        Args:
            script: Voiceover script
            metadata: Video metadata with keywords
            output_path: Where to save video
            aspect_ratio: '9:16' (vertical), '1:1' (square), or '16:9' (horizontal)
            platform: Target platform for optimization
        
        Returns:
            True if successful
        """
        try:
            logger.info(f"Creating video: {metadata['title']}")
            
            # Step 1: Generate voiceover
            audio_path = output_path.replace('.mp4', '_audio.mp3')
            if not self.generate_voiceover(script, audio_path):
                logger.error("Voiceover generation failed")
                return False
            
            # Step 2: Get video duration from audio
            audio_clip = AudioFileClip(audio_path)
            duration = audio_clip.duration
            
            # Step 3: Fetch visual content
            keywords = metadata.get('keywords', ['fashion'])
            video_clips = self.fetch_stock_videos(keywords, duration, aspect_ratio)
            
            # If no videos, use images instead
            if not video_clips:
                video_clips = self.create_slideshow_from_images(keywords, duration, aspect_ratio)
            
            # Step 4: Combine video clips
            final_video = concatenate_videoclips(video_clips, method="compose")
            
            # Step 5: Add audio
            final_video = final_video.set_audio(audio_clip)
            
            # Step 6: Add captions
            final_video = self.add_captions(final_video, script, aspect_ratio)
            
            # Step 7: Add intro/outro branding (optional)
            final_video = self.add_branding(final_video, aspect_ratio)
            
            # Step 8: Export video
            specs = self._get_video_specs(aspect_ratio)
            final_video.write_videofile(
                output_path,
                fps=specs['fps'],
                codec='libx264',
                audio_codec='aac',
                preset='medium',
                threads=4
            )
            
            # Cleanup
            audio_clip.close()
            final_video.close()
            for clip in video_clips:
                clip.close()
            
            if os.path.exists(audio_path):
                os.remove(audio_path)
            
            logger.info(f"✅ Video created: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Video creation failed: {e}")
            return False
    
    def generate_voiceover(self, script: str, output_path: str) -> bool:
        """Generate voiceover from script with automatic fallback"""
        
        # Try multiple TTS providers in order
        providers = ['gtts', 'edge', 'coqui']
        
        for provider in providers:
            try:
                logger.info(f"Trying TTS provider: {provider}")
                
                if provider == 'gtts':
                    # Google TTS (simple, works through most proxies)
                    from gtts import gTTS
                    tts = gTTS(text=script, lang='en', slow=False)
                    tts.save(output_path)
                    logger.info(f"✅ gTTS succeeded")
                    return os.path.exists(output_path)
                    
                elif provider == 'edge':
                    # Edge-TTS (Microsoft, free, high quality)
                    import edge_tts
                    import asyncio
                    
                    async def generate():
                        # Use different voices for variety
                        voices = [
                            'en-US-JennyNeural',  # Female
                            'en-US-GuyNeural',     # Male
                            'en-GB-SoniaNeural',   # British Female
                            'en-AU-NatashaNeural'  # Australian Female
                        ]
                        voice = random.choice(voices)
                        
                        communicate = edge_tts.Communicate(script, voice)
                        await communicate.save(output_path)
                    
                    asyncio.run(generate())
                    logger.info(f"✅ Edge-TTS succeeded")
                    return os.path.exists(output_path)
                    
                elif provider == 'coqui':
                    # Coqui TTS (local, open-source)
                    from TTS.api import TTS
                    tts = TTS("tts_models/en/ljspeech/tacotron2-DDC")
                    tts.tts_to_file(text=script, file_path=output_path)
                    logger.info(f"✅ Coqui TTS succeeded")
                    return os.path.exists(output_path)
                    
            except Exception as e:
                logger.warning(f"TTS provider {provider} failed: {e}")
                continue
        
        logger.error("❌ All TTS providers failed")
        return False
    
    def fetch_stock_videos(self, keywords: List[str], duration: float, aspect_ratio: str) -> List[VideoFileClip]:
        """Fetch stock video clips from Pexels"""
        clips = []
        
        if not self.pexels_key:
            logger.warning("Pexels API key not configured")
            return clips
        
        try:
            keyword = keywords[0] if keywords else 'fashion'
            url = f"https://api.pexels.com/videos/search"
            params = {
                'query': keyword,
                'per_page': 5,
                'orientation': 'portrait' if aspect_ratio == '9:16' else 'landscape'
            }
            headers = {'Authorization': self.pexels_key}
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            
            if response.status_code != 200:
                logger.warning(f"Pexels API error: {response.status_code}")
                return clips
            
            data = response.json()
            videos = data.get('videos', [])
            
            # Download and create clips
            target_per_clip = duration / min(len(videos), 3)
            
            for i, video in enumerate(videos[:3]):
                # Get best quality file
                video_file = video['video_files'][0]
                video_url = video_file['link']
                
                # Download video
                temp_path = f"temp_clip_{i}.mp4"
                video_response = requests.get(video_url, timeout=30)
                
                with open(temp_path, 'wb') as f:
                    f.write(video_response.content)
                
                # Create clip
                clip = VideoFileClip(temp_path)
                
                # Trim to needed duration
                if clip.duration > target_per_clip:
                    start = random.uniform(0, clip.duration - target_per_clip)
                    clip = clip.subclip(start, start + target_per_clip)
                
                # Resize to match aspect ratio
                specs = self._get_video_specs(aspect_ratio)
                clip = clip.resize((specs['width'], specs['height']))
                
                clips.append(clip)
                
                # Clean up temp file
                if os.path.exists(temp_path):
                    os.remove(temp_path)
            
            logger.info(f"Fetched {len(clips)} stock video clips")
            
        except Exception as e:
            logger.error(f"Error fetching stock videos: {e}")
        
        return clips
    
    def create_slideshow_from_images(self, keywords: List[str], duration: float, aspect_ratio: str) -> List[VideoFileClip]:
        """Create video from stock images as fallback"""
        clips = []
        
        try:
            keyword = keywords[0] if keywords else 'fashion'
            
            # Fetch images from Unsplash
            if self.unsplash_key:
                url = f"https://api.unsplash.com/search/photos"
                params = {
                    'query': keyword,
                    'per_page': 5,
                    'orientation': 'portrait' if aspect_ratio == '9:16' else 'landscape'
                }
                headers = {'Authorization': f'Client-ID {self.unsplash_key}'}
                
                response = requests.get(url, params=params, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    images = data.get('results', [])
                    
                    per_image_duration = duration / max(len(images), 1)
                    specs = self._get_video_specs(aspect_ratio)
                    
                    for i, img in enumerate(images[:5]):
                        img_url = img['urls']['regular']
                        
                        # Download image
                        img_response = requests.get(img_url, timeout=10)
                        temp_img_path = f"temp_img_{i}.jpg"
                        
                        with open(temp_img_path, 'wb') as f:
                            f.write(img_response.content)
                        
                        # Create image clip with Ken Burns effect
                        img_clip = ImageClip(temp_img_path, duration=per_image_duration)
                        img_clip = img_clip.resize((specs['width'], specs['height']))
                        
                        # Add zoom effect
                        img_clip = img_clip.resize(lambda t: 1 + 0.1 * t / per_image_duration)
                        
                        clips.append(img_clip)
                        
                        # Cleanup
                        if os.path.exists(temp_img_path):
                            os.remove(temp_img_path)
            
            logger.info(f"Created slideshow with {len(clips)} images")
            
        except Exception as e:
            logger.error(f"Error creating image slideshow: {e}")
        
        return clips
    
    def add_captions(self, video_clip: VideoFileClip, script: str, aspect_ratio: str) -> VideoFileClip:
        """Add animated captions to video"""
        try:
            # Split script into words for word-by-word captions
            words = script.split()
            words_per_caption = 3  # Show 3 words at a time
            
            caption_clips = []
            duration_per_word = video_clip.duration / len(words)
            
            specs = self._get_video_specs(aspect_ratio)
            
            for i in range(0, len(words), words_per_caption):
                caption_text = ' '.join(words[i:i+words_per_caption])
                start_time = i * duration_per_word
                duration = min(words_per_caption * duration_per_word, video_clip.duration - start_time)
                
                # Create text clip
                txt_clip = TextClip(
                    caption_text,
                    fontsize=70,
                    color='white',
                    font='Arial-Bold',
                    stroke_color='black',
                    stroke_width=3,
                    method='caption',
                    size=(specs['width'] - 100, None)
                )
                
                txt_clip = txt_clip.set_position(('center', 0.75), relative=True)
                txt_clip = txt_clip.set_start(start_time)
                txt_clip = txt_clip.set_duration(duration)
                
                caption_clips.append(txt_clip)
            
            # Composite captions onto video
            final = CompositeVideoClip([video_clip] + caption_clips)
            
            logger.info("Added captions to video")
            return final
            
        except Exception as e:
            logger.error(f"Failed to add captions: {e}")
            return video_clip
    
    def add_branding(self, video_clip: VideoFileClip, aspect_ratio: str) -> VideoFileClip:
        """Add subtle branding (logo/watermark)"""
        try:
            specs = self._get_video_specs(aspect_ratio)
            
            # Create simple text watermark
            watermark = TextClip(
                "@FashionAI",
                fontsize=24,
                color='white',
                font='Arial',
                stroke_color='black',
                stroke_width=1
            )
            
            watermark = watermark.set_position((0.05, 0.05), relative=True)
            watermark = watermark.set_duration(video_clip.duration)
            watermark = watermark.set_opacity(0.7)
            
            final = CompositeVideoClip([video_clip, watermark])
            
            return final
            
        except Exception as e:
            logger.error(f"Failed to add branding: {e}")
            return video_clip
    
    def _get_video_specs(self, aspect_ratio: str) -> Dict:
        """Get video specifications for aspect ratio"""
        if aspect_ratio == '9:16':
            return config.VIDEO_SPECS['vertical']
        elif aspect_ratio == '1:1':
            return config.VIDEO_SPECS['square']
        else:
            return config.VIDEO_SPECS['horizontal']
