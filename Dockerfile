# Use a base image passed as a build argument, default to python:3.9-slim if not provided
ARG BASE_IMAGE
FROM ${BASE_IMAGE:-python:3.9-slim}

# Configure proxy settings (required for your network)
ENV http_proxy=http://172.21.3.100:8090
ENV https_proxy=http://172.21.3.100:8090
ENV no_proxy=localhost,127.0.0.1

# Set working directory
WORKDIR /app

# Install dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and app files
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# Expose port and run
EXPOSE 5000
CMD ["python", "app.py"]
