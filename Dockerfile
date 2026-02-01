FROM python:3.11-slim

# Install system dependencies needed for 'thefuzz' and 'Levenshtein'
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 1. Copy dependency files
COPY apps/api/pyproject.toml /app/pyproject.toml
# Create a dummy README so pip doesn't complain
RUN touch /app/README.md

# 2. Install dependencies
RUN python -m pip install --no-cache-dir --upgrade pip \
    && python -m pip install --no-cache-dir -e .

# 3. Copy the source code AND the validation logic
COPY apps/api/src /app/src
COPY apps/api/static /app/static
COPY eval /app/eval

# 4. Set PYTHONPATH
# This tells Python to look in /app (to find 'eval') 
# and /app/src (to find 'planproof_api')
ENV PYTHONPATH=/app:/app/src

EXPOSE 10000

# 5. Launch the app
CMD ["uvicorn", "planproof_api.main:app", "--host", "0.0.0.0", "--port", "10000"]