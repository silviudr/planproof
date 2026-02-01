FROM python:3.11-slim

# 1. Install system dependencies for Levenshtein/thefuzz
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 2. Explicitly install dependencies FIRST.
# This bypasses all pyproject.toml pathing issues.
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
    "fastapi>=0.100.0" \
    "uvicorn[standard]>=0.22.0" \
    "pydantic>=2.0.0" \
    "pydantic-settings>=2.0.0" \
    "python-multipart>=0.0.6" \
    "python-dateutil>=2.8.2" \
    "thefuzz>=0.20.0" \
    "python-Levenshtein>=0.23.0" \
    "opik>=1.0.0" \
    "openai>=1.0.0" \
    "httpx>=0.24.1"

# 3. Copy your folders into a FLAT structure inside /app
# We take the content of apps/api/src and put it in /app/src
COPY apps/api/src ./src
COPY apps/api/static ./static
COPY eval ./eval

# 4. Set PYTHONPATH
# We tell Python that our code is in /app/src and our validators are in /app
ENV PYTHONPATH=/app:/app/src

EXPOSE 10000

# 5. Start the app using the flat path
CMD ["uvicorn", "planproof_api.main:app", "--host", "0.0.0.0", "--port", "10000"]