# Use an official Python runtime as a parent image
ARG BASE_IMAGE=python:3.9
FROM ${BASE_IMAGE}

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install test dependencies if provided
ARG TEST_DEPS=""
RUN if [ -n "$TEST_DEPS" ]; then \
    echo "Installing test dependencies: $TEST_DEPS"; \
    pip install --no-cache-dir $TEST_DEPS; \
    fi

# Copy the rest of the application
COPY . .

# Command to run the application
CMD ["python", "app/main.py"]
