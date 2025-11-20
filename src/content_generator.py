"""
AI-powered content generation using multiple providers (Groq, HuggingFace, local models)
"""
from typing import Dict, List, Optional
import logging
import random
import requests
import json

import config

logger = logging.getLogger(__name__)


class ContentGenerator:
    """Generate video scripts and metadata using AI with automatic fallback"""
    
    def __init__(self):
        self.providers = []
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize available AI providers in order of preference"""
        
        # Provider 1: Groq (fastest, best quality)
        if hasattr(config, 'GROQ_API_KEY') and config.GROQ_API_KEY and config.GROQ_API_KEY != 'your_groq_api_key_here':
            try:
                from groq import Groq
                self.providers.append({
                    'name': 'Groq',
                    'client': Groq(api_key=config.GROQ_API_KEY),
                    'model': 'llama-3.1-70b-versatile',
                    'type': 'groq'
                })
                logger.info("✅ Groq provider initialized")
            except Exception as e:
                logger.warning(f"Groq initialization failed: {e}")
        
        # Provider 2: OpenAI (reliable, $5 free credits for new users)
        if hasattr(config, 'OPENAI_API_KEY') and config.OPENAI_API_KEY and config.OPENAI_API_KEY != 'your_openai_api_key_here':
            try:
                from openai import OpenAI
                self.providers.append({
                    'name': 'OpenAI',
                    'client': OpenAI(api_key=config.OPENAI_API_KEY),
                    'model': 'gpt-3.5-turbo',  # Cheapest option
                    'type': 'openai'
                })
                logger.info("✅ OpenAI provider initialized")
            except Exception as e:
                logger.warning(f"OpenAI initialization failed: {e}")
        
        # Provider 3: HuggingFace Inference API (free, but may be blocked by corporate proxies)
        self.providers.append({
            'name': 'HuggingFace',
            'api_url': 'https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2',
            'type': 'huggingface',
            'headers': {}
        })
        logger.info("✅ HuggingFace provider initialized (free tier)")
        
        # Provider 4: Ollama (local, requires installation)
        if hasattr(config, 'OLLAMA_ENABLED') and config.OLLAMA_ENABLED:
            self.providers.append({
                'name': 'Ollama',
                'api_url': f"{config.OLLAMA_BASE_URL}/api/generate",
                'model': 'llama2',
                'type': 'ollama'
            })
            logger.info("✅ Ollama provider initialized (local)")
        
        if not self.providers:
            logger.warning("⚠️  No AI providers available, will use fallback templates")
        else:
            logger.info(f"📊 {len(self.providers)} AI provider(s) available")
    
    def _call_ai(self, prompt: str, max_tokens: int = 300, temperature: float = 0.8) -> Optional[str]:
        """
        Call AI providers in order until one succeeds
        
        Args:
            prompt: The prompt to send
            max_tokens: Maximum tokens to generate
            temperature: Creativity level (0-1)
            
        Returns:
            Generated text or None if all providers fail
        """
        for provider in self.providers:
            try:
                logger.info(f"Trying {provider['name']}...")
                
                if provider['type'] == 'groq':
                    response = provider['client'].chat.completions.create(
                        messages=[{"role": "user", "content": prompt}],
                        model=provider['model'],
                        temperature=temperature,
                        max_tokens=max_tokens
                    )
                    result = response.choices[0].message.content.strip()
                    logger.info(f"✅ {provider['name']} succeeded")
                    return result
                
                elif provider['type'] == 'openai':
                    response = provider['client'].chat.completions.create(
                        messages=[{"role": "user", "content": prompt}],
                        model=provider['model'],
                        temperature=temperature,
                        max_tokens=max_tokens
                    )
                    result = response.choices[0].message.content.strip()
                    logger.info(f"✅ {provider['name']} succeeded")
                    return result
                
                elif provider['type'] == 'huggingface':
                    # HuggingFace Inference API
                    payload = {
                        "inputs": prompt,
                        "parameters": {
                            "max_new_tokens": max_tokens,
                            "temperature": temperature,
                            "return_full_text": False
                        }
                    }
                    response = requests.post(
                        provider['api_url'],
                        headers=provider['headers'],
                        json=payload,
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        if isinstance(result, list) and len(result) > 0:
                            text = result[0].get('generated_text', '')
                            if text:
                                logger.info(f"✅ {provider['name']} succeeded")
                                return text.strip()
                    
                    # Handle rate limiting or model loading
                    if response.status_code == 503:
                        logger.warning(f"{provider['name']}: Model loading, trying next provider...")
                        continue
                    
                    logger.warning(f"{provider['name']} failed: {response.status_code}")
                
                elif provider['type'] == 'ollama':
                    # Ollama local API
                    payload = {
                        "model": provider['model'],
                        "prompt": prompt,
                        "stream": False
                    }
                    response = requests.post(
                        provider['api_url'],
                        json=payload,
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        result = response.json().get('response', '')
                        if result:
                            logger.info(f"✅ {provider['name']} succeeded")
                            return result.strip()
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"{provider['name']} network error: {e}")
                continue
            except Exception as e:
                logger.warning(f"{provider['name']} failed: {e}")
                continue
        
        logger.error("❌ All AI providers failed")
        return None
    
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

        # Try AI providers
        script = self._call_ai(prompt, max_tokens=300, temperature=0.8)
        
        if script:
            logger.info(f"Generated script: {script[:50]}...")
            return script
        else:
            logger.warning("Using fallback script template")
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

        # Try AI providers
        result = self._call_ai(prompt, max_tokens=400, temperature=0.7)
        
        if result:
            try:
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
                logger.error(f"Metadata parsing failed: {e}")
                return self._fallback_metadata(script, trend)
        else:
            # All AI providers failed
            logger.warning("All AI providers failed for metadata generation, using fallback")
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
