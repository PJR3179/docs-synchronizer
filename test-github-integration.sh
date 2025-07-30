#!/bin/bash
# Test script for GitHub file downloading functionality

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Default values
GITHUB_TOKEN=${GITHUB_TOKEN:-""}
GITHUB_REPO=${1:-"vertexinc/prodeng-md-to-confluence"}
GITHUB_FILE=${2:-"README.md"}
GITHUB_REF=${3:-"main"}

echo -e "${YELLOW}Testing GitHub file download functionality${NC}"
echo "----------------------------------------"
echo -e "Repository: ${GREEN}$GITHUB_REPO${NC}"
echo -e "File path: ${GREEN}$GITHUB_FILE${NC}"
echo -e "Branch/ref: ${GREEN}$GITHUB_REF${NC}"
echo -e "GitHub token: ${GITHUB_TOKEN:+${GREEN}Set${NC}}${GITHUB_TOKEN:+${RED}Not set${NC}}"
echo "----------------------------------------"

# Create temp directory
TEMP_DIR=$(mktemp -d)
echo -e "Created temp directory: ${GREEN}$TEMP_DIR${NC}"

# Function to clean up
cleanup() {
    echo -e "Cleaning up temp directory: ${YELLOW}$TEMP_DIR${NC}"
    rm -rf "$TEMP_DIR"
    exit $1
}

# Test 1: Download using raw URL
echo -e "\n${YELLOW}Test 1: Downloading using raw GitHub URL${NC}"
RAW_URL="https://raw.githubusercontent.com/$GITHUB_REPO/$GITHUB_REF/$GITHUB_FILE"
echo -e "URL: ${GREEN}$RAW_URL${NC}"

# Setup headers
HEADERS=()
if [ -n "$GITHUB_TOKEN" ]; then
    HEADERS=(-H "Authorization: token $GITHUB_TOKEN")
fi

# Download the file
RAW_OUTPUT="$TEMP_DIR/raw_output.md"
if curl -s "${HEADERS[@]}" -o "$RAW_OUTPUT" "$RAW_URL"; then
    echo -e "${GREEN}✓ Successfully downloaded file using raw URL${NC}"
    echo -e "File size: ${GREEN}$(wc -c < "$RAW_OUTPUT") bytes${NC}"
    echo -e "First 5 lines:"
    head -n 5 "$RAW_OUTPUT" | sed 's/^/  /'
else
    echo -e "${RED}✗ Failed to download file using raw URL${NC}"
    echo "HTTP Status: $(curl -s -o /dev/null -w "%{http_code}" "${HEADERS[@]}" "$RAW_URL")"
fi

# Test 2: Download using GitHub API
echo -e "\n${YELLOW}Test 2: Downloading using GitHub API${NC}"
API_URL="https://api.github.com/repos/$GITHUB_REPO/contents/$GITHUB_FILE?ref=$GITHUB_REF"
echo -e "URL: ${GREEN}$API_URL${NC}"

# Download using the API
API_OUTPUT="$TEMP_DIR/api_output.json"
if curl -s "${HEADERS[@]}" -H "Accept: application/vnd.github.v3+json" -o "$API_OUTPUT" "$API_URL"; then
    if jq -e '.content' "$API_OUTPUT" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Successfully retrieved file metadata from GitHub API${NC}"
        echo -e "File type: ${GREEN}$(jq -r '.type' "$API_OUTPUT")${NC}"
        echo -e "File size: ${GREEN}$(jq -r '.size' "$API_OUTPUT") bytes${NC}"
        
        # Decode content
        if command -v base64 > /dev/null && jq -e '.content' "$API_OUTPUT" > /dev/null 2>&1; then
            API_CONTENT="$TEMP_DIR/api_content.md"
            jq -r '.content' "$API_OUTPUT" | base64 -d > "$API_CONTENT"
            echo -e "Decoded content, first 5 lines:"
            head -n 5 "$API_CONTENT" | sed 's/^/  /'
        else
            echo -e "${YELLOW}⚠ Could not decode content (missing base64 or jq tools)${NC}"
        fi
    else
        echo -e "${RED}✗ File metadata does not contain content${NC}"
        echo "API Response: $(cat "$API_OUTPUT" | tr -d '\n' | cut -c 1-100)..."
    fi
