FROM python:3.11-slim

# Set working directory to the project root in the container
WORKDIR /service

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for caching
COPY backend/requirements.txt /service/backend/requirements.txt

# Install python dependencies
RUN pip install --no-cache-dir -r /service/backend/requirements.txt

# Copy the entire backend directory
COPY backend /service/backend

# Set the Python path to include the backend directory so 'app' module is found
ENV PYTHONPATH=/service/backend

# Default Port for Cloud Run
ENV PORT=8080

# Run uvicorn (host 0.0.0.0 is critical for containers)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
