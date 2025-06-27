# Docs as Code - Confluence (FastAPI)

Publish a folder or subfolder of documentation to Confluence using FastAPI and Python.

Create a Confluence Page for each markdown file. Each folder will create a _parent_ page to reflect
the directory structure.

This workflow is adapted for vertexinc's needs and now uses FastAPI with Python instead of Node.js.

## Things to Know

- When linking to sections within your markdown files (e.g., `#overview`), use the full GitHub URL. Otherwise, these links will not work correctly after publishing to Confluence. You can manually adjust Confluence hyperlinks after publishing if needed.
- Automatically published docs are not deleted from Confluence.
- Confluence may restrict the width of text in auto-published tables. You may need to manually resize columns to suit your team's preferences.

## API Endpoints

### FastAPI Web Service

The application provides a FastAPI web service with the following endpoints:

- `GET /` - Health check
- `GET /health` - Health status
- `POST /publish` - Publish markdown files to Confluence

### Publish Request Body

```json
{
  "folder": "path/to/docs",
  "username": "your-email@domain.com",
  "password": "your-api-token",
  "confluence_base_url": "https://mydomain.atlassian.net/wiki",
  "space_key": "MYSPACE",
  "parent_page_id": "123456789",
  "dry_run": false
}
```

## GitHub Action Parameters

| Name                  | Description | Required |
|-----------------------| --- | --- |
| `folder`              | The folder to sync | true |
| `username`            | Confluence username or email | true |
| `password`            | Confluence password or [API token](https://support.atlassian.com/atlassian-account/docs/manage-api-tokens-for-your-atlassian-account/) | true |
| `confluence-base-url` | Your Confluence URL (with `wiki`). Example: `https://mydomain.atlassian.net/wiki` | true |
| `space-key`           | Confluence space key to publish the documentation. Located after `spaces` in the URL. `https://mydomain.atlassian.net/wiki/spaces/<<~1234>>`. <br> Or in _Space settings_ > _Space details_ > _Key_. | true |
| `parent-page-id`      | Page id under which the documentation will be published. Located after `pages` in the URL. `https://mydomain.atlassian.net/wiki/spaces/~1234/pages/<<1234>>/My+Parent+Page` | true |
| `dry-run`             | Run in dry-run mode (don't actually publish) | false |

## Example GitHub Workflow

```yml
name: Sync Docs as Code - Confluence
on:
  push:
    branches:
      - main
    paths:
      - 'docs/**'
jobs:
  docs-as-code:
    runs-on: ubuntu-latest
    name: Sync Docs as Code - Confluence
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      - name: Sync Docs as Code - Confluence
        uses: PJR3179/docs-as-code-confluence@v4
        with:
          folder: 'docs/information_tables'
          username: ${{ secrets.USERNAME }}
          password: ${{ secrets.API_TOKEN }}
          confluence-base-url: https://mydomain.atlassian.net/wiki
          space-key: ~1234
          parent-page-id: 123456789
          dry-run: false
```

## Running Locally

### Command Line Usage

```bash
python confluence_publisher.py \
  --folder "docs/" \
  --username "your-email@domain.com" \
  --password "your-api-token" \
  --confluence-base-url "https://mydomain.atlassian.net/wiki" \
  --space-key "MYSPACE" \
  --parent-page-id "123456789" \
  --dry-run
```

### FastAPI Web Service

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the FastAPI server:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

3. Access the API documentation at `http://localhost:8000/docs`

### Docker

1. Build the Docker image:
```bash
docker build -t docs-as-code-confluence .
```

2. Run the container:
```bash
docker run -p 8000:8000 docs-as-code-confluence
```

## Testing

```bash
pip install pytest pytest-asyncio httpx
python -m pytest tests/
```

## Development

### Project Structure

```
├── main.py                 # FastAPI application
├── confluence_publisher.py # Core Confluence publishing logic
├── requirements.txt        # Python dependencies
├── action.yml             # GitHub Action definition
├── Dockerfile             # Docker container configuration
├── tests/                 # Test files
└── README.md              # This file
```

### Environment Variables

For local development, you can set these environment variables:

- `PORT`: Port for the FastAPI server (default: 8000)

## Alternatives

* [markdown-confluence/publish-action](https://github.com/markdown-confluence/publish-action)
* [mbovo/mark2confluence](https://github.com/mbovo/mark2confluence)
* [markdown-to-confluence PyPI package](https://pypi.org/project/markdown-to-confluence/)
