FROM python:3.11-slim

WORKDIR /app

COPY apps/api/pyproject.toml /app/pyproject.toml
COPY apps/api/src /app/src
COPY apps/api/static /app/static

RUN python -m pip install --no-cache-dir --upgrade pip \
    && python -m pip install --no-cache-dir -e .

EXPOSE 10000

CMD ["uvicorn", "planproof_api.main:app", "--host", "0.0.0.0", "--port", "10000"]
