"""
Job dispatcher service for handling different types of publishing jobs.
"""
from typing import Dict, Callable
from app.models.schemas import MarkdownRequest, MarkdownResponse
from app.services.md2conf_service import MD2ConfService


class JobDispatcher:
    """
    Dispatcher service that routes publishing requests to appropriate handlers.
    
    This service acts as a registry and dispatcher for different job types,
    making it easy to add new processing types in the future.
    """
    
    def __init__(self):
        """Initialize the job dispatcher with available job handlers."""
        self._handlers: Dict[str, Callable[[MarkdownRequest], MarkdownResponse]] = {}
        self._md2conf_service = MD2ConfService()
        
        # Register available job handlers
        self._register_handlers()
    
    def _register_handlers(self):
        """Register all available job type handlers."""
        self._handlers["md2conf"] = self._handle_md2conf_job
        # Future job types can be registered here:
        # self._handlers["pandoc"] = self._handle_pandoc_job
        # self._handlers["custom"] = self._handle_custom_job
    
    def get_supported_job_types(self) -> list:
        """Get list of supported job types."""
        return list(self._handlers.keys())
    
    def is_job_supported(self, job_type: str) -> bool:
        """Check if a job type is supported."""
        return job_type.lower() in self._handlers
    
    def dispatch_job(self, request: MarkdownRequest) -> MarkdownResponse:
        """
        Dispatch a publishing job to the appropriate handler.
        
        Args:
            request: The markdown publishing request.
            
        Returns:
            MarkdownResponse: Result of the publishing operation.
        """
        # Determine job type (default to "md2conf" for backward compatibility)
        job_type = request.job.lower() if request.job else "md2conf"
        
        # Check if job type is supported
        if not self.is_job_supported(job_type):
            supported_types = ", ".join(self.get_supported_job_types())
            return MarkdownResponse(
                success=False,
                message=f"Unsupported job type: '{request.job}'. Supported types: {supported_types}",
                error="INVALID_JOB_TYPE"
            )
        
        # Dispatch to appropriate handler
        handler = self._handlers[job_type]
        return handler(request)
    
    def _handle_md2conf_job(self, request: MarkdownRequest) -> MarkdownResponse:
        """Handle md2conf publishing jobs."""
        return self._md2conf_service.publish_markdown(request)
    
    # Future job handlers can be added here:
    # def _handle_pandoc_job(self, request: MarkdownRequest) -> MarkdownResponse:
    #     """Handle pandoc publishing jobs."""
    #     # Implementation for pandoc-based publishing
    #     pass
    #
    # def _handle_custom_job(self, request: MarkdownRequest) -> MarkdownResponse:
    #     """Handle custom publishing jobs."""
    #     # Implementation for custom publishing logic
    #     pass
