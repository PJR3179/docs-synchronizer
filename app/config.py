"""
Configuration settings for the application.
"""
import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Application settings
    app_title: str = "MD to Confluence Converter"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Server settings
    host: str = "0.0.0.0"
    port: int = 8080
    
    # Confluence settings (can be overridden by request parameters)
    confluence_domain: Optional[str] = None
    confluence_username: Optional[str] = None
    confluence_api_key: Optional[str] = None
    confluence_space: Optional[str] = None
    confluence_root_page: Optional[str] = None
    
    # GitHub settings
    github_token: Optional[str] = None
    github_organization: str = "vertexinc"  # Default but configurable
    github_markdown_file: Optional[str] = None
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Check for alternative environment variable names
        if not self.github_token:
            self.github_token = os.getenv("gh_token") or os.getenv("GITHUB_TOKEN")
    github_markdown_file: Optional[str] = None
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()
