"""
Pydantic models for request and response schemas.
"""
from pydantic import BaseModel
from typing import Optional


class MarkdownRequest(BaseModel):
    """Request model for publishing markdown to Confluence."""
    markdown_path: str
    job: Optional[str] = None           # Job type to determine processing method
    domain: Optional[str] = None
    space: Optional[str] = None
    username: Optional[str] = None
    api_key: Optional[str] = None
    root_page: Optional[str] = None
    github_token: Optional[str] = None  # For accessing private repos
    repository: Optional[str] = None    # Format: owner/repo
    ref: str = "main"                   # Branch, tag, or commit SHA


class MarkdownResponse(BaseModel):
    """Response model for markdown publishing operations."""
    success: bool
    message: str
    error: Optional[str] = None


class HealthResponse(BaseModel):
    """Response model for health check endpoint."""
    status: str
