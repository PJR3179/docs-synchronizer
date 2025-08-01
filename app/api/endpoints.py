"""
API endpoints for the MD to Confluence Converter.
"""
from fastapi import APIRouter, Depends, HTTPException
from app.models.schemas import MarkdownRequest, MarkdownResponse, HealthResponse
from app.services.md2conf_service import MD2ConfService

# Create router for API endpoints
router = APIRouter()

# Dependency to get service instances
def get_md2conf_service() -> MD2ConfService:
    """Dependency to provide MD2ConfService instance."""
    return MD2ConfService()


@router.get("/", tags=["General"])
def hello_world():
    """Root endpoint returning a simple greeting."""
    return {"message": "Hello, World!"}


@router.get("/health", tags=["Health"])
def health_check():
    """Simple health check for Kubernetes/ArgoCD."""
    try:
        # Basic health check - just return 200 OK
        return {"status": "healthy", "service": "md2conf-api"}
    except Exception as e:
        # If anything fails, return 500
        raise HTTPException(status_code=500, detail="Service unhealthy")


@router.post("/publish", response_model=MarkdownResponse, tags=["Publishing"])
def publish_markdown(
    request: MarkdownRequest,
    md2conf_service: MD2ConfService = Depends(get_md2conf_service)
) -> MarkdownResponse:
    """
    Publish markdown content based on the specified job type.
    
    This endpoint acts as a dispatcher that processes different types of publishing jobs:
    - "md2conf": Uses MD2ConfService for Confluence publishing (default)
    - Future job types can be added here
    
    Args:
        request: The markdown publishing request containing job type and parameters.
        md2conf_service: The MD2ConfService instance (injected as dependency).
    
    Returns:
        MarkdownResponse: Result of the publishing operation.
    """
    # Determine job type (default to "md2conf" for backward compatibility)
    job_type = request.job.lower() if request.job else "md2conf"
    
    # Define supported job types
    supported_jobs = ["md2conf"]
    
    # Validate job type
    if job_type not in supported_jobs:
        supported_types = ", ".join(supported_jobs)
        return MarkdownResponse(
            success=False,
            message=f"Unsupported job type: '{request.job}'. Supported types: {supported_types}",
            error="INVALID_JOB_TYPE"
        )
    
    # Process based on job type
    if job_type == "md2conf":
        return md2conf_service.publish_markdown(request)
    
    # Future job types can be added here:
    # elif job_type == "pandoc":
    #     return pandoc_service.publish_markdown(request)
    # elif job_type == "custom":
    #     return custom_service.publish_markdown(request)
    
    # This should never be reached due to validation above, but added for safety
    return MarkdownResponse(
        success=False,
        message=f"Job type '{job_type}' is not implemented yet",
        error="JOB_NOT_IMPLEMENTED"
    )
