from fastapi import FastAPI
from pydantic import BaseModel
import subprocess
import os

# Pydantic models
class MarkdownRequest(BaseModel):
    markdown_path: str
    domain: str = None
    space: str = None
    username: str = None
    api_key: str = None
    root_page: str = None
    github_token: str = None  # For accessing private repos
    repository: str = None    # Format: owner/repo
    ref: str = "main"        # Branch, tag, or commit SHA

class MarkdownResponse(BaseModel):
    success: bool
    message: str
    error: str = None

# Create the FastAPI app
app = FastAPI(title="MD to Confluence Converter")

# Root endpoint
@app.get("/")
def hello_world():
    return {"message": "Hello, World!"}

# Add a health check endpoint
@app.get("/health")
def health_check():
    print("Health check endpoint called.")
    return {"status": "Server is running and healthy."}

# Convert markdown to Confluence format
@app.post("/publish", response_model=MarkdownResponse)
def convert_markdown(request: MarkdownRequest):
    """Convert markdown to Confluence storage format using md2conf"""
    try:
        # Build the md2conf command
        cmd = ["python", "-m", "md2conf"]

        # Get configuration from environment variables or request
        domain = request.domain or os.getenv("CONFLUENCE_DOMAIN")
        username = request.username or os.getenv("CONFLUENCE_USERNAME")
        api_key = request.api_key or os.getenv("CONFLUENCE_API_KEY")
        space = request.space or os.getenv("CONFLUENCE_SPACE")
        root_page = request.root_page or os.getenv("CONFLUENCE_ROOT_PAGE")
        markdown_path = request.markdown_path or os.getenv("GITHUB_MARKDOWN_FILE")

        # Debugging logs for environment variables
        print(f"Domain: {domain}")
        print(f"Username: {'SET' if username else 'NOT SET'}")
        print(f"API Key: {'SET' if api_key else 'NOT SET'}")
        print(f"Space: {space}")
        print(f"Markdown Path: {markdown_path}")
        print(f"Root Page: {root_page}")

        # Validate required parameters
        if not all([domain, username, api_key, space, markdown_path]):
            missing = []
            if not domain: missing.append("domain")
            if not username: missing.append("username")
            if not api_key: missing.append("api_key")
            if not space: missing.append("space")
            if not markdown_path: missing.append("markdown_path")
            return MarkdownResponse(
                success=False,
                message="Missing required parameters",
                error=f"Missing: {', '.join(missing)}"
            )

        # Debugging logs for parameters
        print("Parameters validated successfully.")

        # Add required parameters
        cmd.extend(["-d", domain])
        cmd.extend(["-u", username])
        cmd.extend(["-a", api_key])
        cmd.extend(["-s", space])

        # Add optional parameters
        if root_page:
            cmd.extend(["-r", root_page])
        
        # Add additional options for better integration
        cmd.extend(["--keep-hierarchy"])  # Maintain directory structure
        cmd.extend(["--render-mermaid"])  # Render Mermaid diagrams
        cmd.extend(["--heading-anchors"])  # Add GitHub-style anchors
        
        # Add the markdown path
        cmd.append(markdown_path)
        
        # Debugging logs for publishing process
        print("Starting publishing process...")
        print(f"Command to execute: {' '.join(cmd)}")
        print("Executing md2conf command...")

        # Execute the command
        result = subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=60)

        # Log endpoint call
        print("/publish endpoint called successfully.")

        # Debugging logs for command result
        print("Command executed successfully.")
        print(f"Command output: {result.stdout}")
        print(f"Command errors (if any): {result.stderr}")
        
        return MarkdownResponse(
            success=True,
            message=f"Successfully published {markdown_path} to Confluence",
        )
        
    except subprocess.CalledProcessError as e:
        return MarkdownResponse(
            success=False,
            message="md2conf command failed",
            error=f"Command failed with exit code {e.returncode}: {e.stderr}"
        )
    except Exception as e:
        return MarkdownResponse(
            success=False,
            message="Unexpected error occurred",
            error=str(e)
        )

# Run the app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
