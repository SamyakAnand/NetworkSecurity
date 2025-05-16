# Dockerfile
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Install system utilities (optional but useful)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    jq \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies and install them
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Run the application
CMD ["python3", "app.py"]
