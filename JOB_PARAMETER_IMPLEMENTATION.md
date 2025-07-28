# Job Parameter Feature Implementation Summary

## Overview
Added a new "job" parameter to the API that allows users to specify the processing type. Currently supports "md2conf" job type with validation to reject unsupported job types.

## Changes Made

### 1. Schema Updates (`app/models/schemas.py`)
- Added `job: Optional[str] = None` parameter to `MarkdownRequest` class
- Added comprehensive documentation for the parameter

### 2. API Endpoint Updates (`app/api/endpoints.py`)
- Added job type validation in the `publish_markdown` endpoint
- Returns appropriate error response for unsupported job types
- Allows requests without job parameter (defaults to md2conf behavior)
- Allows "md2conf" job type to proceed normally

### 3. Workflow Updates (`/.github/workflows/shared.yml`)
- Added `job` input parameter with default value "md2conf"
- Added job parameter to environment variables
- Updated API call to include job parameter in request body

### 4. Matrix Configuration (`matrix.json`)
- Added "job": "md2conf" to the matrix configuration

### 5. Caller Workflow Updates (`/.github/workflows/caller.yml`)
- Added job parameter to the workflow call

### 6. Test Updates
- Updated existing test cases in `test_md2conf_service.py` to include job parameter
- Added new test for job parameter validation
- Created comprehensive API endpoint tests in `test_api_endpoints.py`

### 7. Documentation Updates (`README.md`)
- Updated curl examples to include job parameter
- Added explanation of job parameter behavior

## API Behavior

### Valid Requests
```json
{
  "markdown_path": "docs/file.md",
  "job": "md2conf",
  "domain": "example.atlassian.net",
  "username": "user@example.com",
  "api_key": "api_key_123",
  "space": "TEST",
  "root_page": "123456"
}
```

```json
{
  "markdown_path": "docs/file.md",
  "domain": "example.atlassian.net",
  "username": "user@example.com",
  "api_key": "api_key_123",
  "space": "TEST",
  "root_page": "123456"
}
```

### Invalid Request (Unsupported Job Type)
```json
{
  "markdown_path": "docs/file.md",
  "job": "unsupported_job",
  "domain": "example.atlassian.net",
  "username": "user@example.com",
  "api_key": "api_key_123",
  "space": "TEST",
  "root_page": "123456"
}
```

**Response:**
```json
{
  "success": false,
  "message": "Unsupported job type: unsupported_job. Only 'md2conf' is supported.",
  "error": "INVALID_JOB_TYPE"
}
```

## Backward Compatibility
- Existing API calls without the job parameter continue to work unchanged
- Default behavior remains the same (md2conf processing)
- No breaking changes to existing workflows or integrations

## Future Extensibility
The job parameter is designed to support additional processing types in the future:
- Easy to add new job types by extending the validation logic
- Clean separation between job validation and processing logic
- Consistent error handling pattern for unsupported job types
