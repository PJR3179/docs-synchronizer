# Refactored API Structure

## File Structure
```
project-root/
│
├── app/                           # Main application package
│   ├── __init__.py               # Package marker
│   ├── main.py                   # FastAPI app instance and route registration
│   ├── config.py                 # Settings and environment configuration
│   ├── api/                      # API layer
│   │   ├── __init__.py
│   │   └── endpoints.py          # All API endpoints (/health, /publish, etc.)
│   ├── models/                   # Data models
│   │   ├── __init__.py
│   │   └── schemas.py            # Pydantic models for requests/responses
│   └── services/                 # Business logic
│       ├── __init__.py
│       └── md2conf_service.py    # Core md2conf operations
│
├── tests/                        # Test files
│   └── test_md2conf_service.py   # Unit tests for the service
│
├── main.py                       # Application entry point (refactored)
├── entrypoint.py                 # GitHub Actions entry point (updated)
├── action.yml                    # GitHub Actions configuration
├── requirements.txt              # Dependencies
└── README.md                     # Documentation
```

## What Each File Contains

### app/main.py
- FastAPI app instance creation
- Router registration
- Backwards compatibility function for entrypoint.py

### app/config.py
- Centralized configuration using Pydantic BaseSettings
- Environment variable management
- Default values for all settings

### app/models/schemas.py
- All Pydantic models for requests and responses
- Type hints and validation rules
- Clear documentation for each field

### app/api/endpoints.py
- All API route definitions
- Dependency injection for services
- Proper response models and documentation

### app/services/md2conf_service.py
- Core business logic for md2conf operations
- Parameter validation
- Command building and execution
- Error handling

### tests/test_md2conf_service.py
- Unit tests for the service layer
- Mock external dependencies
- Test both success and failure scenarios

## Benefits of This Structure

1. **Separation of Concerns**: Each file has a single responsibility
2. **Testability**: Business logic is separated from API layer, making it easy to test
3. **Maintainability**: Code is organized logically and easy to navigate
4. **Scalability**: Easy to add new endpoints, services, or models
5. **Dependency Injection**: Services can be easily mocked and tested
6. **Configuration Management**: Centralized settings with environment variable support

## Key Improvements

- **Type Safety**: Better type hints throughout the codebase
- **Error Handling**: Centralized error handling in the service layer
- **Logging**: Consistent logging patterns
- **Documentation**: Better API documentation with proper response models
- **Testing**: Structure supports easy unit testing
- **Configuration**: Environment-based configuration management

## Running the Application

The application can still be run the same way:
```bash
python main.py
```

Or with uvicorn directly:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

## Running Tests

To run the tests (requires pytest):
```bash
pip install pytest pytest-mock
python -m pytest tests/ -v
```
