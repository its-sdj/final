# Use a base image
FROM its-sdj/final:v1

# Ensure /etc/apt/sources.list exists with the default Debian repository
RUN if [ ! -f /etc/apt/sources.list ]; then \
    echo "deb http://deb.debian.org/debian/ stable main" > /etc/apt/sources.list; \
    fi && apt-get update

# Install dependencies
RUN apt-get install -y \
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

# Install dependencies in the virtual environment
RUN /venv/bin/pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files
COPY . .

# Set the virtual environment as the default for all commands
ENV PATH="/venv/bin:$PATH"
