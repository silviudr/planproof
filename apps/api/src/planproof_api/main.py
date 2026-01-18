from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from planproof_api.routes import router

app = FastAPI()

app.include_router(router)

static_dir = Path(__file__).resolve().parent.parent.parent / "static"
if not static_dir.exists():
    raise RuntimeError(f"Static directory not found at {static_dir}")

app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")
