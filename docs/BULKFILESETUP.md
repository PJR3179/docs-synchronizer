# Bulk Document Publishing Setup Guide

This guide will help you set up automated bulk publishing of markdown documents to Confluence using GitHub Actions and matrix configurations.

## 📋 Prerequisites

Before you begin, ensure you have:
- A GitHub repository with markdown documentation files
- Access to a Confluence space where you want to publish
- Confluence API token (Personal Access Token)
- Admin access to your GitHub repository (to add secrets)

## 🚀 Quick Start

### 1. Clone the Workflow Templates

Copy the following files from this repository to your own repository:

```bash
# Create the workflows directory if it doesn't exist
mkdir -p .github/workflows

# Copy the required workflow files
curl -o .github/workflows/matrix_docs_sync.yaml https://raw.githubusercontent.com/vertexinc/prodeng-docs-synchronizer/main/.github/workflows/matrix_docs_sync.yaml
curl -o .github/workflows/single_docs_sync.yaml https://raw.githubusercontent.com/vertexinc/prodeng-docs-synchronizer/main/.github/workflows/single_docs_sync.yaml

# Copy the matrix configuration template
curl -o matrix.json https://raw.githubusercontent.com/vertexinc/prodeng-docs-synchronizer/main/matrix.json
```

### 2. Configure GitHub Secrets

Add the following secret to your GitHub repository:

1. Go to your repository → Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Add:
   - **Name**: `ATLASSIAN_TOKEN`
   - **Value**: Your Confluence API token

## 📝 Configuration

### Setting Up matrix.json

The `matrix.json` file defines all the documents you want to publish. Each entry represents one markdown file and its destination in Confluence.

#### Basic Structure

```json
{
  "include": [
    {
      "name": "unique-job-name",
      "markdown_path": "path/to/your/file.md",
      "repository": "your-repo-name",
      "domain": "yourcompany.atlassian.net",
      "username": "your.email@company.com",
      "space": "SPACE_KEY",
      "root_page": "123456789",
      "job": "md2conf"
    }
  ]
}
```

#### Configuration Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `name` | Unique identifier for the job | `"user-guide"` |
| `markdown_path` | Path to markdown file from repo root | `"docs/user-guide.md"` |
| `repository` | Your GitHub repository name | `"my-company/documentation"` |
| `domain` | Your Confluence domain | `"mycompany.atlassian.net"` |
| `username` | Your Confluence email | `"john.doe@company.com"` |
| `space` | Confluence space key | `"DOCS"` |
| `root_page` | Confluence page ID where docs will be published | `"123456789"` |
| `job` | Job type (always use `"md2conf"`) | `"md2conf"` |

### 3. Bulk Configuration Example

Here's an example for publishing multiple documentation files:

```json
{
  "include": [
    {
      "name": "api-documentation",
      "markdown_path": "docs/api/README.md",
      "repository": "my-company/backend-services",
      "domain": "mycompany.atlassian.net",
      "username": "dev-team@company.com",
      "space": "API",
      "root_page": "987654321",
      "job": "md2conf"
    },
    {
      "name": "user-guide",
      "markdown_path": "docs/user-guide/getting-started.md",
      "repository": "my-company/backend-services",
      "domain": "mycompany.atlassian.net",
      "username": "dev-team@company.com",
      "space": "DOCS",
      "root_page": "123456789",
      "job": "md2conf"
    },
    {
      "name": "deployment-guide",
      "markdown_path": "docs/ops/deployment.md",
      "repository": "my-company/backend-services",
      "domain": "mycompany.atlassian.net",
      "username": "dev-team@company.com",
      "space": "OPS",
      "root_page": "456789123",
      "job": "md2conf"
    },
    {
      "name": "troubleshooting",
      "markdown_path": "docs/support/troubleshooting.md",
      "repository": "my-company/backend-services",
      "domain": "mycompany.atlassian.net",
      "username": "dev-team@company.com",
      "space": "SUPPORT",
      "root_page": "789123456",
      "job": "md2conf"
    }
  ]
}
```

## 🔧 Advanced Configuration

### Customizing Parallel Execution

By default, jobs run sequentially (`max-parallel: 1`) to avoid overwhelming the API. You can adjust this in `matrix_docs_sync.yaml`:

```yaml
strategy:
  matrix:
    include: ${{ fromJson(needs.load-matrix.outputs.matrix) }}
  fail-fast: false
  max-parallel: 3  # Increase for more parallel jobs
```

### Custom Runner Configuration

If you're using self-hosted runners, update the `runs-on` field in `single_docs_sync.yaml`:

