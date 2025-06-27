# Example: Testing the FastAPI Service

This document shows how to test the new FastAPI-based Confluence publisher.

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the FastAPI server:**
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

3. **Access the API documentation:**
   - Open your browser to `http://localhost:8000/docs`
   - This provides an interactive Swagger UI for testing the API

## Testing the API

### Health Check
```bash
curl http://localhost:8000/health
```

### Publish Example (Dry Run)
```bash
curl -X POST "http://localhost:8000/publish" \
  -H "Content-Type: application/json" \
  -d '{
    "folder": "./example-docs",
    "username": "your-email@domain.com",
    "password": "your-api-token",
    "confluence_base_url": "https://yourdomain.atlassian.net/wiki",
    "space_key": "YOUR_SPACE",
    "parent_page_id": "123456789",
    "dry_run": true
  }'
```

## Command Line Usage

You can also use the confluence_publisher.py script directly:

```bash
python confluence_publisher.py \
  --folder "./example-docs" \
  --username "your-email@domain.com" \
  --password "your-api-token" \
  --confluence-base-url "https://yourdomain.atlassian.net/wiki" \
  --space-key "YOUR_SPACE" \
  --parent-page-id "123456789" \
  --dry-run
```

## Docker Usage

1. **Build the Docker image:**
   ```bash
   docker build -t docs-as-code-confluence .
   ```

2. **Run the container:**
   ```bash
   docker run -p 8000:8000 docs-as-code-confluence
   ```

## Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
python -m pytest tests/ -v
```
