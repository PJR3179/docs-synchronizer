"""
Main FastAPI application entry point.
"""
from fastapi import FastAPI
from app.api.endpoints import router
from app.config import settings

# Create the FastAPI app
app = FastAPI(
    title=settings.app_title,
    version=settings.app_version,
    description="Automatically publish markdown files to Confluence using md2conf"
)

# Include API routes
app.include_router(router)

# Add health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for Docker and monitoring."""
    return {"status": "healthy", "service": "md2conf-api"}

# For backwards compatibility, expose the convert_markdown function
from app.services.md2conf_service import MD2ConfService
from app.models.schemas import MarkdownRequest

def convert_markdown(request: MarkdownRequest):
    """Backwards compatibility function for entrypoint.py"""
    service = MD2ConfService()
    return service.publish_markdown(request)

# Run the app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.host, port=settings.port)
