# API Key Setup Guide

This guide will help you obtain all the required API keys for the Viral Fashion Agent.

## 📝 Quick Setup Checklist

- [ ] Groq API Key
- [ ] Reddit API Credentials
- [ ] Twitter/X API Credentials
- [ ] Pexels API Key
- [ ] Unsplash API Key
- [ ] YouTube OAuth Credentials
- [ ] Instagram Credentials
- [ ] Facebook Page Token
- [ ] TikTok Session (optional)

---

## 1. Groq API (AI Content Generation)

**Free Tier**: 14,400 requests/day

1. Visit [https://console.groq.com](https://console.groq.com)
2. Sign up with Google/GitHub
3. Go to API Keys section
4. Click "Create API Key"
5. Copy key to `.env` as `GROQ_API_KEY`

---

## 2. Reddit API (Trend Detection)

**Free Tier**: 100 requests/minute

1. Visit [https://www.reddit.com/prefs/apps](https://www.reddit.com/prefs/apps)
2. Scroll to bottom, click "create another app..."
3. Fill in:
   - Name: `Fashion Trend Agent`
   - Type: `script`
   - Redirect URI: `http://localhost:8080`
4. Click "create app"
5. Copy:
   - `client_id` (under app name)
   - `client_secret` (labeled "secret")

---

## 3. Twitter/X API (Trend Detection & Upload)

**Free Tier**: 1,500 tweets/month (Basic), or use Free tier with limits

### For Trend Detection (Read-only):
1. Visit [https://developer.twitter.com/en/portal/dashboard](https://developer.twitter.com/en/portal/dashboard)
2. Create a new Project + App
3. Go to Keys and Tokens
4. Generate Bearer Token
5. Copy to `.env` as `TWITTER_BEARER_TOKEN`

### For Posting Videos:
1. Same app, generate:
   - API Key (`TWITTER_CONSUMER_KEY`)
   - API Secret (`TWITTER_CONSUMER_SECRET`)
   - Access Token (`TWITTER_ACCESS_TOKEN_POST`)
   - Access Secret (`TWITTER_ACCESS_SECRET_POST`)

---

## 4. Pexels API (Stock Videos)

**Free Tier**: 200 requests/hour

1. Visit [https://www.pexels.com/api/](https://www.pexels.com/api/)
2. Click "Get Started"
3. Fill in your details
4. Verify email
5. Copy API key to `.env` as `PEXELS_API_KEY`

---

## 5. Unsplash API (Stock Images)

**Free Tier**: 50 requests/hour

1. Visit [https://unsplash.com/developers](https://unsplash.com/developers)
2. Register as a developer
3. Create a new Application
4. Copy Access Key to `.env` as `UNSPLASH_ACCESS_KEY`

---

## 6. YouTube Data API (Upload Shorts)

**Free Tier**: 10,000 quota units/day (~6 uploads)

### Step 1: Enable API
1. Visit [Google Cloud Console](https://console.cloud.google.com)
2. Create new project: "Fashion Agent"
3. Enable "YouTube Data API v3"

### Step 2: OAuth Credentials
1. Go to Credentials → Create Credentials → OAuth 2.0 Client ID
2. Configure consent screen:
   - User Type: External
   - App name: "Fashion Agent"
   - Add scope: `https://www.googleapis.com/auth/youtube.upload`
3. Create OAuth Client ID:
   - Application type: Desktop app
4. Download JSON file
5. Save as `client_secrets.json` in project root

### Step 3: First Run
```bash
python -c "from src.uploaders.youtube import YouTubeUploader; u = YouTubeUploader(); u.authenticate()"
```
This will open browser for OAuth flow (one-time only).

---

## 7. Instagram Credentials (Upload Reels)

**Method 1: Username/Password** (Simple)
1. Add to `.env`:
   ```
   INSTAGRAM_USERNAME=your_username
   INSTAGRAM_PASSWORD=your_password
   ```
2. If 2FA enabled, use app-specific password

**Method 2: Instagram Graph API** (Better for businesses)
1. Convert to Business account
2. Connect to Facebook Page
3. Get Access Token from [Meta Developers](https://developers.facebook.com)

---

## 8. Facebook Page Access Token (Upload Reels)

**Free Tier**: Unlimited (with page)

1. Visit [Meta for Developers](https://developers.facebook.com)
2. Create an App → Type: Business
3. Add product: "Facebook Login"
4. Go to Tools → Graph API Explorer
5. Select your Page
6. Add permissions: `pages_manage_posts`, `pages_read_engagement`
7. Generate Access Token
8. **Make it long-lived**:
   ```bash
   curl -i -X GET "https://graph.facebook.com/v18.0/oauth/access_token?grant_type=fb_exchange_token&client_id=YOUR_APP_ID&client_secret=YOUR_APP_SECRET&fb_exchange_token=SHORT_LIVED_TOKEN"
   ```
9. Copy long-lived token to `.env` as `FACEBOOK_ACCESS_TOKEN`
10. Get Page ID from Page Settings → About

---

## 9. TikTok (Upload Videos)

⚠️ **TikTok has no official public upload API yet**

### Option 1: Selenium Automation (Implemented)
1. Get session ID from browser:
   - Login to TikTok on desktop
   - Open DevTools → Application → Cookies
   - Copy `sessionid` cookie value
   - Add to `.env` as `TIKTOK_SESSION_ID`

### Option 2: TikTok Content Posting API (Requires approval)
1. Apply at [TikTok for Developers](https://developers.tiktok.com)
2. Request Content Posting API access
3. Wait for approval (can take weeks)

### Option 3: Manual Upload (Fallback)
- Videos saved to `output/videos/`
- Upload manually via TikTok mobile app
- Use TikTok Creator Tools for scheduling

---

## 🔒 Security Best Practices

1. **Never commit `.env` to Git** (already in `.gitignore`)
2. **Use GitHub Secrets** for CI/CD
3. **Rotate keys periodically**
4. **Use read-only tokens** where possible
5. **Enable 2FA** on all accounts

---

## 🧪 Testing Your Setup

Test each API individually:

```bash
# Test Groq
python -c "from groq import Groq; print(Groq(api_key='YOUR_KEY').chat.completions.create(messages=[{'role':'user','content':'hi'}], model='llama-3.1-8b-instant').choices[0].message.content)"

# Test Reddit
python -c "import praw; r = praw.Reddit(client_id='ID', client_secret='SECRET', user_agent='test'); print(list(r.subreddit('fashion').hot(limit=1))[0].title)"

# Test Pexels
python -c "import requests; print(requests.get('https://api.pexels.com/v1/search?query=fashion&per_page=1', headers={'Authorization':'YOUR_KEY'}).json())"

# Test full workflow
python main.py test
```

---

## 📞 Support

If you encounter issues:
1. Check API status pages
2. Verify rate limits
3. Review error logs in `agent.log`
4. Open GitHub issue with redacted logs

---

## 💰 Cost Breakdown (Free Tier Limits)

| Service | Free Limit | Upgrade Cost |
|---------|------------|--------------|
| Groq | 14,400 req/day | $0.10/1M tokens |
| Reddit | 100 req/min | $0 (unlimited) |
| Twitter | 1,500 tweets/mo | $100/mo (Basic) |
| Pexels | 200 req/hr | Unlimited free |
| Unsplash | 50 req/hr | $25/mo (5K req/hr) |
| YouTube | 10K quota/day | $0 (can request more) |
| Instagram | Unlimited | $0 |
| Facebook | Unlimited | $0 |

**Total Monthly Cost**: $0 (if within limits)  
**Recommended**: Start free, upgrade Twitter if needed

---

Done! You should now have all API keys configured. 🎉
