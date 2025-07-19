#!/usr/bin/env python3

import os
import sys
import requests
import json
from main import convert_markdown
from app.models.schemas import MarkdownRequest

def main():
    """GitHub Action entrypoint"""
    
    # Get inputs from environment variables (GitHub Actions sets these)
    markdown_path = os.getenv('INPUT_MARKDOWN_PATH')  # Corrected variable name
    domain = os.getenv('INPUT_CONFLUENCE_DOMAIN')
    username = os.getenv('INPUT_CONFLUENCE_USERNAME')
    api_key = os.getenv('INPUT_CONFLUENCE_API_KEY')
    space = os.getenv('INPUT_CONFLUENCE_SPACE')
    root_page = os.getenv('INPUT_CONFLUENCE_ROOT_PAGE')
    github_token = os.getenv('INPUT_GITHUB_TOKEN')
    
    # GitHub context
    github_workspace = os.getenv('GITHUB_WORKSPACE', '/github/workspace')
    github_repository = os.getenv('GITHUB_REPOSITORY')
    github_ref = os.getenv('GITHUB_REF', 'refs/heads/main')
    
    print(f"🚀 Starting Markdown to Confluence publishing...")
    print(f"📁 Workspace: {github_workspace}")
    print(f"📄 Markdown path: {markdown_path}")
    print(f"🏢 Confluence domain: {domain}")
    print(f"📚 Confluence space: {space}")
    
    # Construct full path to markdown file
    full_markdown_path = os.path.join(github_workspace, markdown_path) # type: ignore
    
    # Validate file exists
    if not os.path.exists(full_markdown_path):
        print(f"❌ Error: Markdown file not found at {full_markdown_path}")
        sys.exit(1)
    
    # Validate required inputs
    if not all([markdown_path, domain, username, api_key, space]):
        print("❌ Error: Missing required inputs")
        sys.exit(1)
    
    # Create request object
    request = MarkdownRequest(
        markdown_path=full_markdown_path,
        domain=domain,
        username=username,
        api_key=api_key,
        space=space,
        root_page=root_page
    )
    
    # Call the conversion function
    try:
        result = convert_markdown(request)
        
        if result.success:
            print(f"✅ {result.message}")
            # Set GitHub Action output (updated syntax)
            github_output = os.getenv('GITHUB_OUTPUT')
            if github_output:
                with open(github_output, 'a') as fh:
                    print(f"status=success", file=fh)
                    print(f"message={result.message}", file=fh)
            sys.exit(0)
        else:
            print(f"❌ {result.message}")
            if result.error:
                print(f"Error details: {result.error}")
            github_output = os.getenv('GITHUB_OUTPUT')
            if github_output:
                with open(github_output, 'a') as fh:
                    print(f"status=failed", file=fh)
                    print(f"message={result.message}", file=fh)
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        github_output = os.getenv('GITHUB_OUTPUT')
        if github_output:
            with open(github_output, 'a') as fh:
                print(f"status=error", file=fh)
                print(f"message=Unexpected error: {str(e)}", file=fh)
        sys.exit(1)

    # Start the FastAPI server in the background
    import subprocess
    server_process = subprocess.Popen(["python", "main.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print("FastAPI server started in the background.")

    # Wait for the server to be ready
    import time
    time.sleep(5)  # Wait for 5 seconds to ensure the server is up

    # Send POST request to the FastAPI server
    try:
        url = "http://0.0.0.0:8000/publish"
        payload = {
            "markdown_path": full_markdown_path,
            "domain": domain,
            "username": username,
            "api_key": api_key,
            "space": space,
            "root_page": root_page
        }
        response = requests.post(url, json=payload)
        print(f"POST request sent to {url}. Response: {response.status_code} - {response.text}")
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to send POST request: {str(e)}")
        server_process.terminate()
        sys.exit(1)

    # Terminate the server process after the request
    server_process.terminate()
    print("FastAPI server terminated.")

if __name__ == "__main__":
    main()
