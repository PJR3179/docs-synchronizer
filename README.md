#
# Project Setup Notes

**Do not commit your `venv/` directory to version control.**

Each developer should create their own virtual environment after cloning the repository:

```sh
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#
# Local Run Commands

You can use your local `.env` file to populate environment variables for curl testing. Run these commands from your project root:

```sh
# Load .env variables into your shell
export $(grep -v '^#' .env | xargs)
```

#### Test the Markdown to Confluence API
```sh
curl -X POST "http://localhost:8000/publish" \
  -H "Content-Type: application/json" \
  -d '{
    "markdown_path": "docs/simple-test.md",
    "domain": "'$CONFLUENCE_DOMAIN'",
    "username": "'$CONFLUENCE_USERNAME'",
    "api_key": "'$CONFLUENCE_API_KEY'",
    "space": "'$CONFLUENCE_SPACE'",
    "root_page": "'$CONFLUENCE_ROOT_PAGE'"
  }'
```

#### Alternative: Test just the health endpoint
```sh
curl -X GET "http://localhost:8000/health"
```

#### Alternative: Test the root endpoint
```sh
curl -X GET "http://localhost:8000/"
```

# MD2Conf Service - Deployment Guide

This guide covers deploying the md2conf service in Linux and macOS environments.

## Quick Start Options



### Option 0: macOS Installation

1. **Install Homebrew (if not already installed):**

    ```bash
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    ```

2. **Install dependencies:**

    ```bash
    brew update
    brew install python3 node npm curl
    ```

3. **Set up Python virtual environment and install Python dependencies:**

    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

4. **Install Mermaid CLI globally:**

    ```bash
    npm install -g @mermaid-js/mermaid-cli
    ```

5. **(Optional) Use `python` as a shortcut for `python3`:**

    If you want to use `python` instead of `python3` in your terminal, add this alias to your `~/.zshrc`:
    ```bash
    echo 'alias python="python3"' >> ~/.zshrc
    source ~/.zshrc
    ```

6. **Configure environment:**

    ```bash
    # Edit .env file with your Confluence credentials
    nano .env
    ```

7. **Run the service:**

    ```bash
    source venv/bin/activate
    uvicorn main:app --host 0.0.0.0 --port 8000
    ```


---


## Linux Deployment Guide

This guide covers deploying the md2conf service in Linux environments.

## Quick Start Options

### Option 1: Direct Linux Installation

1. **Clone and setup:**
```bash
git clone <your-repo>
cd prodeng-md-to-confluence-2
chmod +x setup-linux.sh
./setup-linux.sh
```

2. **Configure environment:**
```bash
# Edit .env file with your Confluence credentials
nano .env
```

3. **Run the service:**
```bash
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Option 2: Docker Deployment

1. **Using Docker Compose (Recommended):**
```bash
# Create .env file with your credentials
cp .env.example .env
nano .env

# Start the service
docker-compose up -d

# Check logs
docker-compose logs -f
```

2. **Using Docker directly:**
```bash
# Build the image
docker build -t md2conf-api .

# Run the container
docker run -d \
  --name md2conf-api \
  -p 8000:8000 \
  --env-file .env \
  -v $(pwd)/docs:/app/docs:ro \
  md2conf-api
```

## Testing

### Health Check
```bash
curl http://localhost:8000/health
```

### Publish Markdown
```bash
# Make test script executable
chmod +x test-linux.sh

# Run tests
./test-linux.sh
```

### Manual curl test
```bash
curl -X POST "http://localhost:8000/publish" \
  -H "Content-Type: application/json" \
  -d '{
    "markdown_path": "docs/simple-test.md",
    "domain": "your-domain.atlassian.net",
    "username": "your-email@company.com",
    "api_key": "your-api-key",
    "space": "YOUR-SPACE",
    "root_page": "123456789"
  }'
```

## Environment Variables

Create a `.env` file with:

```bash
CONFLUENCE_DOMAIN=your-domain.atlassian.net
CONFLUENCE_USERNAME=your-email@company.com
CONFLUENCE_API_KEY=your-confluence-api-key
CONFLUENCE_SPACE=YOUR-SPACE-KEY
CONFLUENCE_ROOT_PAGE=your-root-page-id
```

## Dependencies

### System Requirements
- Python 3.8+
- Node.js 16+ and npm
- curl (for testing)

### Linux Package Installation
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip python3-venv nodejs npm curl

# CentOS/RHEL/Fedora
sudo yum install python3 python3-pip nodejs npm curl
# or for newer versions:
sudo dnf install python3 python3-pip nodejs npm curl
```

### Python Dependencies
```bash
pip install fastapi uvicorn pydantic pydantic-settings md2conf
```

### Mermaid CLI
```bash
sudo npm install -g @mermaid-js/mermaid-cli
```

## Troubleshooting

### Common Issues

1. **Node.js/npm not found:**
```bash
# Check if Node.js is in PATH
which node
which npm

# Add to PATH if needed
export PATH="/usr/local/bin:$PATH"
```

2. **Mermaid CLI not found:**
```bash
# Verify installation
mmdc --version

# Reinstall if needed
sudo npm uninstall -g @mermaid-js/mermaid-cli
sudo npm install -g @mermaid-js/mermaid-cli
```

3. **Permission issues:**
```bash
# Make scripts executable
chmod +x setup-linux.sh test-linux.sh

# Fix npm permissions
sudo chown -R $(whoami) ~/.npm
```

4. **Docker issues:**
```bash
# Check container logs
docker-compose logs md2conf-api

# Restart service
docker-compose restart

# Rebuild if needed
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

## Production Deployment

### Using systemd service
```bash
# Create service file
sudo nano /etc/systemd/system/md2conf-api.service
```

Service file content:
```ini
[Unit]
Description=MD2Conf API Service
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/prodeng-md-to-confluence-2
Environment=PATH=/path/to/prodeng-md-to-confluence-2/venv/bin
ExecStart=/path/to/prodeng-md-to-confluence-2/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable md2conf-api
sudo systemctl start md2conf-api
sudo systemctl status md2conf-api
```

### Using nginx reverse proxy
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Differences from Windows

The service automatically detects the operating system and adjusts:

1. **Path separators:** Uses `:` instead of `;` for PATH
2. **Node.js locations:** Checks common Linux paths like `/usr/bin`, `/usr/local/bin`
3. **npm global directory:** Uses `~/.npm-global/bin` instead of Windows AppData
4. **File permissions:** Scripts need execute permissions (`chmod +x`)

## API Endpoints

- `GET /health` - Health check endpoint
- `POST /publish` - Publish markdown to Confluence

## Monitoring

### Docker health checks
```bash
docker-compose ps
docker inspect md2conf-api | grep -A 5 -B 5 Health
```

### Log monitoring
```bash
# Docker logs
docker-compose logs -f md2conf-api

# System service logs
sudo journalctl -u md2conf-api -f
```
