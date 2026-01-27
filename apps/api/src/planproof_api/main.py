from __future__ import annotations

import os
import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from planproof_api.config import settings
from planproof_api.observability.opik import opik
from opik import config as opik_config
from planproof_api.routes import router

try:
    opik_config.update_session_config("project_name", settings.OPIK_PROJECT_NAME)
    opik.configure(
        api_key=settings.OPIK_API_KEY,
        workspace=settings.OPIK_WORKSPACE,
    )
    print(
        f"OPIK INITIALIZED: {settings.OPIK_WORKSPACE}/{settings.OPIK_PROJECT_NAME}"
    )
except Exception as exc:
    print(f"OPIK WARNING: Failed to initialize. ({exc})", file=sys.stderr)

app = FastAPI()

app.include_router(router)

static_candidates = []
env_static = os.getenv("PLANPROOF_STATIC_DIR")
if env_static:
    static_candidates.append(Path(env_static))
static_candidates.append(Path.cwd() / "apps" / "api" / "static")
static_candidates.append(Path(__file__).resolve().parent.parent.parent / "static")
static_candidates.append(Path(__file__).resolve().parent / "static")

static_dir = next(
    (candidate for candidate in static_candidates if candidate.exists()),
    None,
)
if static_dir is None:
    raise RuntimeError(
        "Static directory not found. "
        "Set PLANPROOF_STATIC_DIR or run from the repo root."
    )

app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")
