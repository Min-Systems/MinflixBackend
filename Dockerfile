# Use the Python 3 alpine official image
# https://hub.docker.com/_/python
FROM python:3-alpine

# Create and change to the app directory.
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .


# Copy local code to the container image.
COPY . .

# Install project dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Run the web service on container startup.
# CMD ["hypercorn", "app.main:app", "--bind", "::"]
CMD ["fastapi", "run", "app/main.py", "--port", "8000"]