#!/bin/bash

# Viral Fashion Agent - Quick Demo Runner
# This script helps you run your first video generation

set -e  # Exit on error

echo "🎬 Viral Fashion Agent - Quick Setup"
echo "======================================"
echo ""

# Step 1: Check FFmpeg
echo "📦 Step 1: Checking FFmpeg..."
if command -v ffmpeg &> /dev/null; then
    echo "✅ FFmpeg is installed: $(ffmpeg -version | head -1)"
else
    echo "❌ FFmpeg not found. Installing..."
    brew install ffmpeg
    echo "✅ FFmpeg installed successfully!"
fi
echo ""

# Step 2: Activate virtual environment
echo "🐍 Step 2: Activating Python environment..."
if [ -d "venv" ]; then
    source venv/bin/activate
    
    # Set SSL certificate environment variables
    export SSL_CERT_FILE=$(python -m certifi)
    export REQUESTS_CA_BUNDLE=$(python -m certifi)
    
    echo "✅ Virtual environment activated"
    echo "   Python: $(python --version)"
    echo "   Packages: $(pip list | wc -l | tr -d ' ') installed"
    echo "   SSL Certs: $SSL_CERT_FILE"
else
    echo "❌ Virtual environment not found!"
    echo "   Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    echo "✅ Environment created and dependencies installed"
fi
echo ""

# Step 3: Check .env file
echo "🔑 Step 3: Checking environment configuration..."
if [ -f ".env" ]; then
    echo "✅ .env file exists"
    
    # Check for required keys
    MISSING_KEYS=()
    if ! grep -q "GROQ_API_KEY=" .env || grep -q "GROQ_API_KEY=your_" .env; then
        MISSING_KEYS+=("GROQ_API_KEY")
    fi
    if ! grep -q "PEXELS_API_KEY=" .env || grep -q "PEXELS_API_KEY=your_" .env; then
        MISSING_KEYS+=("PEXELS_API_KEY")
    fi
    if ! grep -q "UNSPLASH_ACCESS_KEY=" .env || grep -q "UNSPLASH_ACCESS_KEY=your_" .env; then
        MISSING_KEYS+=("UNSPLASH_ACCESS_KEY")
    fi
    
    if [ ${#MISSING_KEYS[@]} -eq 0 ]; then
        echo "✅ All required API keys configured"
    else
        echo "⚠️  Missing API keys: ${MISSING_KEYS[*]}"
        echo ""
        echo "Please add these keys to your .env file:"
        echo ""
        for key in "${MISSING_KEYS[@]}"; do
            case $key in
                GROQ_API_KEY)
                    echo "  - GROQ_API_KEY: Get from https://console.groq.com/"
                    ;;
                PEXELS_API_KEY)
                    echo "  - PEXELS_API_KEY: Get from https://www.pexels.com/api/"
                    ;;
                UNSPLASH_ACCESS_KEY)
                    echo "  - UNSPLASH_ACCESS_KEY: Get from https://unsplash.com/developers"
                    ;;
            esac
        done
        echo ""
        echo "Edit .env file: nano .env"
        echo "Then run this script again."
        exit 1
    fi
else
    echo "❌ .env file not found!"
    echo "   Creating .env from template..."
    cp .env.demo .env
    echo "✅ .env created from template"
    echo ""
    echo "⚠️  Please edit .env and add your API keys:"
    echo "   1. GROQ_API_KEY (https://console.groq.com/)"
    echo "   2. PEXELS_API_KEY (https://www.pexels.com/api/)"
    echo "   3. UNSPLASH_ACCESS_KEY (https://unsplash.com/developers)"
    echo ""
    echo "   Edit file: nano .env"
    echo "   Then run: ./run_demo.sh"
    exit 1
fi
echo ""

# Step 4: Create output directories
echo "📁 Step 4: Creating output directories..."
mkdir -p output/videos
mkdir -p data
echo "✅ Directories ready"
echo ""

# Step 5: Run demo
echo "🎥 Step 5: Running demo..."
echo "   This will generate 1 video (no platform uploads)"
echo "   Time: ~2-3 minutes"
echo ""
read -p "Press Enter to start video generation..."
echo ""

python demo.py

echo ""
echo "======================================"
echo "✅ Demo Complete!"
echo ""
echo "📹 Your video(s) are in: output/videos/"
echo ""
echo "🎉 Next steps:"
echo "   1. View your video: open output/videos/*.mp4"
echo "   2. Configure platform credentials in .env"
echo "   3. Run full test: python main.py test"
echo "   4. See QUICKSTART.md for more options"
echo ""
