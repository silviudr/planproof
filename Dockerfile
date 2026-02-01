FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 1. Copy pyproject.toml AND the source code first
# Pip needs the 'src' directory to exist to complete the installation
COPY apps/api/pyproject.toml /app/pyproject.toml
COPY apps/api/src /app/src
RUN touch /app/README.md

# 2. Install dependencies (now it will find /app/src)
RUN python -m pip install --no-cache-dir --upgrade pip \
    && python -m pip install --no-cache-dir -e .

# 3. Copy the remaining folders
COPY apps/api/static /app/static
COPY eval /app/eval

# 4. Set PYTHONPATH
ENV PYTHONPATH=/app:/app/src

EXPOSE 10000

CMD ["uvicorn", "planproof_api.main:app", "--host", "0.0.0.0", "--port", "10000"]