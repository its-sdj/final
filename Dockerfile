# Use a base image
FROM sdj20/final:v1

# Ensure the sources.list exists and update APT
RUN if [ ! -f /etc/apt/sources.list ]; then \
        echo "deb http://ftp.debian.org/debian stable main" > /etc/apt/sources.list; \
    fi && apt-get update || echo "APT update failed, skipping..."

# Install system dependencies
RUN apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    libglib2.0-0 \
    python3-venv && \
    rm -rf /var/lib/apt/lists/*

# Create a virtual environment
RUN python3 -m venv /venv

# Set working directory
WORKDIR /app

# Copy requirements file and install Python dependencies
COPY requirements.txt .
RUN /venv/bin/pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Update PATH to use the virtual environment
ENV PATH="/venv/bin:$PATH"

# Default command (optional)
CMD ["python", "app.py"]
