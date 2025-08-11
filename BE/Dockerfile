# Backend Dockerfile
FROM python:3.11-slim

# Set Working Directory
WORKDIR /app

# Copy Requirements and Install Dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy Application Code
COPY . .

# Expose Backend Port
EXPOSE 8000

# Run the Backend
CMD ["python", "main.py"]