# GitHub Markdown Integration

This document explains how to use the GitHub integration features to fetch markdown files from private repositories.

## Usage Examples

### 1. Using a GitHub URL

You can directly provide a GitHub URL to a markdown file:

```bash
curl -X POST http://localhost:8000/publish \
  -H "Content-Type: application/json" \
  -d '{
    "markdown_path": "https://github.com/your-org/your-repo/blob/main/docs/example.md",
    "domain": "your-domain.atlassian.net",
    "username": "your-email@company.com",
    "api_key": "your-api-key",
    "space": "YOUR-SPACE",
    "github_token": "ghp_your_github_personal_access_token"
  }'
```

### 2. Using Repository and Path

You can specify a repository and a path within that repository:

```bash
curl -X POST http://localhost:8000/publish \
  -H "Content-Type: application/json" \
  -d '{
    "repository": "your-org/your-repo",
    "markdown_path": "docs/example.md",
    "ref": "main",
    "domain": "your-domain.atlassian.net",
    "username": "your-email@company.com",
    "api_key": "your-api-key",
    "space": "YOUR-SPACE",
    "github_token": "ghp_your_github_personal_access_token"
  }'
```

### 3. Using Environment Variables

You can also set GitHub credentials as environment variables:

```bash
export GITHUB_TOKEN="ghp_your_github_personal_access_token"
export GITHUB_REPOSITORY="your-org/your-repo"

curl -X POST http://localhost:8000/publish \
  -H "Content-Type: application/json" \
  -d '{
    "markdown_path": "docs/example.md",
    "domain": "your-domain.atlassian.net",
    "username": "your-email@company.com",
    "api_key": "your-api-key",
    "space": "YOUR-SPACE"
  }'
```

## GitHub Personal Access Token

For private repositories, you need to provide a GitHub Personal Access Token (PAT) with the following permissions:

- `repo` scope for full private repository access

You can create a PAT in your GitHub account settings:
1. Go to Settings > Developer settings > Personal access tokens
2. Generate a new token with appropriate permissions
3. Use this token in your API requests or set it as an environment variable

## Specifying a Branch, Tag or Commit

You can specify a branch, tag, or commit SHA using the `ref` parameter:

```json
{
  "repository": "your-org/your-repo",
  "markdown_path": "docs/example.md",
  "ref": "develop",  // Branch name
  "github_token": "your-token"
}
```

If not specified, the default branch (`main`) will be used.

## Temporary File Handling

The system will:
1. Download the file from GitHub to a temporary location
2. Process the file with md2conf
3. Automatically clean up temporary files after processing

## Troubleshooting

If you encounter issues:

1. Check that your GitHub token has the correct permissions
2. Verify the path to the markdown file is correct
3. Ensure the file exists in the specified branch or commit
4. Check the API logs for detailed error messages
