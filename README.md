# 🚀 Viral Fashion Agent - Autonomous Multi-Platform Content Creator

An AI-powered agent that automatically generates and publishes 10 fashion short-form videos daily across **YouTube Shorts, TikTok, Instagram Reels, Twitter, and Facebook Reels**.

**100% Free & Open Source** • **Fully Automated** • **Multi-Platform** • **AI-Generated Content**

---

## 🎯 Features

- ✅ **Trend Detection**: Automatically scrapes fashion trends from Reddit, Twitter, Google Trends, and TikTok
- ✅ **AI Content Generation**: Uses Groq (free LLM API) to write engaging video scripts
- ✅ **Text-to-Speech**: High-quality voiceovers with Microsoft Edge TTS (free)
- ✅ **Stock Media**: Fetches royalty-free videos/images from Pexels & Unsplash
- ✅ **Video Editing**: Automated editing with captions, transitions, and branding
- ✅ **Multi-Platform Upload**: Simultaneously uploads to 5+ platforms
- ✅ **Analytics Tracking**: Monitors views, likes, comments across all platforms
- ✅ **Zero Cost**: Runs entirely on free tiers and open-source tools

---

## 💰 Monetization Opportunities

This agent is designed to maximize revenue across multiple platforms:

| Platform | Monetization Method | Requirements |
|----------|---------------------|--------------|
| **YouTube Shorts** | Shorts Fund + AdSense | 1K subs, 10M views (90 days) |
| **TikTok** | Creator Fund + Shop | 10K followers, 100K views (30 days) |
| **Instagram** | Reels Play Bonus + Affiliate | Invitation only |
| **Twitter/X** | Creator Subscriptions + Ads Revenue | 500 followers, Twitter Blue |
| **Facebook** | In-stream Ads + Stars | 10K followers, 600K mins (60 days) |

**Estimated Potential**: $500-$5,000/month after building audience (3-6 months)

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    DAILY WORKFLOW (6 AM)                     │
└─────────────────────────────────────────────────────────────┘
                              ↓
        ┌──────────────────────────────────────┐
        │   1. TREND DETECTION                 │
        │   • Reddit (fashion subreddits)      │
        │   • Twitter (hashtags)               │
        │   • Google Trends                    │
        │   • TikTok trending                  │
        └──────────────────────────────────────┘
                              ↓
        ┌──────────────────────────────────────┐
        │   2. AI CONTENT GENERATION           │
        │   • Groq LLM (script writing)        │
        │   • Metadata optimization            │
        │   • Platform-specific adaptation     │
        └──────────────────────────────────────┘
                              ↓
        ┌──────────────────────────────────────┐
        │   3. MEDIA CREATION                  │
        │   • Edge-TTS (voiceover)             │
        │   • Pexels/Unsplash (visuals)        │
        │   • MoviePy (video editing)          │
        │   • Auto-captions + branding         │
        └──────────────────────────────────────┘
                              ↓
        ┌──────────────────────────────────────┐
        │   4. MULTI-PLATFORM UPLOAD           │
        │   • YouTube Shorts                   │
        │   • TikTok                           │
        │   • Instagram Reels                  │
        │   • Twitter/X                        │
        │   • Facebook Reels                   │
        └──────────────────────────────────────┘
                              ↓
        ┌──────────────────────────────────────┐
        │   5. ANALYTICS & TRACKING            │
        │   • SQLite database                  │
        │   • Performance metrics              │
        │   • Revenue tracking                 │
        └──────────────────────────────────────┘
