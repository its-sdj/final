# Use a base image with necessary dependencies (avoid slim for OpenCV)
FROM python:3.9

# Set working directory
WORKDIR /app

# Install system dependencies for OpenCV and other libraries
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create a virtual environment and activate it
RUN python3 -m venv /venv
ENV PATH="/venv/bin:$PATH"

# Install test dependencies (for Jenkins test stage)
RUN pip install --no-cache-dir pytest pytest-cov

# Copy the rest of the application code
COPY . .

# Expose the port your app runs on (Flask default is 5000; update if different)
EXPOSE 8080

# Run the app with the virtual environment
CMD ["venv/bin/python", "app.py"]
