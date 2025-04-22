# Use a base image
FROM python:3.9-slim

# Set the proxy environment variables if you're behind a proxy (optional)
# ENV http_proxy=http://your_proxy:8090
# ENV https_proxy=http://your_proxy:8090

# Set a working directory
WORKDIR /app

# Ensure sources.list exists and update the sources for apt
RUN if [ ! -f /etc/apt/sources.list ]; then \
        echo "deb http://deb.debian.org/debian stable main" > /etc/apt/sources.list; \
    fi && \
    apt-get update && \
    apt-get install -y --fix-missing \
    libgl1-mesa-glx \
    libglib2.0-0 \
    python3-venv && \
    rm -rf /var/lib/apt/lists/*

# Copy your application code into the container
COPY . .

# Create and activate a virtual environment
RUN python3 -m venv venv
RUN . venv/bin/activate

# Install Python dependencies (ensure you have a requirements.txt file)
RUN pip install --no-cache-dir -r requirements.txt

# Expose port (if needed for your app)
EXPOSE 5000

# Set the command to run your app
CMD ["python", "app.py"]
