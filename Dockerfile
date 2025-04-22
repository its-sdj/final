# Use a Python base image
FROM python:3.9-slim

# Set the working directory to /app
WORKDIR /app

# Ensure sources.list exists and update the sources for apt
RUN if [ ! -f /etc/apt/sources.list ]; then \
        echo "deb http://archive.ubuntu.com/ubuntu stable main" > /etc/apt/sources.list; \
    fi && \
    apt-get update && \
    apt-get install -y --fix-missing \
    libgl1-mesa-glx \
    libglib2.0-0 \
    python3-venv && \
    rm -rf /var/lib/apt/lists/*

# Copy the current directory contents into the container at /app
COPY . /app

# Install required Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Expose the app on port 5000 (or whatever your app uses)
EXPOSE 5000

# Define the environment variable for Flask
ENV FLASK_APP=app.py

# Run the Flask app
CMD ["flask", "run", "--host=0.0.0.0"]
