FROM python:3.9-slim

# Install system dependencies for dlib, OpenCV, SQLite, etc.
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
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy project files
COPY . /app

# Upgrade pip first
RUN pip install --upgrade pip

# Install dlib with custom flags to avoid memory crash
RUN pip install --no-cache-dir dlib --config-settings="--build-option=--jobs=1"

# Install the rest of the requirements (skip dlib in requirements.txt!)
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000"]
