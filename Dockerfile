FROM python:3.10-slim

WORKDIR /app

# Copy requirements first to leverage Docker caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install gunicorn explicitly
RUN pip install --no-cache-dir gunicorn

# Make folder for images
RUN mkdir -p /app/static/images

# Copy the application code
COPY . .

# Ensure correct permissions for images folder
RUN chmod -R 755 /app/static

# Envrionment variables
ENV DB_NAME=filmpoc
# ENV INSTANCE_CONNECTION_NAME=minflix-451300:us-west2:streaming-db
ENV DB_HOST=dpg-cvesi2nnoe9s73ba3ss0-a
ENV SETUPDB=Production
ENV ALGORITHM=HS256
ENV ACCESS_TOKEN_EXPIRE_MINUTES=10

# Expose the port - this is just documentation, Cloud Run ignores it
EXPOSE 8080

# Use Gunicorn as the production server
# Cloud Run sets PORT env variable - we use it to bind the server
CMD exec gunicorn --bind :$PORT --workers 1 --worker-class uvicorn.workers.UvicornWorker --threads 8 main:app