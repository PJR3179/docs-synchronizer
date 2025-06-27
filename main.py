import os
import logging
from pathlib import Path
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
from confluence_publisher import publish_markdown_files

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Docs as Code - Confluence API",
    description="Publish markdown documentation to Confluence",
    version="1.0.0"
)

class PublishRequest(BaseModel):
    folder: str
    username: str
    password: str
    confluence_base_url: str
    space_key: str
    parent_page_id: str
    dry_run: Optional[bool] = False

class PublishResponse(BaseModel):
    success: bool
    message: str
    pages_published: Optional[List[str]] = None

@app.get("/")
async def root():
    return {"message": "Docs as Code - Confluence API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/publish", response_model=PublishResponse)
async def publish_docs(request: PublishRequest):
    """
    Publish markdown files from a folder to Confluence
    """
    try:
        # Validate folder exists
        folder_path = Path(request.folder)
        if not folder_path.exists():
            raise HTTPException(status_code=400, detail=f"Folder {request.folder} does not exist")
        
        # Publish markdown files to Confluence
        published_pages = publish_markdown_files(
            folder=request.folder,
            username=request.username,
            password=request.password,
            confluence_base_url=request.confluence_base_url,
            space_key=request.space_key,
            parent_page_id=request.parent_page_id,
            dry_run=request.dry_run
        )
        
        return PublishResponse(
            success=True,
            message=f"Successfully processed {len(published_pages)} pages",
            pages_published=published_pages
        )
        
    except Exception as e:
        logger.error(f"Error publishing docs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
