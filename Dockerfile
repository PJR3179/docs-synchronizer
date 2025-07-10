FROM python:3.11-slim

# Install git for repository operations
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY main.py .
COPY entrypoint.py .

# Make entrypoint executable
RUN chmod +x entrypoint.py

# Set entrypoint
ENTRYPOINT ["python", "/app/entrypoint.py"]
