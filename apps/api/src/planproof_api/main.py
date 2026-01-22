from __future__ import annotations

from pathlib import Path
import sys

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from planproof_api.config import settings
from planproof_api.observability.opik import opik
from planproof_api.routes import router

try:
    opik.configure(
        api_key=settings.OPIK_API_KEY,
        workspace=settings.OPIK_WORKSPACE,
        project_name=settings.OPIK_PROJECT_NAME,
    )
    print(
        f"OPIK INITIALIZED: {settings.OPIK_WORKSPACE}/{settings.OPIK_PROJECT_NAME}"
    )
except Exception as exc:
    print(f"OPIK WARNING: Failed to initialize. ({exc})", file=sys.stderr)

app = FastAPI()

app.include_router(router)

static_dir = Path(__file__).resolve().parent.parent.parent / "static"
if not static_dir.exists():
    raise RuntimeError(f"Static directory not found at {static_dir}")

app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")
