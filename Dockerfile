FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

# Working directory in the container
WORKDIR /app

# Install system dependencies for Chrome/Puppeteer and other dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    gnupg \
    ca-certificates \
    curl \
    nodejs \
    npm \
    git \
    # Chrome dependencies
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libpango-1.0-0 \
    libcairo2 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code to the container
COPY . .

# Create directories with proper permissions BEFORE switching users
RUN mkdir -p /tmp/mermaid /app/.puppeteer_cache && \
    chmod 1777 /tmp/mermaid && \
    chmod 777 /app/.puppeteer_cache && \
    # Install npm packages as root for proper permissions
    npm install -g @mermaid-js/mermaid-cli && \
    # Create user and set ownership
    useradd -m appuser && \
    chown -R appuser:appuser /app

# Switch to app user
USER appuser

# Set environment variables for Puppeteer/Chrome
ENV TMPDIR=/tmp/mermaid
ENV PUPPETEER_CACHE_DIR=/app/.puppeteer_cache
ENV PUPPETEER_TMP_DIR=/tmp/mermaid
ENV CHROME_NO_SANDBOX=1
ENV PUPPETEER_EXECUTABLE_PATH=/usr/bin/google-chrome
ENV PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true
ENV PUPPETEER_ARGS="--no-sandbox --disable-setuid-sandbox --disable-dev-shm-usage --disable-gpu --no-first-run --no-zygote --single-process --disable-background-timer-throttling --disable-backgrounding-occluded-windows --disable-renderer-backgrounding"

# Expose the port the app will run on
EXPOSE 8080

# Add health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
  CMD curl -f http://localhost:8080/actuator/health || exit 1

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
