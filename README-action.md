# Markdown to Confluence Publisher

A GitHub Action that automatically publishes markdown files to Confluence using the `md2conf` tool.

## Usage

```yaml
name: Publish to Confluence
on:
  push:
    branches: [ main ]
    paths: [ 'docs/**' ]

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Publish to Confluence
        uses: your-username/markdown-to-confluence-action@v1
        with:
          markdown-path: 'README.md'
          confluence-domain: 'mycompany.atlassian.net'
          confluence-username: 'user@company.com'
          confluence-api-key: ${{ secrets.CONFLUENCE_API_KEY }}
          confluence-space: 'DOCS'
          confluence-root-page: '123456789'
```

## Inputs

| Input | Description | Required |
|-------|-------------|----------|
| `markdown-path` | Path to markdown file or directory | Yes |
| `confluence-domain` | Confluence domain | Yes |
| `confluence-username` | Confluence username | Yes |
| `confluence-api-key` | Confluence API key | Yes |
| `confluence-space` | Confluence space key | Yes |
| `confluence-root-page` | Root page ID (optional) | No |

## Secrets

Store sensitive information in GitHub Secrets:
- `CONFLUENCE_API_KEY`: Your Confluence API key
- `CONFLUENCE_USERNAME`: Your Confluence username (optional)
