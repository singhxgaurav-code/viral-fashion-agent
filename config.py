"""
Configuration settings for the Viral Fashion Agent
"""
import os
from dotenv import load_dotenv

load_dotenv()

# AI Configuration
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
HUGGINGFACE_API_KEY = os.getenv('HUGGINGFACE_API_KEY')  # Optional for HuggingFace free tier
OLLAMA_ENABLED = os.getenv('OLLAMA_ENABLED', 'False').lower() == 'true'  # Local Ollama instance
OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')  # Ollama API endpoint

# Trend Detection
REDDIT_CLIENT_ID = os.getenv('REDDIT_CLIENT_ID')
REDDIT_CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET')
REDDIT_USER_AGENT = os.getenv('REDDIT_USER_AGENT', 'fashion_agent_v1.0')

TWITTER_BEARER_TOKEN = os.getenv('TWITTER_BEARER_TOKEN')
TWITTER_API_KEY = os.getenv('TWITTER_API_KEY')
TWITTER_API_SECRET = os.getenv('TWITTER_API_SECRET')

# Media APIs
PEXELS_API_KEY = os.getenv('PEXELS_API_KEY')
UNSPLASH_ACCESS_KEY = os.getenv('UNSPLASH_ACCESS_KEY')
PIXABAY_API_KEY = os.getenv('PIXABAY_API_KEY')

# Platform Upload Credentials
YOUTUBE_CLIENT_SECRETS = os.getenv('YOUTUBE_CLIENT_SECRETS_FILE', 'client_secrets.json')
TIKTOK_SESSION_ID = os.getenv('TIKTOK_SESSION_ID')
INSTAGRAM_USERNAME = os.getenv('INSTAGRAM_USERNAME')
INSTAGRAM_PASSWORD = os.getenv('INSTAGRAM_PASSWORD')
FACEBOOK_PAGE_ID = os.getenv('FACEBOOK_PAGE_ID')
FACEBOOK_ACCESS_TOKEN = os.getenv('FACEBOOK_ACCESS_TOKEN')

# Agent Settings
DAILY_VIDEOS_COUNT = int(os.getenv('DAILY_VIDEOS_COUNT', 10))
UPLOAD_STAGGER_MINUTES = int(os.getenv('UPLOAD_STAGGER_MINUTES', 60))
OUTPUT_DIR = os.getenv('OUTPUT_DIR', 'output/videos')
DATABASE_PATH = os.getenv('DATABASE_PATH', 'data/agent.db')
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

# Platform-specific settings
PLATFORMS = {
    'youtube': {
        'enabled': True,
        'aspect_ratio': '9:16',  # Vertical (Shorts)
        'max_duration': 60,
        'max_file_size_mb': 256,
        'monetization': 'AdSense + Shorts Fund'
    },
    'tiktok': {
        'enabled': True,
        'aspect_ratio': '9:16',
        'max_duration': 60,
        'max_file_size_mb': 287,
        'monetization': 'Creator Fund + TikTok Shop'
    },
    'instagram': {
        'enabled': True,
        'aspect_ratio': '9:16',  # Reels
        'max_duration': 90,
        'max_file_size_mb': 100,
        'monetization': 'Reels Play Bonus + Affiliate'
    },
    'twitter': {
        'enabled': True,
        'aspect_ratio': '16:9',  # Or 1:1
        'max_duration': 140,
        'max_file_size_mb': 512,
        'monetization': 'Creator Subscriptions + Ads Revenue'
    },
    'facebook': {
        'enabled': True,
        'aspect_ratio': '9:16',  # Reels
        'max_duration': 60,
        'max_file_size_mb': 100,
        'monetization': 'In-stream Ads + Stars'
    }
}

# Fashion niches and categories
FASHION_NICHES = [
    'streetwear',
    'high fashion',
    'sustainable fashion',
    'vintage style',
    'minimalist fashion',
    'luxury brands',
    'affordable fashion',
    'athleisure',
    'korean fashion',
    'japanese fashion',
    'y2k fashion',
    'cottagecore',
    'dark academia'
]

# Subreddits to monitor
REDDIT_SUBREDDITS = [
    'fashion',
    'streetwear',
    'malefashion',
    'femalefashion',
    'streetwearstartup',
    'sneakers',
    'fashionreps',
    'DesignerReps',
    'frugalmalefashion',
    'frugalfemalefashion'
]

# Twitter hashtags to monitor
TWITTER_HASHTAGS = [
    '#fashion',
    '#ootd',
    '#streetwear',
    '#fashiontrends',
    '#style',
    '#fashionblogger',
    '#outfitoftheday',
    '#fashionista',
    '#styleinspo'
]

# Content templates for different platforms
CONTENT_TEMPLATES = {
    'hook_types': [
        "Did you know...",
        "This is trending right now:",
        "Everyone's wearing this:",
        "The fashion industry doesn't want you to know:",
        "3 seconds to learn this trend:",
        "POV: You're about to look expensive:",
        "Stop wearing this, wear this instead:",
    ],
    'cta_types': [
        "Follow for daily fashion tips!",
        "Save this for later!",
        "Tag someone who needs this!",
        "Which outfit would you wear? Comment below!",
        "Double tap if you agree!",
    ]
}

# Video specifications
VIDEO_SPECS = {
    'vertical': {
        'width': 1080,
        'height': 1920,
        'fps': 30
    },
    'square': {
        'width': 1080,
        'height': 1080,
        'fps': 30
    },
    'horizontal': {
        'width': 1920,
        'height': 1080,
        'fps': 30
    }
}