```yaml
jobs:
  call-api:
    runs-on: your-custom-runner  # Change from arc-dind-viper-dev
```

### Adding Conditional Publishing

You can add conditions to only publish certain documents:

```yaml
# In matrix_docs_sync.yaml, add to the call-api-matrix job:
if: contains(matrix.name, 'production') || github.ref == 'refs/heads/main'
```

## 🎯 Finding Confluence Parameters

### Getting Your Space Key
1. Go to your Confluence space
2. Look at the URL: `https://yourcompany.atlassian.net/wiki/spaces/SPACEKEY/`
3. The `SPACEKEY` part is your space key

### Getting Page IDs
1. Navigate to the parent page where you want documents published
2. Click "..." menu → "Page Information"
3. Look at the URL: the number at the end is your page ID

### Getting Your Domain
Your Confluence domain is the part before `.atlassian.net` in your Confluence URL.

## 🚀 Running the Workflow

### Manual Trigger
1. Go to your repository → Actions
2. Select "Matrix Docs Sync API Parser"
3. Click "Run workflow"
4. Click "Run workflow" again

### Automatic Triggers
Add triggers to `matrix_docs_sync.yaml`:

```yaml
on:
  workflow_dispatch:  # Manual trigger
  push:
    branches: [main]   # Auto-run on main branch pushes
    paths: ['docs/**'] # Only when docs change
  schedule:
    - cron: '0 9 * * 1' # Weekly on Mondays at 9 AM
```

## 📊 Monitoring and Troubleshooting

### Viewing Results
- Go to Actions tab in your repository
- Click on the workflow run
- Check individual job logs for detailed output

### Common Issues

#### 1. Authentication Errors
- Verify your `ATLASSIAN_TOKEN` secret is correct
- Ensure the token has write permissions to your Confluence space

#### 2. File Not Found
- Check that `markdown_path` points to existing files
- Verify file paths are relative to repository root

#### 3. Permission Errors
- Ensure your Confluence user has edit permissions in the target space
- Verify the `root_page` ID exists and you have access

#### 4. API Rate Limiting
- Reduce `max-parallel` setting
- Add delays between jobs if needed

## 🎨 Customization Examples

### Publishing to Different Spaces Based on File Location

```json
{
  "include": [
    {
      "name": "frontend-docs",
      "markdown_path": "frontend/README.md",
      "space": "FRONTEND",
      "root_page": "111111111",
      "..."
    },
    {
      "name": "backend-docs", 
      "markdown_path": "backend/README.md",
      "space": "BACKEND",
      "root_page": "222222222",
      "..."
    }
  ]
}
```

### Environment-Specific Publishing

Create separate matrix files:
- `matrix-dev.json` for development documentation
- `matrix-prod.json` for production documentation

Update workflow to use different matrices based on branch:

```yaml
- name: Select Matrix File
  id: matrix-file
  run: |
    if [ "${{ github.ref }}" == "refs/heads/main" ]; then
      echo "file=matrix-prod.json" >> $GITHUB_OUTPUT
    else
      echo "file=matrix-dev.json" >> $GITHUB_OUTPUT
    fi

- name: Load Matrix from JSON
  id: set-matrix
  run: |
    MATRIX=$(cat ${{ steps.matrix-file.outputs.file }} | jq -c '.include')
    echo "matrix=$MATRIX" >> $GITHUB_OUTPUT
```

## 📚 Best Practices

1. **Test with a Small Set**: Start with 2-3 documents before scaling up
2. **Use Descriptive Names**: Make job names clear and unique
3. **Organize by Purpose**: Group related documents in the same Confluence space
4. **Version Control**: Keep your `matrix.json` in version control
5. **Monitor Runs**: Regularly check workflow execution logs
6. **Backup Strategy**: Consider keeping copies of important documentation

## 🔄 Maintenance

### Regular Tasks
- Review and update Confluence page IDs if pages are moved
- Verify API tokens haven't expired
- Check for any new documentation files that need publishing
- Monitor workflow execution times and adjust `max-parallel` if needed

### Scaling Considerations
- For 50+ documents, consider breaking into multiple matrix files
- Monitor Confluence API rate limits
- Consider using workflow artifacts for large-scale operations

## 🆘 Support

If you encounter issues:
1. Check the workflow execution logs in GitHub Actions
2. Verify all configuration parameters in `matrix.json`
3. Test with a single document first using the `call_docs_sync.yaml` workflow
4. Ensure your Confluence permissions are correct

For additional help, check the repository issues or contact your DevOps team.
