# Code Review Assistant - Docker Image
FROM python:3.11-slim

LABEL maintainer="kietnguyen@vulcanlabs.co"
LABEL description="AI-powered code review CLI using LangChain + Gemini"
LABEL version="0.1.0"

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    CRA_CONFIG_DIR=/config \
    CRA_OUTPUT_DIR=/output

# Create working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install poetry
RUN pip install poetry

# Copy project files
COPY pyproject.toml poetry.lock* ./
COPY shield_pr ./shield_pr
COPY README.md LICENSE ./

# Install dependencies and package
RUN poetry build && \
    pip install dist/code_review_assistant-*.whl && \
    rm -rf dist

# Create directories for config and output
RUN mkdir -p /config /output

# Create non-root user
RUN useradd -m -u 1000 crauser && \
    chown -R crauser:crauser /app /config /output
USER crauser

# Set working directory for reviews
WORKDIR /workspace

# Volume mounts
VOLUME ["/workspace", "/config", "/output"]

# Default command shows version
ENTRYPOINT ["shield-pr"]
CMD ["--help"]
