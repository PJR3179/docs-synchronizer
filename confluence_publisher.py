import os
import sys
import logging
from pathlib import Path
from typing import List, Dict, Any
import requests
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConfluencePublisher:
    """
    Simplified Confluence publisher using the Confluence REST API
    """
    
    def __init__(self, confluence_url: str, username: str, api_token: str, space_key: str):
        self.confluence_url = confluence_url.rstrip('/')
        self.username = username
        self.api_token = api_token
        self.space_key = space_key
        self.session = requests.Session()
        self.session.auth = (username, api_token)
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def convert_markdown_to_confluence(self, markdown_content: str) -> str:
        """
        Convert markdown to Confluence storage format
        This is a basic implementation - you might want to use a proper markdown parser
        """
        # Basic markdown to Confluence conversion
        # In a real implementation, you'd use a proper markdown parser
        content = markdown_content
        
        # Convert headers
        content = content.replace('# ', '<h1>').replace('\n# ', '</h1>\n<h1>')
        content = content.replace('## ', '<h2>').replace('\n## ', '</h2>\n<h2>')
        content = content.replace('### ', '<h3>').replace('\n### ', '</h3>\n<h3>')
        
        # Convert bold and italic
        content = content.replace('**', '<strong>').replace('**', '</strong>')
        content = content.replace('*', '<em>').replace('*', '</em>')
        
        # Convert code blocks
        content = content.replace('```', '<ac:structured-macro ac:name="code"><ac:plain-text-body><![CDATA[')
        content = content.replace('```', ']]></ac:plain-text-body></ac:structured-macro>')
        
        # Wrap in paragraph tags
        paragraphs = content.split('\n\n')
        formatted_paragraphs = []
        for para in paragraphs:
            if para.strip() and not para.startswith('<h') and not para.startswith('<ac:'):
                formatted_paragraphs.append(f'<p>{para.strip()}</p>')
            else:
                formatted_paragraphs.append(para)
        
        return '\n'.join(formatted_paragraphs)
    
    def create_page(self, title: str, content: str, parent_id: str) -> Dict[str, Any]:
        """
        Create a new Confluence page
        """
        confluence_content = self.convert_markdown_to_confluence(content)
        
        page_data = {
            "type": "page",
            "title": title,
            "space": {"key": self.space_key},
            "body": {
                "storage": {
                    "value": confluence_content,
                    "representation": "storage"
                }
            },
            "ancestors": [{"id": parent_id}]
        }
        
        response = self.session.post(
            f"{self.confluence_url}/rest/api/content",
            data=json.dumps(page_data)
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Failed to create page: {response.status_code} - {response.text}")
            response.raise_for_status()
    
    def update_page(self, page_id: str, title: str, content: str, version: int) -> Dict[str, Any]:
        """
        Update an existing Confluence page
        """
        confluence_content = self.convert_markdown_to_confluence(content)
        
        page_data = {
            "version": {"number": version + 1},
            "title": title,
            "type": "page",
            "body": {
                "storage": {
                    "value": confluence_content,
                    "representation": "storage"
                }
            }
        }
        
        response = self.session.put(
            f"{self.confluence_url}/rest/api/content/{page_id}",
            data=json.dumps(page_data)
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Failed to update page: {response.status_code} - {response.text}")
            response.raise_for_status()
    
    def get_page_by_title(self, title: str) -> Dict[str, Any]:
        """
        Get a page by title in the space
        """
        response = self.session.get(
            f"{self.confluence_url}/rest/api/content",
            params={
                "spaceKey": self.space_key,
                "title": title,
                "expand": "version"
            }
        )
        
        if response.status_code == 200:
            results = response.json()
            if results["results"]:
                return results["results"][0]
        return None
    
    def publish_page(self, title: str, content: str, parent_id: str) -> Dict[str, Any]:
        """
        Publish a page (create or update if exists)
        """
        existing_page = self.get_page_by_title(title)
        
        if existing_page:
            logger.info(f"Updating existing page: {title}")
            return self.update_page(
                existing_page["id"],
                title,
                content,
                existing_page["version"]["number"]
            )
        else:
            logger.info(f"Creating new page: {title}")
            return self.create_page(title, content, parent_id)

def publish_markdown_files(
    folder: str,
    username: str,
    password: str,
    confluence_base_url: str,
    space_key: str,
    parent_page_id: str,
    dry_run: bool = False
) -> List[str]:
    """
    Publish all markdown files in a folder to Confluence
    """
    folder_path = Path(folder)
    if not folder_path.exists():
        raise ValueError(f"Folder {folder} does not exist")
    
    publisher = ConfluencePublisher(confluence_base_url, username, password, space_key)
    published_pages = []
    
    # Find all markdown files recursively
    markdown_files = list(folder_path.rglob("*.md"))
    
    if not markdown_files:
        logger.info("No markdown files found in the specified folder")
        return []
    
    logger.info(f"Found {len(markdown_files)} markdown files to publish")
    
    for md_file in markdown_files:
        try:
            # Read markdown content
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Generate page title from filename
            page_title = md_file.stem.replace('-', ' ').replace('_', ' ').title()
            
            if not dry_run:
                # Publish to Confluence
                page_info = publisher.publish_page(
                    title=page_title,
                    content=content,
                    parent_id=parent_page_id
                )
                published_pages.append(f"{page_title} (ID: {page_info.get('id', 'unknown')})")
                logger.info(f"Published: {page_title}")
            else:
                published_pages.append(f"{page_title} (DRY RUN)")
                logger.info(f"Dry run: {page_title}")
                
        except Exception as e:
            logger.error(f"Failed to publish {md_file}: {str(e)}")
            continue
    
    return published_pages

def main():
    """
    Main function for command line usage
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="Publish markdown files to Confluence")
    parser.add_argument("--folder", required=True, help="Folder containing markdown files")
    parser.add_argument("--username", required=True, help="Confluence username/email")
    parser.add_argument("--password", required=True, help="Confluence API token")
    parser.add_argument("--confluence-base-url", required=True, help="Confluence base URL")
    parser.add_argument("--space-key", required=True, help="Confluence space key")
    parser.add_argument("--parent-page-id", required=True, help="Parent page ID")
    parser.add_argument("--dry-run", action="store_true", help="Dry run mode")
    
    args = parser.parse_args()
    
    try:
        published_pages = publish_markdown_files(
            folder=args.folder,
            username=args.username,
            password=args.password,
            confluence_base_url=args.confluence_base_url,
            space_key=args.space_key,
            parent_page_id=args.parent_page_id,
            dry_run=args.dry_run
        )
        
        print(f"Successfully processed {len(published_pages)} pages:")
        for page in published_pages:
            print(f"  - {page}")
            
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
