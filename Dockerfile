# Use the base image for your app
FROM its-sdj/final:v1

# Install dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

# Create and activate virtual environment
RUN python3 -m venv /venv

# Set working directory
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install the Python dependencies into the virtual environment
RUN /venv/bin/pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files
COPY . .

# Set the virtual environment as the default for all commands
ENV PATH="/venv/bin:$PATH"
