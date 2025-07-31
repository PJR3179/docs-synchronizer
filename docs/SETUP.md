# Developer Setup Guide

This guide will help you set up and run the MD to Confluence API locally on your development machine.

## Prerequisites

### Required Software
- **Python 3.12+** - The application is built with Python
- **Docker** - For containerized deployment (recommended)
- **Git** - For version control
- **Node.js 18+** - Required for Mermaid diagram rendering
- **npm** - For installing JavaScript dependencies

### Optional Tools
- **curl** or **Postman** - For testing API endpoints
- **jq** - For formatting JSON responses (makes testing easier)
- **VS Code** - Recommended IDE with Python extension

## Quick Start (Docker - Recommended)

### 1. Clone the Repository
```bash
git clone https://github.com/vertexinc/prodeng-docs-synchronizer.git
cd prodeng-docs-synchronizer
```

### 2. Create Environment File
Create a `.env` file in the root directory with your Confluence credentials:

```bash
# Copy the example environment file
cp .env.example .env

# Edit with your actual values
nano .env
```

Example `.env` contents:
```env
# Confluence Configuration
CONFLUENCE_DOMAIN=your-domain.atlassian.net
CONFLUENCE_USERNAME=your-email@company.com
CONFLUENCE_API_KEY=your-api-key-here
CONFLUENCE_SPACE=YOUR_SPACE_KEY
CONFLUENCE_ROOT_PAGE=123456789

# GitHub Configuration (for private repos)
GITHUB_TOKEN=your-github-token
GITHUB_REPOSITORY=vertexinc/your-repo

# Optional: Logging
LOG_LEVEL=INFO
```

### 3. Build and Run with Docker
```bash
# Make the helper script executable
chmod +x docker-run.sh

# Build and run the container
./docker-run.sh run
```

### 4. Test the API
```bash
# Test the health endpoint
./docker-run.sh test

# Or manually test
curl http://localhost:8000/health
```

The API will be available at `http://localhost:8000`

## Manual Setup (Without Docker)

### 1. Install Python Dependencies
```bash
# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Install Node.js Dependencies (for Mermaid)
```bash
# Install mermaid-cli globally for diagram rendering
npm install -g @mermaid-js/mermaid-cli

# Verify installation
mmdc --version
```

### 3. Set Environment Variables
```bash
# Export your environment variables
export CONFLUENCE_DOMAIN=your-domain.atlassian.net
export CONFLUENCE_USERNAME=your-email@company.com
export CONFLUENCE_API_KEY=your-api-key-here
export CONFLUENCE_SPACE=YOUR_SPACE_KEY
export CONFLUENCE_ROOT_PAGE=123456789

# Optional GitHub settings
export GITHUB_TOKEN=your-github-token
export GITHUB_REPOSITORY=vertexinc/your-repo
```

### 4. Run the API Server
```bash
# Start the FastAPI server
python3 main.py

# Or use uvicorn directly
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## Getting Confluence Credentials

### API Key Generation
1. Go to [Atlassian Account Settings](https://id.atlassian.com/manage-profile/security/api-tokens)
2. Click "Create API token"
3. Give it a label (e.g., "MD2Conf Local Development")
4. Copy the generated token - this is your `CONFLUENCE_API_KEY`

### Finding Your Space Key
1. Go to your Confluence space
2. Look at the URL: `https://your-domain.atlassian.net/wiki/spaces/SPACEKEY/pages/...`
3. The `SPACEKEY` part is your `CONFLUENCE_SPACE`

### Finding Root Page ID (Optional)
1. Navigate to your target page in Confluence
2. Look at the URL: `https://your-domain.atlassian.net/wiki/spaces/SPACE/pages/123456789/Page+Title`
3. The number `123456789` is your page ID

## Testing the API

### Health Check
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "Server is running and healthy.",
  "timestamp": "2025-07-30T10:30:00Z"
}
```

### Publishing a Markdown File
```bash
curl -X POST "http://localhost:8000/publish" \
  -H "Content-Type: application/json" \
  -d '{
    "markdown_path": "docs/test-readme.md",
    "job": "md2conf",
    "domain": "your-domain.atlassian.net",
    "username": "your-email@company.com",
    "api_key": "your-api-key",
    "space": "YOUR_SPACE",
    "root_page": "123456789"
  }'
