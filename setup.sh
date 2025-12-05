#!/bin/bash

echo "========================================"
echo "Fineract Transaction Tool Setup"
echo "========================================"
echo ""

# Check Python
echo "[1/4] Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed!"
    echo "Please install Python 3.8 or higher"
    exit 1
fi
python3 --version
echo ""

# Install dependencies
echo "[2/4] Installing Python dependencies..."
pip3 install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    exit 1
fi
echo ""

# Create .env
echo "[3/4] Setting up configuration..."
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.template .env
    echo ""
    echo "IMPORTANT: Please edit .env file with your Fineract server details!"
    echo ""
else
    echo ".env file already exists - skipping"
    echo ""
fi

# Create desktop folder
echo "[4/4] Creating data folders..."
mkdir -p ../desktop
echo ""

echo "========================================"
echo "Setup Complete!"
echo "========================================"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your Fineract credentials"
echo "2. Run: python3 main.py"
echo "3. Open browser: http://localhost:8000"
echo ""
