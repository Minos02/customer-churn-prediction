FROM python:3.11-slim

WORKDIR /app

# Install Node.js
RUN apt-get update && apt-get install -y nodejs npm && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy everything
COPY . .

# Build React frontend
WORKDIR /app/frontend
RUN npm install
RUN npm run build

# Back to app root
WORKDIR /app

# Expose port
EXPOSE 5000

# Start Flask
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "api.main:app"]
