from __future__ import annotations

import os

import pytest


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--run-live",
        action="store_true",
        default=False,
        help="Run live OpenAI tests that incur API usage.",
    )


@pytest.fixture(scope="session")
def run_live(pytestconfig: pytest.Config) -> bool:
    return pytestconfig.getoption("--run-live")


def pytest_configure() -> None:
    os.environ.setdefault("OPIK_TRACK_DISABLE", "1")
    try:
        from planproof_api.observability.opik import opik

        if hasattr(opik, "set_tracing_active"):
            opik.set_tracing_active(False)
    except Exception:
        pass
