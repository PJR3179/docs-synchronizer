
# 📦 Refactored Project Structure

## File Structure

```text
project-root/
│
├── app/                           # Main application package
│   ├── __init__.py               # Package marker
│   ├── main.py                   # FastAPI app instance and route registration
│   ├── config.py                 # Settings and environment configuration
│   ├── api/                      # API layer
│   │   ├── __init__.py
│   │   └── endpoints.py          # All API endpoints (/health, /publish, etc.)
│   ├── models/                   # Data models
│   │   ├── __init__.py
│   │   └── schemas.py            # Pydantic models for requests/responses
│   └── services/                 # Business logic
│       ├── __init__.py
│       └── md2conf_service.py    # Core md2conf operations
│
├── tests/                        # Test files
│   └── test_md2conf_service.py   # Unit tests for the service
│
├── main.py                       # Application entry point (refactored)
├── entrypoint.py                 # GitHub Actions entry point (updated)
├── action.yml                    # GitHub Actions configuration
├── requirements.txt              # Dependencies
└── README.md                     # Documentation
```

## What Each File Contains

- **app/main.py**: FastAPI app instance creation, router registration, backwards compatibility for entrypoint.py
- **app/config.py**: Centralized configuration using Pydantic BaseSettings, environment variable management, default values for all settings
- **app/models/schemas.py**: All Pydantic models for requests and responses, type hints and validation rules, clear documentation for each field
- **app/api/endpoints.py**: All API route definitions, dependency injection for services, proper response models and documentation
- **app/services/md2conf_service.py**: Core business logic for md2conf operations, parameter validation, command building and execution, error handling
- **tests/test_md2conf_service.py**: Unit tests for the service layer, mock external dependencies, test both success and failure scenarios

## Benefits of This Structure

1. **Separation of Concerns**: Each file has a single responsibility
2. **Testability**: Business logic is separated from API layer, making it easy to test
3. **Maintainability**: Code is organized logically and easy to navigate
4. **Scalability**: Easy to add new endpoints, services, or models
5. **Dependency Injection**: Services can be easily mocked and tested
6. **Configuration Management**: Centralized settings with environment variable support

## Key Improvements

- **Type Safety**: Better type hints throughout the codebase
- **Error Handling**: Centralized error handling in the service layer
- **Logging**: Consistent logging patterns
- **Documentation**: Better API documentation with proper response models
- **Testing**: Structure supports easy unit testing
- **Configuration**: Environment-based configuration management

# MD2Conf Service