else
    echo -e "${RED}✗ Failed to retrieve file metadata from GitHub API${NC}"
    echo "HTTP Status: $(curl -s -o /dev/null -w "%{http_code}" "${HEADERS[@]}" -H "Accept: application/vnd.github.v3+json" "$API_URL")"
    echo "API Response: $(cat "$API_OUTPUT")"
fi

echo -e "\n${YELLOW}Summary${NC}"
echo "----------------------------------------"
if [ -f "$RAW_OUTPUT" ] && [ -s "$RAW_OUTPUT" ]; then
    echo -e "${GREEN}✓ Raw URL download successful${NC}"
else
    echo -e "${RED}✗ Raw URL download failed${NC}"
fi

if [ -f "$API_OUTPUT" ] && jq -e '.content' "$API_OUTPUT" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ GitHub API download successful${NC}"
else
    echo -e "${RED}✗ GitHub API download failed${NC}"
fi

echo -e "\n${YELLOW}Testing with Python script${NC}"
echo "----------------------------------------"

# Create a Python test script
cat > "$TEMP_DIR/test_github.py" << EOF
#!/usr/bin/env python3
"""
Test GitHub file downloading functionality.
"""
import os
import sys
import base64
import json
import requests
from pathlib import Path

# Configuration
github_token = os.environ.get("GITHUB_TOKEN", "")
github_repo = "${GITHUB_REPO}"
github_file = "${GITHUB_FILE}"
github_ref = "${GITHUB_REF}"

print(f"Testing GitHub file download for {github_repo}/{github_file} (ref: {github_ref})")

# Test 1: Raw URL
raw_url = f"https://raw.githubusercontent.com/{github_repo}/{github_ref}/{github_file}"
print(f"\nTest 1: Raw URL - {raw_url}")

headers = {"User-Agent": "GithubFileTest/1.0"}
if github_token:
    headers["Authorization"] = f"token {github_token}"

try:
    response = requests.get(raw_url, headers=headers)
    print(f"Status code: {response.status_code}")
    
    if response.status_code == 200:
        content = response.text
        print(f"Success! Content length: {len(content)} bytes")
        print("First few lines:")
        for line in content.splitlines()[:5]:
            print(f"  {line}")
    else:
        print(f"Failed. Response: {response.text[:100]}...")
except Exception as e:
    print(f"Error: {str(e)}")

# Test 2: GitHub API
api_url = f"https://api.github.com/repos/{github_repo}/contents/{github_file}?ref={github_ref}"
print(f"\nTest 2: GitHub API - {api_url}")

try:
    headers["Accept"] = "application/vnd.github.v3+json"
    response = requests.get(api_url, headers=headers)
    print(f"Status code: {response.status_code}")
    
    if response.status_code == 200:
        content_data = response.json()
        print(f"Success! File type: {content_data.get('type')}")
        print(f"File size: {content_data.get('size')} bytes")
        
        if content_data.get("type") == "file" and content_data.get("content"):
            try:
                decoded_content = base64.b64decode(content_data.get("content")).decode("utf-8")
                print("First few lines of decoded content:")
                for line in decoded_content.splitlines()[:5]:
                    print(f"  {line}")
            except Exception as e:
                print(f"Error decoding content: {str(e)}")
    else:
        print(f"Failed. Response: {response.text[:100]}...")
except Exception as e:
    print(f"Error: {str(e)}")

print("\nTests completed.")
EOF

# Make the Python script executable
chmod +x "$TEMP_DIR/test_github.py"

# Run the Python test if Python is available
if command -v python3 > /dev/null; then
    python3 "$TEMP_DIR/test_github.py"
else
    echo -e "${YELLOW}⚠ Python not found, skipping Python test${NC}"
fi

# Clean up
cleanup 0
