"""
Business logic for md2conf operations.
"""
import subprocess
import os
import platform
import tempfile
import re
import requests
import base64
import shutil
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from app.models.schemas import MarkdownRequest, MarkdownResponse
from app.config import settings


class MD2ConfService:
    """Service class for handling md2conf operations."""
    
    def __init__(self):
        self.timeout = 60
        self.is_windows = platform.system() == "Windows"
        self.temp_dir = None  # Will store temp directory for GitHub downloads
        
    def __del__(self):
        """Clean up any temporary files on destruction."""
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            print(f"Cleaned up temporary directory: {self.temp_dir}")
    
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
    
    def _parse_github_url(self, url: str) -> Tuple[str, str, str]:
        """
        Parse a GitHub URL to extract repo, path, and ref.
        Owner is hardcoded to "vertexinc".
        
        Handles formats like:
        - https://github.com/vertexinc/repo/blob/branch/path/to/file.md
        - https://github.com/vertexinc/repo/tree/branch/path/to/directory
        - https://raw.githubusercontent.com/vertexinc/repo/branch/path/to/file.md
        - repo/path/to/file.md (assumes main branch)
        
        Returns:
            Tuple containing (repo, path, ref)
        """
        print(f"Parsing GitHub URL: {url}")
        
        # Handle simple repo/path format (no http prefix)
        if not url.startswith(("http://", "https://", "github.com", "raw.githubusercontent.com")):
            parts = url.strip("/").split("/")
            if len(parts) < 2:
                raise ValueError(f"Invalid GitHub path format: {url}. Expected format: repo/path/to/file.md")
            return parts[0], "/".join(parts[1:]), "main"
            
        # Handle raw.githubusercontent.com URLs
        if "raw.githubusercontent.com" in url:
            # Format: https://raw.githubusercontent.com/vertexinc/repo/branch/path/to/file.md
            raw_pattern = r"https?://raw\.githubusercontent\.com/vertexinc/([^/]+)/([^/]+)/(.+)"
            match = re.match(raw_pattern, url)
            
            if match:
                repo, ref, path = match.groups()
                return repo, path, ref
                
        # Handle github.com URLs with blob or tree
        # Extract components from URL
        github_pattern = r"https?://(?:www\.)?github\.com/vertexinc/([^/]+)/(?:blob|tree)/([^/]+)/(.+)"
        match = re.match(github_pattern, url)
        
        if match:
            repo, ref, path = match.groups()
            return repo, path, ref
            
        # Handle github.com URLs without blob or tree (assume main branch and empty path)
        simple_pattern = r"https?://(?:www\.)?github\.com/vertexinc/([^/]+)/?$"
        match = re.match(simple_pattern, url)
        
        if match:
            repo = match.group(1)
            return repo, "", "main"
            
        # If we reach here, none of our patterns matched
        raise ValueError(
            f"Invalid GitHub URL: {url}. Expected formats:\n"
            "- https://github.com/vertexinc/repo/blob/branch/path/to/file.md\n"
            "- https://raw.githubusercontent.com/vertexinc/repo/branch/path/to/file.md\n"
            "- repo/path/to/file.md"
        )
    
    def _download_github_file(self, repo: str, path: str, ref: str, token: Optional[str] = None) -> str:
        """
        Download a file from GitHub repository using raw content URL.
        Owner is hardcoded to "vertexinc".
        
        Args:
            repo: GitHub repository name
            path: Path to the file within the repository
            ref: Branch, tag, or commit SHA
            token: GitHub Personal Access Token for private repositories
            
        Returns:
            Path to the downloaded file
        """
        print(f"Downloading file from GitHub: vertexinc/{repo}/{path} (ref: {ref})")
        
        # Create temp directory if not exists
        if not self.temp_dir:
            self.temp_dir = tempfile.mkdtemp(prefix="md2conf_")
            print(f"Created temporary directory: {self.temp_dir}")
        
        # We'll try two approaches:
        # 1. First try the raw content URL (more efficient for larger files)
        # 2. If that fails, fall back to the GitHub API (which can provide more error details)
        
        # Setup headers for all requests
        headers = {
            "Accept": "application/vnd.github.v3.raw, application/vnd.github.v3+json;q=0.9",
            "User-Agent": "MD2ConfService/1.0"
        }
        
        if token:
            headers["Authorization"] = f"token {token}"
            
        # Try the raw content URL first (more efficient for larger files)
        # Hardcode owner to "vertexinc"
        raw_url = f"https://raw.githubusercontent.com/vertexinc/{repo}/{ref}/{path}"
        print(f"Attempting to download from raw URL: {raw_url}")
        
        try:
            response = requests.get(raw_url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                # Success with raw URL
                file_content = response.text
                
                # Save to temporary file
                local_file_path = os.path.join(self.temp_dir, os.path.basename(path))
                with open(local_file_path, "w", encoding="utf-8") as f:
                    f.write(file_content)
                
                print(f"Successfully downloaded file from raw URL to: {local_file_path}")
                return local_file_path
                
            elif response.status_code == 404:
                print("File not found with raw URL, trying GitHub API...")
            else:
                print(f"Raw URL request failed with status {response.status_code}, trying GitHub API...")
                
        except requests.RequestException as e:
            print(f"Error accessing raw URL: {str(e)}")
            print("Falling back to GitHub API...")
        
        # Fall back to GitHub API
        # Hardcode owner to "vertexinc"
        api_url = f"https://api.github.com/repos/vertexinc/{repo}/contents/{path}?ref={ref}"
        print(f"Requesting file from GitHub API: {api_url}")
        
        try:
            response = requests.get(api_url, headers=headers, timeout=30)
            
            if response.status_code != 200:
                # Get error details from response
                try:
                    error_info = response.json() if response.headers.get("Content-Type", "").startswith("application/json") else response.text
                except ValueError:
                    error_info = response.text
                
                error_message = f"Failed to download GitHub file. Status: {response.status_code}"
                
                # Add common error interpretations
                if response.status_code == 401:
                    error_message += ". Authentication failed. Check your GitHub token."
                elif response.status_code == 403:
                    rate_limit_remaining = response.headers.get("X-RateLimit-Remaining")
                    if rate_limit_remaining == "0":
                        reset_time = response.headers.get("X-RateLimit-Reset")
                        error_message += f". GitHub API rate limit exceeded. Reset at: {reset_time}"
                    else:
                        error_message += ". Permission denied. Ensure your token has necessary permissions."
                elif response.status_code == 404:
                    error_message += f". File not found. Verify the repository, path, and branch/ref exist."
                
                error_message += f" Details: {error_info}"
                raise ValueError(error_message)
            
            # Parse the response
            content_data = response.json()
            
            if content_data.get("type") != "file":
                raise ValueError(f"The GitHub path does not point to a file: {path}")
            
            # Decode content (base64-encoded in the API response)
            file_content = base64.b64decode(content_data.get("content", "")).decode("utf-8")
            
            # Save to temporary file
            local_file_path = os.path.join(self.temp_dir, os.path.basename(path))
            with open(local_file_path, "w", encoding="utf-8") as f:
                f.write(file_content)
            
            print(f"Downloaded and saved file to: {local_file_path}")
            return local_file_path
            
        except requests.RequestException as e:
            raise ValueError(f"Network error accessing GitHub API: {str(e)}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON response from GitHub API: {str(e)}")
        except Exception as e:
            raise ValueError(f"Unexpected error downloading GitHub file: {str(e)}")
    
    def _process_github_markdown_path(self, markdown_path: str, github_token: Optional[str] = None, 
                                      repository: Optional[str] = None, ref: str = "main") -> str:
        """
        Process markdown path which could be a GitHub URL or repository reference.
        
        Args:
            markdown_path: Local path or GitHub URL
            github_token: GitHub Personal Access Token (from environment variables only)
            repository: Repository in format "owner/repo"
            ref: Branch, tag, or commit SHA
            
        Returns:
            Local path to the markdown file
        """
        # If we already have a local file path that exists, use it directly
        if os.path.isfile(markdown_path):
            print(f"Using existing local file: {markdown_path}")
            return markdown_path
            
        # Check if it's a GitHub URL (multiple formats)
        if any(markdown_path.startswith(prefix) for prefix in [
            "http://github.com", 
            "https://github.com", 
            "github.com", 
            "http://raw.githubusercontent.com", 
            "https://raw.githubusercontent.com"
        ]):
            print(f"Processing GitHub URL: {markdown_path}")
            try:
                repo, path, url_ref = self._parse_github_url(markdown_path)
                # Use URL ref if provided, otherwise fall back to the passed ref
                actual_ref = url_ref or ref
                return self._download_github_file(repo, path, actual_ref, github_token)
            except Exception as e:
                print(f"Error parsing GitHub URL: {str(e)}")
                raise ValueError(f"Failed to process GitHub URL: {markdown_path}. Error: {str(e)}")
        
        # Check if it's a repository + path reference
        elif repository:
            print(f"Processing repository reference: {repository} with path: {markdown_path}")
            try:
                # Since owner is hardcoded to "vertexinc", we only need the repo name
                if "/" in repository:
                    # If format is "vertexinc/repo", extract just the repo part
                    owner_part, repo = repository.split("/", 1)
                    if owner_part != "vertexinc":
                        print(f"Warning: Owner '{owner_part}' will be ignored. Using hardcoded 'vertexinc'.")
                else:
                    # If just repo name provided, use it directly
                    repo = repository
                
                return self._download_github_file(repo, markdown_path, ref, github_token)
            except Exception as e:
                print(f"Error processing repository reference: {str(e)}")
                raise ValueError(f"Failed to process GitHub repository: {repository}. Error: {str(e)}")
        
        # Last resort: Check if the path exists locally
        if os.path.exists(markdown_path):
            print(f"Using local file: {markdown_path}")
            return markdown_path
        else:
            print(f"Warning: File not found locally: {markdown_path}")
            # We'll still return the path and let the command execution fail if needed
            return markdown_path
    
    def validate_required_parameters(self, request: MarkdownRequest) -> Dict[str, Any]:
        """Validate and extract required parameters from request."""
        try:
            # Get configuration from environment variables or request
            domain = request.domain or os.getenv("CONFLUENCE_DOMAIN")
            username = request.username or os.getenv("CONFLUENCE_USERNAME")
            api_key = request.api_key or os.getenv("CONFLUENCE_API_KEY")
            space = request.space or os.getenv("CONFLUENCE_SPACE")
            root_page = request.root_page or os.getenv("CONFLUENCE_ROOT_PAGE")
            markdown_path = request.markdown_path or os.getenv("GITHUB_MARKDOWN_FILE")
            github_token = settings.github_token or os.getenv("GITHUB_TOKEN") or os.getenv("gh_token")
            repository = request.repository or os.getenv("GITHUB_REPOSITORY")
            ref = request.ref or os.getenv("GITHUB_REF", "main")
            
            # Process GitHub path if needed
            if markdown_path and (
                repository or 
                any(markdown_path.startswith(prefix) for prefix in [
                    "http://github.com", 
                    "https://github.com", 
                    "github.com", 
                    "http://raw.githubusercontent.com", 
                    "https://raw.githubusercontent.com"
                ])
            ):
                print(f"Detected GitHub reference - will download file")
                try:
                    markdown_path = self._process_github_markdown_path(
                        markdown_path=markdown_path,
                        github_token=github_token,
                        repository=repository,
                        ref=ref
                    )
                except Exception as e:
                    error_message = f"Failed to process GitHub markdown path: {str(e)}"
                    print(f"Error: {error_message}")
                    raise ValueError(error_message)
            
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
            
            # Verify the markdown file exists if it's a local path
            if not os.path.isfile(markdown_path):
                print(f"Warning: Markdown file not found at: {markdown_path}")
                # We don't raise an error here as the path might be resolved differently during command execution
            
            return {
                "domain": domain,
                "username": username,
                "api_key": api_key,
                "space": space,
                "root_page": root_page,
                "markdown_path": markdown_path,
                "github_token": github_token,
                "repository": repository,
                "ref": ref
            }
        except Exception as e:
            if not isinstance(e, ValueError):
                # Wrap non-ValueError exceptions
                raise ValueError(f"Parameter validation error: {str(e)}")
            raise
    
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
        
        # Add the markdown path (which may have been downloaded from GitHub)
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
        
        # Add Chrome/Puppeteer environment variables for Docker containers
        env.update({
            "TMPDIR": "/tmp/puppeteer",
            "PUPPETEER_CACHE_DIR": "/app/.puppeteer_cache",
            "PUPPETEER_TMP_DIR": "/tmp/puppeteer",
            "CHROME_NO_SANDBOX": "1",
            "PUPPETEER_EXECUTABLE_PATH": "/usr/bin/google-chrome",
            "PUPPETEER_SKIP_CHROMIUM_DOWNLOAD": "true",
            "PUPPETEER_ARGS": "--no-sandbox --disable-setuid-sandbox --disable-dev-shm-usage --disable-gpu --no-first-run --no-zygote --single-process",
            "CHROME_DEVEL_SANDBOX": "/usr/bin/google-chrome"
        })
        
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
            print(f"GitHub Token: {'SET' if params.get('github_token') else 'NOT SET'}")
            print(f"GitHub Repository: {params.get('repository', 'NOT SET')}")
            print(f"GitHub Ref: {params.get('ref', 'main')}")
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
