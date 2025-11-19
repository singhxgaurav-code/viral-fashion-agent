"""
AI-powered content generation using Groq
"""
from typing import Dict, List
import logging
from groq import Groq
import random

import config

logger = logging.getLogger(__name__)


class ContentGenerator:
    """Generate video scripts and metadata using AI"""
    
    def __init__(self):
        self.client = Groq(api_key=config.GROQ_API_KEY)
        self.model = "llama-3.1-70b-versatile"  # Fast and high quality
    
    def generate_script(self, trend: Dict, duration: int = 45) -> str:
        """
        Generate a short-form video script
        
        Args:
            trend: Trend dict with title, description, keywords
            duration: Target duration in seconds
        
        Returns:
            Script text optimized for voiceover
        """
        hook_type = random.choice(config.CONTENT_TEMPLATES['hook_types'])
        cta_type = random.choice(config.CONTENT_TEMPLATES['cta_types'])
        
        prompt = f"""Create a {duration}-second YouTube Shorts/TikTok/Reels script about this fashion trend:

Trend: {trend['title']}
Context: {trend.get('description', '')}
Keywords: {', '.join(trend.get('keywords', []))}

Requirements:
1. Start with this hook style: "{hook_type}"
2. Write for voiceover (natural, conversational tone)
3. Keep it {duration} seconds when spoken (approximately {duration * 2.5} words)
4. Make it educational yet entertaining
5. Include 3 specific styling tips or facts
6. End with: "{cta_type}"
7. Use simple language, short sentences
8. Make it shareable and valuable

Output only the script text, no extra formatting or labels."""

        try:
            response = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=self.model,
                temperature=0.8,
                max_tokens=300
            )
            
            script = response.choices[0].message.content.strip()
            logger.info(f"Generated script: {script[:50]}...")
            return script
            
        except Exception as e:
            logger.error(f"Script generation failed: {e}")
            return self._fallback_script(trend)
    
    def generate_metadata(self, script: str, trend: Dict) -> Dict:
        """
        Generate platform-optimized metadata
        
        Returns:
            Dict with title, description, tags, hashtags
        """
        prompt = f"""Based on this short-form video script, generate metadata:

Script: {script}

Original trend: {trend['title']}

Generate:
1. A catchy title (max 60 characters, clickable, uses numbers or questions)
2. A description (max 200 characters, includes value prop)
3. 10 relevant hashtags (mix of popular and niche)
4. 5 search keywords

Format as JSON:
{{
    "title": "...",
    "description": "...",
    "hashtags": ["tag1", "tag2", ...],
    "keywords": ["keyword1", ...]
}}"""

        try:
            response = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=self.model,
                temperature=0.7,
                max_tokens=400
            )
            
            import json
            result = response.choices[0].message.content.strip()
            
            # Extract JSON from response
            if '```json' in result:
                result = result.split('```json')[1].split('```')[0]
            elif '```' in result:
                result = result.split('```')[1].split('```')[0]
            
            metadata = json.loads(result)
            
            # Add tags for all platforms
            tags = metadata.get('hashtags', [])
            metadata['tags'] = [tag.replace('#', '') for tag in tags]
            
            logger.info(f"Generated metadata: {metadata['title']}")
            return metadata
            
        except Exception as e:
            logger.error(f"Metadata generation failed: {e}")
            return self._fallback_metadata(script, trend)
    
    def generate_batch_content(self, trends: List[Dict], videos_per_trend: int = 1) -> List[Dict]:
        """
        Generate multiple video scripts from trends
        
        Returns:
            List of dicts with script, metadata, trend_info
        """
        content_batch = []
        
        for trend in trends:
            for _ in range(videos_per_trend):
                try:
                    script = self.generate_script(trend)
                    metadata = self.generate_metadata(script, trend)
                    
                    content_batch.append({
                        'script': script,
                        'metadata': metadata,
                        'trend': trend,
                        'status': 'ready'
                    })
                    
                except Exception as e:
                    logger.error(f"Failed to generate content for trend: {e}")
                    continue
        
        logger.info(f"Generated {len(content_batch)} pieces of content")
        return content_batch
    
    def optimize_for_platform(self, metadata: Dict, platform: str) -> Dict:
        """Optimize metadata for specific platform"""
        optimized = metadata.copy()
        
        if platform == 'youtube':
            # YouTube Shorts optimization
            optimized['title'] = f"{metadata['title']} #Shorts"
            optimized['description'] = f"{metadata['description']}\n\n#Shorts #Fashion"
            
        elif platform == 'tiktok':
            # TikTok prefers shorter captions
            desc = metadata['description']
            if len(desc) > 100:
                desc = desc[:97] + "..."
            
            hashtags = ' '.join([f'#{tag}' for tag in metadata['tags'][:5]])
            optimized['description'] = f"{desc}\n\n{hashtags}"
            
        elif platform == 'instagram':
            # Instagram loves hashtags
            hashtags = ' '.join([f'#{tag}' for tag in metadata['tags'][:30]])
            optimized['description'] = f"{metadata['description']}\n\n{hashtags}"
            
        elif platform == 'twitter':
            # Twitter character limit
            desc = metadata['description'][:200]
            hashtags = ' '.join([f'#{tag}' for tag in metadata['tags'][:3]])
            optimized['description'] = f"{desc} {hashtags}"
            
        return optimized
    
    def _fallback_script(self, trend: Dict) -> str:
        """Generate simple fallback script if AI fails"""
        return f"""Did you know this is trending right now?

{trend['title']}

Here's what makes it special:
• Unique style
• Easy to wear
• Perfect for any occasion

Try this trend and stand out!

Follow for daily fashion tips!"""
    
    def _fallback_metadata(self, script: str, trend: Dict) -> Dict:
        """Generate simple fallback metadata"""
        title = trend['title'][:60]
        
        return {
            'title': title,
            'description': script[:200],
            'tags': trend.get('keywords', ['fashion', 'style', 'trend']),
            'hashtags': ['#fashion', '#style', '#trending', '#ootd', '#fashiontips']
        }
    
    def generate_viral_hook(self, trend: Dict) -> str:
        """Generate a highly engaging hook for the video"""
        hooks = [
            f"This {trend['title']} trend is going viral...",
            f"POV: You just discovered {trend['title']}",
            f"Everyone's talking about {trend['title']}",
            f"The fashion industry doesn't want you to know about {trend['title']}",
            f"3 seconds to learn {trend['title']}",
            f"Stop scrolling! This is about {trend['title']}",
        ]
        
        return random.choice(hooks)