A FastAPI-based web service that automatically publishes Markdown files to Confluence using the [md2conf](https://github.com/hunyadi/md2conf) CLI tool. This service supports Mermaid diagram rendering and can be used as both a standalone API and a GitHub Action.

## 🚀 Quick Start

The easiest way to get started is by integrating the GitHub Actions workflow into your repository to automatically publish your documentation to Confluence.

### Prerequisites

- GitHub repository with markdown documentation
- Confluence API token with publishing permissions
- Access to GitHub repository secrets

### 1. Create Confluence API Token

First, create a Confluence API token with the necessary scopes:

1. Go to [Atlassian API Tokens](https://id.atlassian.com/manage-profile/security/api-tokens)
2. Click **Create API token**
3. Give it a descriptive name (e.g., "GitHub Docs Sync")
4. **Important**: Your token needs these scopes for full functionality:
   - `read:confluence-space.summary`
   - `read:confluence-content.all` 
   - `write:confluence-content`
   - `write:confluence-file`
   - `write:confluence-props`
5. Copy the generated token - you'll need it for GitHub Secrets

### 2. Add GitHub Actions Workflow

Copy the example workflow to your repository:

```bash
# In your repository root
mkdir -p .github/workflows
curl -o .github/workflows/docs-sync.yaml https://raw.githubusercontent.com/vertexinc/prodeng-docs-synchronizer/main/.github/workflows/example.yaml
```

Or manually create `.github/workflows/docs-sync.yaml` with this content:

```yaml
name: Sync Documentation to Confluence

on:
  workflow_dispatch:
    inputs:
      markdown_path:
        description: 'Path to the markdown file in this repo'
        required: true
      repository:
        description: 'Repo name (no owner, e.g. my-project)'
        required: true
      space:
        description: 'Confluence space key'
        required: true
      root_page:
        description: 'Confluence root page ID'
        required: true

jobs:
  sync-docs:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Health Check
        run: |
          echo "Checking health endpoint..."
          curl -fsS "https://prodeng-docs-synchronizer-dev.doh.vtxdev.net/actuator/health" || exit 1

      - name: Call Docs Sync API
        id: api-call-2
        uses: fjogeleit/http-request-action@v1
        with:
          url: 'https://prodeng-docs-synchronizer-dev.doh.vtxdev.net/publish'
          method: 'POST'
          customHeaders: '{"Content-Type":"application/json"}'
          #Replace with wanted page information, make sure secrets are added!
          data: |
            {
              "markdown_path": "docs/example.md",
              "repository": "repo-project",
              "domain": "vertexinc.atlassian.net",
              "username": "${{ secrets.ATLASSIAN_USERNAME }}",
              "api_key": "${{ secrets.ATLASSIAN_TOKEN }}",
              "space": "ABC",
              "root_page": "$12345678",
              "job": "md2conf"
            }
          timeout: 300000
```

### 3. Configure GitHub Secrets

Add these secrets to your GitHub repository:

1. Go to your repository **Settings** → **Secrets and variables** → **Actions**
2. Add the following repository secrets:

   - **`ATLASSIAN_USERNAME`**: Your Confluence email address
   - **`ATLASSIAN_TOKEN`**: The API token you created in step 1

### 4. Configure Your Documentation

Update your workflow with your specific details:

- **`markdown_path`**: Path to your markdown file (e.g., `docs/api-guide.md`)
- **`repository`**: Your repository name without owner (e.g., `my-awesome-project`)
- **`space`**: Your Confluence space key (e.g., `DOCS`, `ENG`, `PROJ`)
- **`root_page`**: Confluence page ID where docs should be published
**You can find the space and root_page values in the Confluence Link to your page!**

### 5. Run the Workflow

1. Go to your repository's **Actions** tab
2. Select **Sync Documentation to Confluence**
3. Click **Run workflow**

Your markdown documentation will be automatically converted and published to Confluence with proper formatting, diagrams, and structure!

## 🛠️ Local Development Setup

For developers who want to run the service locally or contribute to the project:

### Prerequisites

- Python 3.8+ 
- Node.js 16+ and npm
- Confluence API token (from Quick Start above)

### 1. Clone and Setup

```bash
git clone https://github.com/vertexinc/prodeng-docs-synchronizer.git
cd prodeng-docs-synchronizer
```

### 2. Create Virtual Environment

⚠️ **Important**: Never commit your `venv/` directory to version control. Each developer should create their own:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Install Mermaid CLI (Optional - for diagram rendering)

```bash
npm install -g @mermaid-js/mermaid-cli
```

### 4. Configure Environment

Copy the example environment file and add your Confluence credentials:

```bash
cp .env.example .env
# Edit .env with your Confluence details
```

Required environment variables:
```bash
CONFLUENCE_DOMAIN=your-domain.atlassian.net
CONFLUENCE_USERNAME=your-email@company.com
CONFLUENCE_API_KEY=your-confluence-api-key
CONFLUENCE_SPACE=YOUR-SPACE-KEY
CONFLUENCE_ROOT_PAGE=your-root-page-id
```

### 5. Start the Service

```bash
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000` with interactive docs at `http://localhost:8000/docs`.

### 4. Configure Environment

Copy the example environment file and add your Confluence credentials:

```bash
cp .env.example .env
# Edit .env with your Confluence details
```

Required environment variables:
```bash
CONFLUENCE_DOMAIN=your-domain.atlassian.net
CONFLUENCE_USERNAME=your-email@company.com
CONFLUENCE_API_KEY=your-confluence-api-key
CONFLUENCE_SPACE=YOUR-SPACE-KEY
CONFLUENCE_ROOT_PAGE=your-root-page-id
```

### 5. Start the Service

```bash
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000` with interactive docs at `http://localhost:8000/docs`.

## 📚 Usage

### API Endpoints

- `GET /health` - Health check endpoint
- `POST /publish` - Publish markdown to Confluence
- `GET /docs` - Interactive API documentation

### Testing the API

First, load your environment variables:

```bash
export $(grep -v '^#' .env | xargs)
```

Test the health endpoint:

Check service health:

```bash
curl -X GET "http://localhost:8000/health"
```

Get supported job types:

```bash
curl -X GET "http://localhost:8000/jobs"
```

Publish a markdown file:

```bash
curl -X POST "http://localhost:8000/publish" \
  -H "Content-Type: application/json" \
  -d '{
    "markdown_path": "docs/mermaid-test.md",
    "job": "md2conf",
    "domain": "'$CONFLUENCE_DOMAIN'",
    "username": "'$CONFLUENCE_USERNAME'",
    "api_key": "'$CONFLUENCE_API_KEY'",
    "space": "'$CONFLUENCE_SPACE'",
    "root_page": "'$CONFLUENCE_ROOT_PAGE'"
  }'
```

**Job Parameter**: The `job` parameter specifies the processing type for the `/publish` endpoint:
- `"md2conf"`: Process using MD2Conf service for Confluence publishing
- If omitted, defaults to `"md2conf"` for backward compatibility
- Invalid job types return an error with list of supported types

**Available Endpoints**:
- `GET /health` - Health check
- `GET /jobs` - List supported job types
- `POST /publish` - Dispatch publishing job based on job type

The `/publish` endpoint acts as a job dispatcher, routing requests to appropriate processing services based on the `job` parameter. This architecture makes it easy to add new processing types in the future.

### GitHub Action Usage

This service can also be used as a GitHub Action. See `action.yml` for configuration details.

## 🏗️ Architecture

The service is built with:

- **FastAPI**: Modern, fast web framework for Python APIs
- **md2conf**: CLI tool for converting Markdown to Confluence
- **Mermaid CLI**: For rendering diagrams in markdown
- **Pydantic**: Data validation and settings management

### Project Structure

```
├── app/
│   ├── api/
│   │   └── endpoints.py         # API route definitions
│   ├── models/
│   │   └── schemas.py           # Pydantic models
│   └── services/
│       └── md2conf_service.py   # Core business logic
├── tests/
│   └── test_md2conf_service.py  # Unit tests
├── docs/                        # Example markdown files
├── main.py                      # FastAPI application entry point
├── entrypoint.py               # GitHub Action entry point
└── requirements.txt            # Python dependencies
```

## 🧪 Testing

Run the unit tests:

```bash
source venv/bin/activate
pip install pytest pytest-mock  # If not already installed
python -m pytest tests/ -v
```

### Platform-Specific Setup

#### macOS (Homebrew)

```bash
# Install system dependencies
brew update
brew install python3 node npm curl

# Optional: Create python alias
echo 'alias python="python3"' >> ~/.zshrc
source ~/.zshrc
```

#### Linux

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip python3-venv nodejs npm curl

# CentOS/RHEL/Fedora
sudo yum install python3 python3-pip nodejs npm curl
# or for newer versions:
sudo dnf install python3 python3-pip nodejs npm curl
```

### Production Deployment

#### Systemd Service

Create a systemd service for automatic startup:

```bash
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
WorkingDirectory=/path/to/prodeng-md-to-confluence
Environment=PATH=/path/to/prodeng-md-to-confluence/venv/bin
ExecStart=/path/to/prodeng-md-to-confluence/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
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

#### Nginx Reverse Proxy

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

## 🔧 Troubleshooting

### Common Issues

**1. Module not found errors:**

- Ensure you're in the activated virtual environment
- Reinstall dependencies: `pip install -r requirements.txt`

**2. Node.js/npm not found:**

```bash
# Check if Node.js is in PATH
which node
which npm

# Add to PATH if needed (macOS/Linux)
export PATH="/usr/local/bin:$PATH"
```

**3. Mermaid CLI not found:**

```bash
# Verify installation
mmdc --version

# Reinstall if needed
npm uninstall -g @mermaid-js/mermaid-cli
npm install -g @mermaid-js/mermaid-cli
```

**4. Permission issues:**

```bash
# Make scripts executable
chmod +x setup-linux.sh test-linux.sh

# Fix npm permissions
sudo chown -R $(whoami) ~/.npm
```

**5. Virtual environment issues:**

If you see interpreter path errors, recreate your virtual environment:

```bash
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```


### Monitoring

#### Health Checks

```bash
# Simple health check
curl http://localhost:8000/health

# Docker health checks
docker-compose ps
docker inspect md2conf-api | grep -A 5 -B 5 Health
```

#### Log Monitoring

```bash
# Docker logs
docker-compose logs -f md2conf-api

# System service logs
sudo journalctl -u md2conf-api -f
```

## 🔒 Security Considerations

- Store API keys securely in environment variables, never in code
- Use HTTPS in production with proper SSL certificates
- Consider implementing authentication for the API endpoints
- Regularly update dependencies to patch security vulnerabilities

## 🆘 Support

For issues and questions:

- Check the troubleshooting section above
- Review existing GitHub issues
- Create a new issue with detailed information about your problem
