"""
Unit tests for the MD2Conf service.
"""
import pytest
from unittest.mock import patch, MagicMock
from app.services.md2conf_service import MD2ConfService
from app.models.schemas import MarkdownRequest


class TestMD2ConfService:
    """Test cases for MD2ConfService."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.service = MD2ConfService()
        self.sample_request = MarkdownRequest(
            markdown_path="/path/to/file.md",
            job="md2conf",
            domain="example.atlassian.net",
            username="user@example.com",
            api_key="api_key_123",
            space="TEST"
        )
    
    def test_validate_required_parameters_success(self):
        """Test successful parameter validation."""
        params = self.service.validate_required_parameters(self.sample_request)
        
        assert params["domain"] == "example.atlassian.net"
        assert params["username"] == "user@example.com"
        assert params["api_key"] == "api_key_123"
        assert params["space"] == "TEST"
        assert params["markdown_path"] == "/path/to/file.md"
    
    @patch.dict('os.environ', {}, clear=True)  # Clear environment variables
    def test_validate_required_parameters_missing(self):
        """Test parameter validation with missing required fields."""
        incomplete_request = MarkdownRequest(
            markdown_path="/path/to/file.md",
            job="md2conf",
            domain=None,  # Missing required field
            username=None,  # Missing required field
            api_key=None,  # Missing required field
            space=None  # Missing required field
        )
        
        with pytest.raises(ValueError, match="Missing required parameters"):
            self.service.validate_required_parameters(incomplete_request)
    
    def test_build_md2conf_command(self):
        """Test building the md2conf command."""
        params = {
            "domain": "example.atlassian.net",
            "username": "user@example.com",
            "api_key": "api_key_123",
            "space": "TEST",
            "markdown_path": "/path/to/file.md",
            "root_page": "123456"
        }
        
        cmd = self.service.build_md2conf_command(params)
        
        assert cmd[0:3] == ["python3", "-m", "md2conf"]
        assert "-d" in cmd and "example.atlassian.net" in cmd
        assert "-u" in cmd and "user@example.com" in cmd
        assert "-a" in cmd and "api_key_123" in cmd
        assert "-s" in cmd and "TEST" in cmd
        assert "-r" in cmd and "123456" in cmd
        assert cmd[-1] == "/path/to/file.md"
    
    @patch('subprocess.run')
    def test_publish_markdown_success(self, mock_run):
        """Test successful markdown publishing."""
        # Mock subprocess.run to return success
        mock_run.return_value = MagicMock(
            stdout="Success",
            stderr="",
            returncode=0
        )
        
        response = self.service.publish_markdown(self.sample_request)
        
        assert response.success is True
        assert "Successfully published" in response.message
        assert response.error is None

    def test_job_parameter_validation(self):
        """Test that job parameter is properly handled."""
        # Test with valid job type
        valid_request = MarkdownRequest(
            markdown_path="/path/to/file.md",
            job="md2conf",
            domain="example.atlassian.net",
            username="user@example.com",
            api_key="api_key_123",
            space="TEST"
        )
        
        # This should not raise an error during validation
        params = self.service.validate_required_parameters(valid_request)
        assert params is not None
        
        # Test with no job specified (should default to md2conf behavior)
        no_job_request = MarkdownRequest(
            markdown_path="/path/to/file.md",
            domain="example.atlassian.net",
            username="user@example.com",
            api_key="api_key_123",
            space="TEST"
        )
        
        params = self.service.validate_required_parameters(no_job_request)
        assert params is not None


# Example of how to run tests:
# pip install pytest pytest-mock
# python -m pytest tests/test_md2conf_service.py -v
