# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install --no-cache-dir poetry

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy only requirements to cache them in docker layer
COPY pyproject.toml poetry.lock* ./

# Project initialization:
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

# Copying the rest of the application
COPY . .

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Run the application:
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "app:app"]
