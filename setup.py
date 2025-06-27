#!/usr/bin/env python3
"""
Setup script for the Docs as Code - Confluence project
"""

import subprocess
import sys
import os

def install_dependencies():
    """Install Python dependencies"""
    print("Installing Python dependencies...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

def run_tests():
    """Run the test suite"""
    print("Running tests...")
    subprocess.check_call([sys.executable, "-m", "pytest", "tests/", "-v"])

def start_server():
    """Start the FastAPI development server"""
    print("Starting FastAPI server...")
    subprocess.check_call([sys.executable, "-m", "uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"])

def main():
    """Main setup function"""
    if len(sys.argv) < 2:
        print("Usage: python setup.py [install|test|start]")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "install":
        install_dependencies()
    elif command == "test":
        run_tests()
    elif command == "start":
        start_server()
    else:
        print(f"Unknown command: {command}")
        print("Available commands: install, test, start")
        sys.exit(1)

if __name__ == "__main__":
    main()
