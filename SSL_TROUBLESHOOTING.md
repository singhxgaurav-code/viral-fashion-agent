# SSL Certificate Issues - Troubleshooting Guide

## Problem
You're seeing errors like:
```
[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate
```

This is a common macOS issue where Python can't verify SSL certificates.

## Solutions (Try in Order)

### Solution 1: Install Python SSL Certificates (Recommended)
```bash
# For Homebrew Python (most common)
brew postinstall python@3.12

# Or install certificates manually
pip install --upgrade certifi
```

### Solution 2: Run macOS Certificate Installer
```bash
# Find your Python installation
ls /Applications/Python\ 3.*/

# Run the Install Certificates command
/Applications/Python\ 3.12/Install\ Certificates.command
```

### Solution 3: Use System Certificates
```bash
# Link Homebrew OpenSSL certificates
export SSL_CERT_FILE=/opt/homebrew/etc/openssl@3/cert.pem
export REQUESTS_CA_BUNDLE=/opt/homebrew/etc/openssl@3/cert.pem

# Add to your shell profile (.zshrc or .bash_profile)
echo 'export SSL_CERT_FILE=/opt/homebrew/etc/openssl@3/cert.pem' >> ~/.zshrc
echo 'export REQUESTS_CA_BUNDLE=/opt/homebrew/etc/openssl@3/cert.pem' >> ~/.zshrc
```

### Solution 4: Reinstall Python with SSL Support
```bash
# Uninstall current Python
brew uninstall python@3.12

# Reinstall with OpenSSL
brew install python@3.12
brew postinstall python@3.12

# Recreate virtual environment
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Solution 5: Corporate Network Workaround
If you're behind a corporate firewall or proxy:

```bash
# Set proxy variables (ask your IT department for values)
export HTTP_PROXY=http://proxy.company.com:8080
export HTTPS_PROXY=http://proxy.company.com:8080
export NO_PROXY=localhost,127.0.0.1

# Or add to .env file:
echo "HTTP_PROXY=http://proxy.company.com:8080" >> .env
echo "HTTPS_PROXY=http://proxy.company.com:8080" >> .env
```

### Solution 6: Temporary SSL Bypass (Testing Only - NOT SECURE!)
**⚠️ WARNING: This disables security checks. Only use for local testing!**

```bash
# Create a temporary test file
cat > test_demo.py << 'EOF'
import ssl
import urllib3

# Disable SSL warnings and verification
urllib3.disable_warnings()
ssl._create_default_https_context = ssl._create_unverified_context

# Now import and run demo
import demo
demo.main()
EOF

# Run it
python test_demo.py
```

## Verification

After applying a fix, test SSL:
```bash
source venv/bin/activate

# Test 1: Check SSL paths
python -c "import ssl; print(ssl.get_default_verify_paths())"

# Test 2: Test HTTPS connection
python -c "import requests; r = requests.get('https://www.google.com'); print('✅ SSL working' if r.status_code == 200 else '❌ SSL failed')"

# Test 3: Test Groq API
python -c "from groq import Groq; import os; client = Groq(api_key=os.getenv('GROQ_API_KEY')); print('✅ Groq API working')"
```

## Common Issues

### Issue: "certificate verify failed"
- **Cause**: Missing or outdated SSL certificates
- **Fix**: Try Solutions 1-3 above

### Issue: "Connection error" from Groq/Pexels
- **Cause**: SSL verification failing or network blocking HTTPS
- **Fix**: Check if you're behind a corporate proxy (Solution 5)

### Issue: "Connection timeout" from Edge-TTS
- **Cause**: WebSocket connection blocked or SSL issue
- **Fix**: Edge-TTS requires working SSL. Try Solutions 1-4

## Alternative: Use Different Services

If SSL issues persist, you can modify the code to use alternative services:

### For Content Generation (instead of Groq):
```python
# Use OpenAI API (also in requirements.txt)
from openai import OpenAI
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
```

### For TTS (instead of Edge-TTS):
```python
# Use gTTS (Google TTS - simpler, no SSL issues)
from gtts import gTTS
tts = gTTS('Your text here', lang='en')
tts.save('output.mp3')
```

### For Trends (instead of online APIs):
```python
# Use local trend list
SAMPLE_TRENDS = [
    {'title': 'Oversized Blazers 2024', 'keywords': ['blazer', 'fashion']},
    {'title': 'Vintage Denim Trends', 'keywords': ['denim', 'vintage']},
    # Add more...
]
```

## If All Else Fails

Create a simplified version that works offline:

```bash
# Run the offline demo
python << 'EOF'
from src.content_generator import ContentGenerator
from src.media_creator import MediaCreator

# Use sample trend
trend = {
    'title': 'Fall Fashion 2024',
    'keywords': ['fall', 'fashion', 'trends']
}

# Generate script (if Groq works)
try:
    gen = ContentGenerator()
    script = gen.generate_script(trend)
    print(f"Generated: {script[:100]}")
except:
    print("Using fallback script")
    script = "Fall fashion is all about layering..."

# Create video (if media APIs work)
try:
    creator = MediaCreator()
    metadata = {'title': 'Fall Fashion', 'keywords': ['fall']}
    creator.create_video(script, metadata, 'output/test.mp4')
except Exception as e:
    print(f"Video creation failed: {e}")
EOF
```

## Get Help

1. Check if you're on a corporate network that blocks HTTPS
2. Verify your internet connection is working
3. Try from a different network (e.g., home WiFi vs work network)
4. Contact your IT department if on corporate network

## Success Indicators

When SSL is working properly, you should see:
- ✅ No SSL warnings in logs
- ✅ Groq API connects successfully
- ✅ Pexels/Unsplash download stock media
- ✅ Edge-TTS generates audio
- ✅ Video files created in `output/videos/`
