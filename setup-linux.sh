#!/bin/bash
# Setup script for Linux environment

set -e

echo "Setting up md2conf service for Linux..."

# Check if running on Linux
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    echo "Warning: This script is designed for Linux. Current OS: $OSTYPE"
fi

# Update package manager
echo "Updating package manager..."
sudo apt update

# Install Python 3 and pip if not already installed
echo "Installing Python 3 and pip..."
sudo apt install -y python3 python3-pip python3-venv

# Install Node.js and npm
echo "Installing Node.js and npm..."
curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
sudo apt install -y nodejs

# Verify installations
echo "Verifying installations..."
python3 --version
pip3 --version
node --version
npm --version

# Create Python virtual environment
echo "Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Install mermaid-cli globally
echo "Installing mermaid-cli..."
sudo npm install -g @mermaid-js/mermaid-cli

# Verify mermaid-cli installation
echo "Verifying mermaid-cli installation..."
mmdc --version

# Create .env file template if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env template..."
    cat > .env << EOL
CONFLUENCE_DOMAIN=your-domain.atlassian.net
CONFLUENCE_USERNAME=your-email@company.com
CONFLUENCE_API_KEY=your-api-key
CONFLUENCE_SPACE=your-space-key
CONFLUENCE_ROOT_PAGE=your-root-page-id
EOL
    echo "Created .env file. Please update with your Confluence credentials."
fi

echo "Setup complete!"
echo ""
echo "To run the service:"
echo "1. Activate the virtual environment: source venv/bin/activate"
echo "2. Update .env with your Confluence credentials"
echo "3. Start the server: uvicorn main:app --host 0.0.0.0 --port 8001"
echo ""
echo "Test with curl:"
echo 'curl -X POST "http://localhost:8001/publish" \'
echo '  -H "Content-Type: application/json" \'
echo '  -d '\''{'
echo '    "markdown_path": "docs/simple-test.md"'
echo '  }'\'
