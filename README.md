# My First FastAPI

A simple beginner-friendly FastAPI application with markdown to Confluence conversion.

## Getting Started

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the app:**
   ```bash
   python main.py
   ```

3. **Open your browser to:**
   - App: `http://localhost:8000`
   - Interactive docs: `http://localhost:8000/docs`

## Try the API

### Using your browser:
- Go to `http://localhost:8000` - see "Hello, World!"
- Go to `http://localhost:8000/items` - see list of items
- Go to `http://localhost:8000/items/1` - see item 1

### Using curl:
```bash
# Get hello world
curl http://localhost:8000

# Get all items
curl http://localhost:8000/items

# Create a new item
curl -X POST "http://localhost:8000/items" \
  -H "Content-Type: application/json" \
  -d '{"name": "apple", "description": "red fruit"}'

# Get specific item
curl http://localhost:8000/items/1

# Convert markdown to Confluence
curl -X POST "http://localhost:8000/convert" \
  -H "Content-Type: application/json" \
  -d '{"markdown": "# Hello World\n\nThis is **bold** text."}'
```

## What's Next?

1. Add more endpoints in `main.py`
2. Connect to a database
3. Add authentication
4. Deploy to the cloud

Check out the interactive documentation at `http://localhost:8000/docs` to explore all endpoints!