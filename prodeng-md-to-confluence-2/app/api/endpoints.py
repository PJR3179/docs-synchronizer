"""
API endpoints for the MD to Confluence Converter.
"""
from fastapi import APIRouter, Depends
from app.models.schemas import MarkdownRequest, MarkdownResponse, HealthResponse
from app.services.md2conf_service import MD2ConfService

# Create router for API endpoints
router = APIRouter()

# Dependency to get service instance
def get_md2conf_service() -> MD2ConfService:
    """Dependency to provide MD2ConfService instance."""
    return MD2ConfService()


@router.get("/", tags=["General"])
def hello_world():
    """Root endpoint returning a simple greeting."""
    return {"message": "Hello, World!"}


@router.get("/health", response_model=HealthResponse, tags=["Health"])
def health_check():
    """Health check endpoint to verify service status."""
    print("Health check endpoint called.")
    return HealthResponse(status="Server is running and healthy.")


@router.post("/publish", response_model=MarkdownResponse, tags=["Publishing"])
def publish_markdown(
    request: MarkdownRequest,
    service: MD2ConfService = Depends(get_md2conf_service)
) -> MarkdownResponse:
    """
    Convert and publish markdown to Confluence using md2conf.
    
    Args:
        request: The markdown publishing request containing all necessary parameters.
        service: The MD2ConfService instance (injected as dependency).
    
    Returns:
        MarkdownResponse: Result of the publishing operation.
    """
    return service.publish_markdown(request)
