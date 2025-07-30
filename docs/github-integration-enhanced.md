# Enhanced GitHub Markdown Integration

This document explains how to use the enhanced GitHub integration features to fetch markdown files from private repositories.

## Usage Examples

### 1. Using a GitHub URL

You can directly provide a GitHub URL to a markdown file in several formats:

```bash
# Standard GitHub URL
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

# Raw GitHub URL
curl -X POST http://localhost:8000/publish \
  -H "Content-Type: application/json" \
  -d '{
    "markdown_path": "https://raw.githubusercontent.com/your-org/your-repo/main/docs/example.md",
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

## How It Works

The system uses two methods to download files from GitHub:

1. **Raw Content URL** (primary method):
   - Uses `https://raw.githubusercontent.com/owner/repo/ref/path` format
   - More efficient for larger files
   - No base64 encoding/decoding overhead

2. **GitHub API** (fallback method):
   - Uses the GitHub API at `https://api.github.com/repos/owner/repo/contents/path`
   - Provides more detailed error messages
   - Limited to files under 1MB in size

The system automatically tries the most efficient method first and falls back to alternatives if needed.

## Temporary File Handling

The system will:
1. Download the file from GitHub to a temporary location
2. Process the file with md2conf
3. Automatically clean up temporary files after processing

## Troubleshooting

If you encounter issues:

1. **Authentication Issues**:
   - Ensure your GitHub token is valid and not expired
   - Check that your token has the correct permissions (repo scope)
   - For organizations with SSO, ensure your token has SSO enabled

2. **File Not Found**:
   - Verify the path is correct (case-sensitive)
   - Check that the branch, tag, or commit exists
   - Ensure the file exists at the specified location

3. **Rate Limiting**:
   - GitHub API has rate limits that may be reached
   - Using a token increases your rate limit
   - The system will show when the rate limit resets

4. **Large Files**:
   - Files over 1MB may not work with the GitHub API method
   - The system automatically tries the raw URL method first which supports larger files
