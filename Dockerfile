
# Base Image
FROM python:3.12-slim

# Working Directory
WORKDIR /app


# System Dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Python Dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Application Code
COPY app/ ./app/

# Port
EXPOSE 8000

# start command 
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
