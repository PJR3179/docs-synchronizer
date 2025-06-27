import pytest
import tempfile
import json
from pathlib import Path
from unittest.mock import patch, MagicMock
from confluence_publisher import ConfluencePublisher, publish_markdown_files

class TestConfluencePublisher:
    
    def test_markdown_conversion(self):
        """Test basic markdown to Confluence conversion"""
        publisher = ConfluencePublisher(
            "https://example.atlassian.net/wiki",
            "test@example.com",
            "token",
            "TEST"
        )
        
        markdown = "# Header\n\nThis is **bold** text.\n\n```python\nprint('hello')\n```"
        result = publisher.convert_markdown_to_confluence(markdown)
        
        assert "<h1>" in result
        assert "<strong>" in result
        assert "<ac:structured-macro" in result

    @patch('confluence_publisher.requests.Session')
    def test_create_page_success(self, mock_session):
        """Test successful page creation"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "12345", "title": "Test Page"}
        
        mock_session_instance = MagicMock()
        mock_session_instance.post.return_value = mock_response
        mock_session.return_value = mock_session_instance
        
        publisher = ConfluencePublisher(
            "https://example.atlassian.net/wiki",
            "test@example.com",
            "token",
            "TEST"
        )
        publisher.session = mock_session_instance
        
        result = publisher.create_page("Test Page", "# Test Content", "123")
        
        assert result["id"] == "12345"
        assert result["title"] == "Test Page"

    @patch('confluence_publisher.requests.Session')
    def test_get_page_by_title(self, mock_session):
        """Test getting page by title"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "results": [{"id": "12345", "title": "Test Page", "version": {"number": 1}}]
        }
        
        mock_session_instance = MagicMock()
        mock_session_instance.get.return_value = mock_response
        mock_session.return_value = mock_session_instance
        
        publisher = ConfluencePublisher(
            "https://example.atlassian.net/wiki",
            "test@example.com",
            "token",
            "TEST"
        )
        publisher.session = mock_session_instance
        
        result = publisher.get_page_by_title("Test Page")
        
        assert result["id"] == "12345"
        assert result["title"] == "Test Page"

def test_publish_markdown_files():
    """Test publishing markdown files from a directory"""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create test markdown files
        test_file1 = Path(temp_dir) / "test1.md"
        test_file1.write_text("# Test Document 1\n\nContent 1")
        
        test_file2 = Path(temp_dir) / "test2.md"
        test_file2.write_text("# Test Document 2\n\nContent 2")
        
        # Test dry run
        result = publish_markdown_files(
            folder=temp_dir,
            username="test@example.com",
            password="token",
            confluence_base_url="https://example.atlassian.net/wiki",
            space_key="TEST",
            parent_page_id="123",
            dry_run=True
        )
        
        assert len(result) == 2
        assert all("DRY RUN" in page for page in result)

def test_publish_markdown_files_no_files():
    """Test publishing when no markdown files exist"""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a non-markdown file
        test_file = Path(temp_dir) / "test.txt"
        test_file.write_text("Not a markdown file")
        
        result = publish_markdown_files(
            folder=temp_dir,
            username="test@example.com",
            password="token",
            confluence_base_url="https://example.atlassian.net/wiki",
            space_key="TEST",
            parent_page_id="123",
            dry_run=True
        )
        
        assert len(result) == 0

def test_publish_markdown_files_invalid_folder():
    """Test publishing with invalid folder"""
    with pytest.raises(ValueError, match="does not exist"):
        publish_markdown_files(
            folder="/nonexistent/folder",
            username="test@example.com",
            password="token",
            confluence_base_url="https://example.atlassian.net/wiki",
            space_key="TEST",
            parent_page_id="123",
            dry_run=True
        )
