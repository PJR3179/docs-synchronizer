# Simple Test Document

This is a simple test README file without Mermaid diagrams.

## Overview

This document demonstrates basic Markdown features that should be properly converted to Confluence format.

## Features

### Lists

**Unordered List:**
- Item 1
- Item 2
  - Nested item 2.1
  - Nested item 2.2
- Item 3

**Ordered List:**
1. First item
2. Second item
3. Third item

### Code Blocks

Here's some inline `code` and a code block:

```python
def hello_world():
    print("Hello, World!")
    return "success"
```

```bash
# Example bash command
curl -X POST "http://localhost:8000/publish"
```

### Tables

| Feature | Status | Notes |
|---------|--------|-------|
| Basic Markdown | ✅ | Working |
| Code Blocks | ✅ | Working |
| Tables | ✅ | Working |
| Links | ✅ | Working |

### Links

- [External Link](https://www.example.com)
- [Confluence](https://vertexinc.atlassian.net)

### Emphasis

This text has **bold** and *italic* formatting.

### Blockquotes

> This is a blockquote with important information.
> It can span multiple lines.

## Configuration

This document can be published to Confluence using the md2conf service with the following parameters:

- **Space**: PRE
- **Root Page**: 5685346535
- **Domain**: vertexinc.atlassian.net

## Testing Notes

This file is specifically designed to test:
1. Markdown parsing
2. Confluence conversion
3. Table formatting
4. Code syntax highlighting
5. Basic formatting elements

## Mermaid Diagram Test

<!-- confluence-page-id: 5748228865 -->
