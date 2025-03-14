FROM python:3.10-slim

WORKDIR /app

# Copy requirements first to leverage Docker caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install gunicorn explicitly
RUN pip install --no-cache-dir gunicorn

# Copy the application code
COPY . .

# Expose the port - this is just documentation, Cloud Run ignores it
EXPOSE 8080

# Use Gunicorn as the production server
# Cloud Run sets PORT env variable - we use it to bind the server
CMD exec gunicorn --bind :$PORT --workers 1 --worker-class uvicorn.workers.UvicornWorker --threads 8 server:app