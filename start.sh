#!/bin/bash

# SynthGen Quick Start Script
# This script helps you get SynthGen up and running quickly

echo "════════════════════════════════════════════════════════════"
echo "  SynthGen v4.1 - Quick Start"
echo "════════════════════════════════════════════════════════════"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed!"
    echo "   Please install Python 3.8 or higher and try again."
    exit 1
fi

echo "✅ Python found: $(python3 --version)"
echo ""

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip is not installed!"
    echo "   Please install pip and try again."
    exit 1
fi

echo "✅ pip found: $(pip3 --version)"
echo ""

# Check if requirements.txt exists
if [ ! -f "requirements.txt" ]; then
    echo "❌ requirements.txt not found!"
    echo "   Make sure you're in the SynthGen project directory."
    exit 1
fi

echo "📦 Checking dependencies..."
echo ""

# Check if dependencies are installed
MISSING=0
while IFS= read -r package; do
    # Extract package name (before >= or ==)
    pkg_name=$(echo "$package" | sed 's/[>=].*//')
    if ! pip3 show "$pkg_name" &> /dev/null; then
        MISSING=1
        break
    fi
done < requirements.txt

if [ $MISSING -eq 1 ]; then
    echo "⚠️  Some dependencies are missing."
    echo ""
    read -p "Install dependencies now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo ""
        echo "📦 Installing dependencies..."
        pip3 install -r requirements.txt
        
        if [ $? -eq 0 ]; then
            echo ""
            echo "✅ Dependencies installed successfully!"
        else
            echo ""
            echo "❌ Failed to install dependencies."
            echo "   Try running manually: pip3 install -r requirements.txt"
            exit 1
        fi
    else
        echo ""
        echo "⚠️  Cannot start without dependencies."
        echo "   Run: pip3 install -r requirements.txt"
        exit 1
    fi
else
    echo "✅ All dependencies are installed!"
fi

echo ""
echo "════════════════════════════════════════════════════════════"
echo "  Starting SynthGen Backend..."
echo "════════════════════════════════════════════════════════════"
echo ""
echo "The backend will start on http://localhost:5000"
echo ""
echo "To use SynthGen:"
echo "  1. Keep this terminal window open"
echo "  2. Open your browser"
echo "  3. Go to: http://localhost:5000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""
echo "════════════════════════════════════════════════════════════"
echo ""

# Start the backend
python3 backend.py