```

### Testing with GitHub URLs
```bash
curl -X POST "http://localhost:8000/publish" \
  -H "Content-Type: application/json" \
  -d '{
    "markdown_path": "https://github.com/vertexinc/your-repo/blob/main/docs/example.md",
    "job": "md2conf",
    "domain": "your-domain.atlassian.net",
    "username": "your-email@company.com",
    "api_key": "your-api-key",
    "space": "YOUR_SPACE",
    "github_token": "your-github-token"
  }'
```

## Docker Helper Script Commands

The `docker-run.sh` script provides convenient commands for Docker-based development:

```bash
# Build the Docker image
./docker-run.sh build

# Run the container (builds if needed)
./docker-run.sh run

# Stop the container
./docker-run.sh stop

# Restart the container
./docker-run.sh restart

# View container logs
./docker-run.sh logs

# Open a shell in the running container
./docker-run.sh shell

# Test the API health endpoint
./docker-run.sh test

# Show help
./docker-run.sh help
```

## Development Workflow

### 1. Code Changes
When making code changes:

```bash
# For Docker development
./docker-run.sh restart  # Rebuilds and restarts

# For manual development  
# The server will auto-reload with --reload flag
```

### 2. Testing Changes
```bash
# Test health endpoint
curl http://localhost:8000/health

# Test with a sample file
curl -X POST "http://localhost:8000/publish" \
  -H "Content-Type: application/json" \
  -d '{
    "markdown_path": "docs/simple-test.md",
    "job": "md2conf"
  }'
```

### 3. Running Tests
```bash
# Install test dependencies (if not using Docker)
pip install pytest pytest-cov httpx

# Run unit tests
python3 -m pytest tests/ -v

# Run with coverage
python3 -m pytest tests/ -v --cov=app --cov-report=term
```

## Troubleshooting

### Common Issues

#### "Container failed to start"
```bash
# Check container logs
./docker-run.sh logs

# Or for manual debugging
docker logs md2conf-api
```

#### "Module not found" errors
```bash
# Ensure you're in the virtual environment
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

#### "Mermaid diagrams not rendering"
```bash
# Check if mermaid-cli is installed
mmdc --version

# Install if missing
npm install -g @mermaid-js/mermaid-cli

# For Docker, rebuild the image
./docker-run.sh build
```

#### "API returns 500 errors"
1. Check the logs for detailed error messages
2. Verify your Confluence credentials are correct
3. Ensure the target space and page exist
4. Check that the markdown file path is valid

### Environment Variables Not Loading
If using a `.env` file with manual setup:
```bash
# Install python-dotenv
pip install python-dotenv

# Or export variables manually
export CONFLUENCE_DOMAIN=your-domain.atlassian.net
# ... etc
```

### Port Already in Use
```bash
# Check what's using port 8000
lsof -i :8000

# Kill the process or use a different port
uvicorn main:app --host 0.0.0.0 --port 8001
```

## API Documentation

Once the server is running, you can access:
- **Interactive API docs**: http://localhost:8000/docs
- **ReDoc documentation**: http://localhost:8000/redoc
- **OpenAPI schema**: http://localhost:8000/openapi.json

## File Structure

```
prodeng-docs-synchronizer/
├── app/                    # Application source code
│   ├── api/               # API endpoints
│   ├── models/            # Pydantic schemas
│   └── services/          # Business logic
├── docs/                  # Documentation and test files
├── tests/                 # Unit tests
├── deployments/           # Helm charts and deployment configs
├── viper-config/          # CI/CD configuration
├── .env                   # Environment variables (create this)
├── .env.example           # Environment template
├── docker-run.sh          # Docker helper script
├── Dockerfile             # Container definition
├── main.py                # FastAPI application entry point
├── requirements.txt       # Python dependencies
└── README.md              # Project overview
```

## Next Steps

1. **Explore the API**: Try different markdown files and options
2. **Read the main README**: For project overview and features
3. **Check the tests**: See `tests/` directory for examples
4. **Contribute**: Submit issues or pull requests on GitHub

## Support

- **GitHub Issues**: [Report bugs or request features](https://github.com/vertexinc/prodeng-docs-synchronizer/issues)
- **Documentation**: Check the `docs/` folder for more examples
- **Code Examples**: See `tests/` for API usage examples
