from fastapi import FastAPI
from pydantic import BaseModel

# Create the FastAPI app
app = FastAPI(title="My First API")

# Define a simple data model
class Item(BaseModel):
    name: str
    description: str = None

class MarkdownRequest(BaseModel):
    markdown: str

class MarkdownResponse(BaseModel):
    confluence_content: str

# Root endpoint
@app.get("/")
def hello_world():
    return {"message": "Hello, World!"}

# Get all items
@app.get("/items")
def get_items():
    return {"items": ["apple", "banana", "orange"]}

# Create a new item
@app.post("/items")
def create_item(item: Item):
    return {"message": f"Created item: {item.name}"}

# Get a specific item
@app.get("/items/{item_id}")
def get_item(item_id: int):
    return {"item_id": item_id, "name": f"Item {item_id}"}

# Convert markdown to Confluence format
@app.post("/convert", response_model=MarkdownResponse)
def convert_markdown(request: MarkdownRequest):
    """Convert markdown to Confluence storage format"""
    try:
        from markdown_to_confluence.markdown_converter import MarkdownConverter
        
        converter = MarkdownConverter()
        confluence_content = converter.convert(request.markdown)
        
        return MarkdownResponse(confluence_content=confluence_content)
    except ImportError:
        return {"error": "markdown-to-confluence package not installed"}
    except Exception as e:
        return {"error": f"Conversion failed: {str(e)}"}

# Run the app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
