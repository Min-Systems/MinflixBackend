FROM python:3.10-slim

WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir fastapi uvicorn

# Copy application code
COPY main.py .

# Expose port
EXPOSE 8080

# Run the application
CMD ["python", "main.py"]
