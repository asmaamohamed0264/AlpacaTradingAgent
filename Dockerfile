# syntax=docker/dockerfile:1

# Base image
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# System dependencies for building some Python packages (lxml, hnswlib, etc.)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential \
       gcc \
       g++ \
       cmake \
       libxml2-dev \
       libxslt1-dev \
       libffi-dev \
       curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first for better layer caching
COPY requirements.txt ./
RUN python -m pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Install the package itself (ensures setup.py install_requires are satisfied)
RUN pip install --no-cache-dir -e .

# Create non-root user
RUN adduser --disabled-password --gecos "" appuser \
    && chown -R appuser:appuser /app
USER appuser

# Expose the Dash server port
EXPOSE 7860

# Default command: bind to 0.0.0.0 for container networking
CMD ["python", "run_webui_dash.py", "--server-name", "0.0.0.0"]


