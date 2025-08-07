#!/bin/bash

# Simple app test - run this locally to verify app starts
echo "🧪 Testing app startup locally..."

# Test 1: Check if app starts locally
echo "1. Testing local startup..."
python3 -c "
import sys
sys.path.append('.')
try:
    from app.config import settings
    print(f'✅ Config loaded: host={settings.host}, port={settings.port}')
except Exception as e:
    print(f'❌ Config error: {e}')

try:
    from app.api.endpoints import router
    print('✅ Endpoints imported successfully')
except Exception as e:
    print(f'❌ Endpoints error: {e}')

try:
    from main import app
    print('✅ FastAPI app created successfully')
except Exception as e:
    print(f'❌ App creation error: {e}')
"

echo ""
echo "2. Testing with Docker locally..."
echo "Run this to test your container:"
echo "docker build -t test-md2conf ."
echo "docker run -p 8080:8080 test-md2conf"
echo "Then test: curl http://localhost:8080/actuator/health"
