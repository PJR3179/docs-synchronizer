#!/bin/bash
# WSL Setup Guide for MD2Conf API

echo "=== Setting up MD2Conf API in WSL ==="

# Check if we're in WSL
if grep -qi microsoft /proc/version; then
    echo "✓ Running in WSL environment"
else
    echo "❌ Not running in WSL. Please run this script from WSL terminal."
    exit 1
fi

# Update system packages
echo "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install required packages
echo "Installing Python, Node.js, and dependencies..."
sudo apt install -y python3 python3-pip python3-venv nodejs npm curl git

# Install Node.js LTS (latest)
echo "Installing Node.js LTS..."
curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
sudo apt install -y nodejs

# Install mermaid-cli globally
echo "Installing mermaid-cli..."
sudo npm install -g @mermaid-js/mermaid-cli

# Create project directory in WSL home
echo "Setting up project directory..."
PROJECT_DIR="$HOME/prodeng-md-to-confluence-2"
mkdir -p "$PROJECT_DIR"

echo "Project directory created at: $PROJECT_DIR"
echo ""
echo "Next steps:"
echo "1. Copy your project files from Windows to WSL:"
echo "   cp -r /mnt/c/Users/Philip.Rubbo/prodeng-md-to-confluence-2/* $PROJECT_DIR/"
echo ""
echo "2. Navigate to project directory:"
echo "   cd $PROJECT_DIR"
echo ""
echo "3. Create virtual environment:"
echo "   python3 -m venv venv"
echo "   source venv/bin/activate"
echo ""
echo "4. Install Python dependencies:"
echo "   pip install -r requirements.txt"
echo ""
echo "5. Set up environment variables:"
echo "   cp .env.example .env"
echo "   nano .env  # Edit with your Confluence credentials"
echo ""
echo "6. Run the API:"
echo "   uvicorn main:app --host 0.0.0.0 --port 8001"
echo ""
echo "=== Setup script completed ==="