```

---

## 📋 Prerequisites

### Required API Keys (All Free Tier)

1. **Groq** (AI): [groq.com](https://groq.com) - 14,400 requests/day
2. **Reddit**: [reddit.com/prefs/apps](https://reddit.com/prefs/apps)
3. **Twitter/X**: [developer.twitter.com](https://developer.twitter.com)
4. **Pexels**: [pexels.com/api](https://pexels.com/api)
5. **Unsplash**: [unsplash.com/developers](https://unsplash.com/developers)

### Platform Credentials

6. **YouTube**: Google Cloud Console (OAuth 2.0)
7. **Instagram**: Username + Password
8. **TikTok**: Session ID or Creative Center API
9. **Facebook**: Page ID + Access Token

---

## 🚀 Quick Start

### Option 1: GitHub Actions (Recommended)

1. **Fork this repository**

2. **Add secrets** to your GitHub repo:
   - Go to Settings → Secrets → Actions
   - Add all API keys from `.env.example`

3. **Enable GitHub Actions**:
   - Go to Actions tab → Enable workflows
   - Workflow runs daily at 6 AM UTC automatically

4. **Manual trigger** (optional):
   - Actions → Daily Fashion Shorts Generator → Run workflow

### Option 2: Local Development

```bash
# Clone repository
git clone https://github.com/yourusername/viral-fashion-agent.git
cd viral-fashion-agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install FFmpeg (required for video editing)
# macOS: brew install ffmpeg
# Ubuntu: sudo apt-get install ffmpeg
# Windows: Download from ffmpeg.org

# Copy environment template
cp .env.example .env

# Edit .env and add your API keys
nano .env  # or use your favorite editor

# Run test workflow
python main.py test

# Or run scheduled agent
python main.py
```

### Option 3: Cloud Deployment

#### **Render.com** (Free)
1. Connect GitHub repo
2. Create new Background Worker
3. Build command: `pip install -r requirements.txt`
4. Start command: `python main.py`
5. Add environment variables

#### **Railway.app** (Free $5/month credit)
1. Import from GitHub
2. Add environment variables
3. Deploy automatically

#### **Oracle Cloud** (Always Free)
1. Create VM instance (1GB RAM)
2. SSH and clone repo
3. Set up systemd service
4. Configure cron job

---

## 📁 Project Structure

```
viral-fashion-agent/
├── .github/
│   └── workflows/
│       └── daily_shorts.yml       # GitHub Actions automation
├── src/
│   ├── uploaders/
│   │   ├── __init__.py           # Multi-platform uploader
│   │   ├── base.py               # Base uploader class
│   │   ├── youtube.py            # YouTube Shorts
│   │   ├── tiktok.py             # TikTok
│   │   ├── instagram.py          # Instagram Reels
│   │   ├── twitter.py            # Twitter/X
│   │   └── facebook.py           # Facebook Reels
│   ├── trend_detector.py         # Trend scraping
│   ├── content_generator.py      # AI script generation
│   ├── media_creator.py          # Video creation
│   └── database.py               # Analytics tracking
├── config.py                     # Configuration
├── main.py                       # Main orchestrator
├── requirements.txt              # Dependencies
├── .env.example                  # Environment template
└── README.md                     # This file
```

---

## ⚙️ Configuration

Edit `config.py` to customize:

- **Daily video count**: `DAILY_VIDEOS_COUNT = 10`
- **Upload timing**: `UPLOAD_STAGGER_MINUTES = 60`
- **Fashion niches**: `FASHION_NICHES = [...]`
- **Platform settings**: Enable/disable specific platforms
- **Video specs**: Resolution, FPS, aspect ratios

---

## 📊 Commands

```bash
# Run test workflow (generates 10 videos once)
python main.py test

# Update analytics from all platforms
python main.py analytics

# Generate performance report
python main.py report

