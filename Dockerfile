# Use a larger base image with necessary dependencies (avoid slim for OpenCV)
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

# Copy app code
COPY . .

# Expose port (adjust based on your app, e.g., 5000 for Flask, 8000 for FastAPI)
EXPOSE 8080

# Run the app
CMD ["python", "app.py"]