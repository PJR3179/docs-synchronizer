"""
Business logic for md2conf operations.
"""
import subprocess
import os
import platform
from pathlib import Path
from typing import Dict, List, Any
from app.models.schemas import MarkdownRequest, MarkdownResponse


class MD2ConfService:
    """Service class for handling md2conf operations."""
    
    def __init__(self):
        self.timeout = 60
        self.is_windows = platform.system() == "Windows"
        
    def _get_node_paths(self) -> tuple[str, str]:
        """Get Node.js and npm paths based on the operating system."""
        if self.is_windows:
            # Windows paths
            nodejs_bin_path = r"C:\Program Files\nodejs"
            npm_bin_path = str(Path.home() / "AppData" / "Roaming" / "npm")
        else:
            # Linux/macOS paths
            nodejs_bin_path = "/usr/bin"  # Common system path
            npm_bin_path = str(Path.home() / ".npm-global" / "bin")
            
            # Also check common alternative paths
            alternative_paths = [
                "/usr/local/bin",
                str(Path.home() / "node_modules" / ".bin"),
                str(Path.home() / ".local" / "bin"),
                "/opt/nodejs/bin"
            ]
            
            # Use the first existing path or default
            for alt_path in alternative_paths:
                if Path(alt_path).exists():
                    nodejs_bin_path = alt_path
                    break
        
        return nodejs_bin_path, npm_bin_path
    
    def validate_required_parameters(self, request: MarkdownRequest) -> Dict[str, Any]:
        """Validate and extract required parameters from request."""
        # Get configuration from environment variables or request
        domain = request.domain or os.getenv("CONFLUENCE_DOMAIN")
        username = request.username or os.getenv("CONFLUENCE_USERNAME")
        api_key = request.api_key or os.getenv("CONFLUENCE_API_KEY")
        space = request.space or os.getenv("CONFLUENCE_SPACE")
        root_page = request.root_page or os.getenv("CONFLUENCE_ROOT_PAGE")
        markdown_path = request.markdown_path or os.getenv("GITHUB_MARKDOWN_FILE")
        
        # Validate required parameters
        required_params = {
            "domain": domain,
            "username": username,
            "api_key": api_key,
            "space": space,
            "markdown_path": markdown_path
        }
        
        missing = [key for key, value in required_params.items() if not value]
        if missing:
            raise ValueError(f"Missing required parameters: {', '.join(missing)}")
        
        return {
            "domain": domain,
            "username": username,
            "api_key": api_key,
            "space": space,
            "root_page": root_page,
            "markdown_path": markdown_path
        }
    
    def build_md2conf_command(self, params: Dict[str, str]) -> List[str]:
        """Build the md2conf command with all necessary parameters."""
        cmd = ["python3", "-m", "md2conf"]
        
        # Add required parameters
        cmd.extend(["-d", params["domain"]])
        cmd.extend(["-u", params["username"]])
        cmd.extend(["-a", params["api_key"]])
        cmd.extend(["-s", params["space"]])
        
        # Add optional parameters
        if params.get("root_page"):
            cmd.extend(["-r", params["root_page"]])
        
        # Add additional options for better integration
        cmd.extend(["--keep-hierarchy"])  # Maintain directory structure
        cmd.extend(["--render-mermaid"])  # Render Mermaid diagrams
        cmd.extend(["--heading-anchors"])  # Add GitHub-style anchors
        
        # Add the markdown path
        cmd.append(params["markdown_path"])
        
        return cmd
    
    def execute_md2conf_command(self, cmd: List[str]) -> subprocess.CompletedProcess:
        """Execute the md2conf command and return the result."""
        print("Starting publishing process...")
        print(f"Command to execute: {' '.join(cmd)}")
        print("Executing md2conf command...")
        
        # Prepare environment with npm bin directory and Node.js in PATH for mermaid-cli
        env = os.environ.copy()
        nodejs_bin_path, npm_bin_path = self._get_node_paths()
        
        current_path = env.get("PATH", "")
        paths_to_add = []
        
        # Check if paths need to be added
        if npm_bin_path not in current_path:
            paths_to_add.append(npm_bin_path)
        if nodejs_bin_path not in current_path:
            paths_to_add.append(nodejs_bin_path)
            
        if paths_to_add:
            # Use appropriate path separator for the OS
            path_separator = ";" if self.is_windows else ":"
            env["PATH"] = path_separator.join(paths_to_add) + path_separator + current_path
        
        print(f"Updated PATH for Node.js/npm: {env['PATH'][:200]}...")  # Log first 200 chars
        
        try:
            result = subprocess.run(
                cmd, 
                check=True, 
                capture_output=True, 
                text=True, 
                timeout=self.timeout,
                env=env
            )
            return result
        except subprocess.CalledProcessError as e:
            print("❌ md2conf command failed.")
            print(f"Exit code: {e.returncode}")
            print(f"Error output: {e.stderr}")
            raise
        except Exception as e:
            print("❌ Unexpected error during md2conf execution.")
            print(f"Error: {str(e)}")
            raise
    
    def publish_markdown(self, request: MarkdownRequest) -> MarkdownResponse:
        """Main method to publish markdown to Confluence."""
        try:
            # Validate parameters
            params = self.validate_required_parameters(request)
            
            # Log parameters (safely)
            print(f"Domain: {params['domain']}")
            print(f"Username: {'SET' if params['username'] else 'NOT SET'}")
            print(f"API Key: {'SET' if params['api_key'] else 'NOT SET'}")
            print(f"Space: {params['space']}")
            print(f"Markdown Path: {params['markdown_path']}")
            print(f"Root Page: {params.get('root_page', 'NOT SET')}")
            print("Parameters validated successfully.")
            
            # Build and execute command
            cmd = self.build_md2conf_command(params)
            result = self.execute_md2conf_command(cmd)
            
            # Log success
            print("/publish endpoint called successfully.")
            print("Command executed successfully.")
            print(f"Command output: {result.stdout}")
            print(f"Command errors (if any): {result.stderr}")
            
            return MarkdownResponse(
                success=True,
                message=f"Successfully published {params['markdown_path']} to Confluence"
            )
            
        except ValueError as e:
            # Parameter validation errors
            return MarkdownResponse(
                success=False,
                message="Missing required parameters",
                error=str(e)
            )
        except subprocess.CalledProcessError as e:
            # md2conf command errors
            return MarkdownResponse(
                success=False,
                message="md2conf command failed.",
                error=f"Exit code: {e.returncode}, Error: {e.stderr}"
            )
        except Exception as e:
            # Unexpected errors
            return MarkdownResponse(
                success=False,
                message="Unexpected error occurred",
                error=str(e)
            )
