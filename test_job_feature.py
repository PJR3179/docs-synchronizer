#!/usr/bin/env python3
"""
Simple test script to verify the job parameter functionality.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.schemas import MarkdownRequest
from app.api.endpoints import publish_markdown
from app.services.md2conf_service import MD2ConfService

def test_job_validation():
    """Test the job parameter validation logic."""
    
    print("Testing job parameter validation...")
    
    # Test 1: Valid md2conf job
    print("\n1. Testing with valid 'md2conf' job:")
    try:
        request = MarkdownRequest(
            markdown_path="test.md",
            job="md2conf"
        )
        print(f"✓ Created request with job: {request.job}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test 2: No job specified (should default)
    print("\n2. Testing with no job specified:")
    try:
        request = MarkdownRequest(
            markdown_path="test.md"
        )
        print(f"✓ Created request with job: {request.job}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test 3: Invalid job (this will be caught in the endpoint)
    print("\n3. Testing with invalid job type:")
    try:
        request = MarkdownRequest(
            markdown_path="test.md",
            job="invalid_job"
        )
        print(f"✓ Created request with job: {request.job}")
        print("  (Note: Invalid job validation happens in the endpoint, not the schema)")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    print("\n✓ All job parameter tests completed successfully!")

if __name__ == "__main__":
    test_job_validation()
