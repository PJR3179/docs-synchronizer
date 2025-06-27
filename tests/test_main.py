import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_root_endpoint():
    """Test the root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Docs as Code - Confluence API"}

def test_health_endpoint():
    """Test the health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_publish_endpoint_invalid_folder():
    """Test the publish endpoint with invalid folder"""
    request_data = {
        "folder": "/nonexistent/folder",
        "username": "test@example.com",
        "password": "test-token",
        "confluence_base_url": "https://example.atlassian.net/wiki",
        "space_key": "TEST",
        "parent_page_id": "123456789"
    }
    
    response = client.post("/publish", json=request_data)
    assert response.status_code == 400
    assert "does not exist" in response.json()["detail"]

@patch('main.publish_markdown_files')
def test_publish_endpoint_success(mock_publish):
    """Test successful publish endpoint"""
    # Create a temporary directory with a markdown file
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a test markdown file
        test_file = Path(temp_dir) / "test.md"
        test_file.write_text("# Test Document\n\nThis is a test.")
        
        mock_publish.return_value = ["Test Document (ID: 12345)"]
        
        request_data = {
            "folder": temp_dir,
            "username": "test@example.com",
            "password": "test-token",
            "confluence_base_url": "https://example.atlassian.net/wiki",
            "space_key": "TEST",
            "parent_page_id": "123456789"
        }
        
        response = client.post("/publish", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "Successfully processed 1 pages" in data["message"]
        assert data["pages_published"] == ["Test Document (ID: 12345)"]

@patch('main.publish_markdown_files')
def test_publish_endpoint_dry_run(mock_publish):
    """Test publish endpoint in dry run mode"""
    with tempfile.TemporaryDirectory() as temp_dir:
        test_file = Path(temp_dir) / "test.md"
        test_file.write_text("# Test Document\n\nThis is a test.")
        
        mock_publish.return_value = ["Test Document (DRY RUN)"]
        
        request_data = {
            "folder": temp_dir,
            "username": "test@example.com",
            "password": "test-token",
            "confluence_base_url": "https://example.atlassian.net/wiki",
            "space_key": "TEST",
            "parent_page_id": "123456789",
            "dry_run": True
        }
        
        response = client.post("/publish", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert data["pages_published"] == ["Test Document (DRY RUN)"]
