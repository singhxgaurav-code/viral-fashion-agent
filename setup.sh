#!/bin/bash

# Setup script for Viral Fashion Agent

echo "🚀 Viral Fashion Agent - Setup Script"
echo "======================================"
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version || { echo "❌ Python 3.11+ required"; exit 1; }

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Check FFmpeg
echo "Checking for FFmpeg..."
if command -v ffmpeg &> /dev/null; then
    echo "✅ FFmpeg found: $(ffmpeg -version | head -n1)"
else
    echo "❌ FFmpeg not found!"
    echo "Please install FFmpeg:"
    echo "  macOS: brew install ffmpeg"
    echo "  Ubuntu: sudo apt-get install ffmpeg"
    echo "  Windows: Download from https://ffmpeg.org"
fi

# Create directories
echo "Creating directories..."
mkdir -p output/videos
mkdir -p data
mkdir -p logs

# Copy environment template
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo "⚠️  Please edit .env and add your API keys!"
else
    echo "✅ .env file already exists"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env and add your API keys"
echo "2. Run: python main.py test"
echo ""
echo "For help, see README.md"