# Run scheduled agent (daily at 6 AM)
python main.py
```

---

## 🎬 Video Creation Process

1. **Trend Detection**: Scrapes 50+ sources, deduplicates, scores by relevance
2. **Script Generation**: AI writes 45-second engaging scripts with hooks and CTAs
3. **Voiceover**: Edge-TTS generates natural-sounding audio (4 voice options)
4. **Visuals**: Downloads 3-5 stock videos/images matching trend keywords
5. **Editing**: Combines clips, adds audio, captions, branding
6. **Export**: 1080x1920 vertical MP4 (optimized for mobile)
7. **Upload**: Parallel uploads to all platforms with custom metadata

**Average time per video**: 3-5 minutes  
**Total daily runtime**: 30-60 minutes

---

## 📈 Analytics Dashboard

The agent tracks:

- **Total views, likes, comments, shares** across all platforms
- **Platform performance** (which platform drives most engagement)
- **Trend effectiveness** (which trends perform best)
- **Upload success rate**
- **Revenue estimates** (based on platform-specific RPM)

View stats anytime:
```bash
python main.py report
```

---

## 🔧 Troubleshooting

### TikTok Upload Issues
TikTok doesn't have an official upload API. Options:
1. **Selenium automation** (implemented, may require manual setup)
2. **TikTok Creative Center API** (requires business account approval)
3. **Manual upload** using mobile app

### Instagram Login Fails
- Use app-specific password if 2FA enabled
- Session may expire every 30 days
- Consider using Instagram Business API (requires Meta verification)

### YouTube Quota Exceeded
- YouTube API has 10,000 units/day quota
- Each upload costs ~1,600 units (~6 uploads/day)
- Request quota increase: [Google Console](https://console.cloud.google.com)

### FFmpeg Not Found
```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt-get install ffmpeg

# Windows
# Download from: https://ffmpeg.org/download.html
```

---

## 🛡️ Legal & Best Practices

### ⚠️ Important Disclaimers

1. **API Terms of Service**: Respect rate limits and TOS of all platforms
2. **Stock Media**: Only use royalty-free content for commercial use
3. **Content Ownership**: AI-generated content may have licensing implications
4. **Spam Prevention**: Don't upload duplicate or low-quality content
5. **Disclosure**: Mark content as AI-generated if required by platform

### Ethical Guidelines

- ✅ Create genuine value for viewers
- ✅ Cite sources when referencing trends
- ✅ Use diverse fashion perspectives
- ✅ Respect copyright and trademarks
- ❌ Don't mislead or spread misinformation
- ❌ Don't spam or use clickbait

---

## 🤝 Contributing

Contributions welcome! Areas for improvement:

- [ ] Better trend scoring algorithm
- [ ] Face/avatar generation for on-screen presence
- [ ] Multi-language support
- [ ] Advanced video effects
- [ ] Revenue optimization strategies
- [ ] Additional platforms (Pinterest, Snapchat)

**Submit PR** or **open an issue** on GitHub!

---

## 📄 License

MIT License - Free to use, modify, and distribute.

---

## 🌟 Success Tips

1. **Consistency is key**: Run daily for 30+ days to build momentum
2. **Optimize titles**: Test different title formats (questions, numbers, hooks)
3. **Engage with comments**: Respond to boost algorithm favor
4. **Cross-promote**: Mention other platforms in videos
5. **Track what works**: Analyze top performers, double down on successful trends
6. **Quality over quantity**: Better to post 5 great videos than 10 mediocre ones
7. **Patience**: Monetization takes 3-6 months of consistent posting

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/viral-fashion-agent/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/viral-fashion-agent/discussions)
- **Updates**: Watch this repo for new features

---

## 🎯 Roadmap

- [x] Multi-platform upload
- [x] Trend detection
- [x] AI content generation
- [x] Analytics tracking
- [ ] Revenue dashboard
- [ ] A/B testing framework
- [ ] Comment auto-responder
- [ ] Affiliate link integration
- [ ] Merchandise promotion
- [ ] Live streaming automation

---

**Built with ❤️ by the open-source community**

⭐ **Star this repo** if you find it useful!

🔔 **Watch** for updates and new features!

🍴 **Fork** to create your own viral agent!

---

*Disclaimer: This tool is for educational purposes. Success depends on content quality, consistency, and platform algorithms. No guarantee of revenue.*
