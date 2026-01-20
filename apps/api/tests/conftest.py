from __future__ import annotations

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
