#!/bin/bash
# Test script for Linux curl commands

# Load environment variables if .env exists
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Test health endpoint
echo "Testing health endpoint..."
curl -X GET "http://localhost:8001/health"
echo -e "\n"

# Test publish endpoint with environment variables
echo "Testing publish endpoint..."
curl -X POST "http://localhost:8001/publish" \
  -H "Content-Type: application/json" \
  -d "{
    \"markdown_path\": \"docs/simple-test.md\",
    \"domain\": \"${CONFLUENCE_DOMAIN:-vertexinc.atlassian.net}\",
    \"username\": \"${CONFLUENCE_USERNAME:-your-email@company.com}\",
    \"api_key\": \"${CONFLUENCE_API_KEY:-your-api-key}\",
    \"space\": \"${CONFLUENCE_SPACE:-PRE}\",
    \"root_page\": \"${CONFLUENCE_ROOT_PAGE:-5685346535}\"
  }"

echo -e "\n"

# Test with minimal request (using env vars)
echo "Testing minimal request (using environment variables)..."
curl -X POST "http://localhost:8001/publish" \
  -H "Content-Type: application/json" \
  -d "{
    \"markdown_path\": \"docs/simple-test.md\"
  }"

echo -e "\n"
