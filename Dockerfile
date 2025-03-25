# Use official Python slim image
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    libopenblas-dev \
    liblapack-dev \
    libx11-dev \
    libgtk-3-dev \
    libboost-all-dev \
    libsm6 \
    libxext6 \
    libxrender-dev \
    pkg-config \
    ffmpeg \
    libsqlite3-dev \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy all project files
COPY . /app

# Upgrade pip and install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expose the port that gunicorn will use
EXPOSE 5000

# Start the Flask app using gunicorn (filename: app.py, Flask instance: app)
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000"]
