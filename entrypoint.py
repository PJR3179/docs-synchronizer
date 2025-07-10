#!/usr/bin/env python3

import os
import sys
import requests
import json
from main import convert_markdown, MarkdownRequest

def main():
    """GitHub Action entrypoint"""
    
    # Get inputs from environment variables (GitHub Actions sets these)
    markdown_path = os.getenv('INPUT_MARKDOWN-PATH')
    domain = os.getenv('INPUT_CONFLUENCE-DOMAIN')
    username = os.getenv('INPUT_CONFLUENCE-USERNAME')
    api_key = os.getenv('INPUT_CONFLUENCE-API-KEY')
    space = os.getenv('INPUT_CONFLUENCE-SPACE')
    root_page = os.getenv('INPUT_CONFLUENCE-ROOT-PAGE')
    github_token = os.getenv('INPUT_GITHUB-TOKEN')
    
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
    full_markdown_path = os.path.join(github_workspace, markdown_path)
    
    # Validate file exists
    if not os.path.exists(full_markdown_path):
        print(f"❌ Error: Markdown file not found at {full_markdown_path}")
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
            # Set GitHub Action output
            print(f"::set-output name=status::success")
            print(f"::set-output name=message::{result.message}")
            sys.exit(0)
        else:
            print(f"❌ {result.message}")
            if result.error:
                print(f"Error details: {result.error}")
            print(f"::set-output name=status::failed")
            print(f"::set-output name=message::{result.message}")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        print(f"::set-output name=status::error")
        print(f"::set-output name=message::Unexpected error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
