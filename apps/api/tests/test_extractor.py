from __future__ import annotations

import json
import os
from types import SimpleNamespace

import pytest

from planproof_api.agent import extractor


def _fake_openai(payload: dict) -> object:
    message = SimpleNamespace(content=json.dumps(payload))
    choice = SimpleNamespace(message=message)
    response = SimpleNamespace(choices=[choice])

    class _Completions:
        @staticmethod
        def create(**_: object) -> object:
            return response

    class _Chat:
        completions = _Completions()

    class _Client:
        chat = _Chat()

    return _Client()


def test_extract_metadata_mocked(monkeypatch: pytest.MonkeyPatch) -> None:
    payload = {
        "detected_constraints": ["Meeting at 2 PM"],
        "ground_truth_entities": ["Bob", "Apollo"],
        "task_keywords": ["call", "project"],
    }

    monkeypatch.setattr(extractor, "OpenAI", lambda: _fake_openai(payload))

    result = extractor.extract_metadata("Need to call Bob about the Apollo project.")

    assert result.detected_constraints == payload["detected_constraints"]
    assert result.ground_truth_entities == payload["ground_truth_entities"]
    assert result.task_keywords == payload["task_keywords"]


def test_extract_metadata_live(run_live: bool) -> None:
    if not run_live:
        pytest.skip("Use --run-live to enable OpenAI calls.")
    if not os.getenv("OPENAI_API_KEY"):
        pytest.skip("OPENAI_API_KEY not set.")

    result = extractor.extract_metadata("Need to call Bob about the Apollo project.")

    assert "Bob" in result.ground_truth_entities
    assert "Apollo" in result.ground_truth_entities


def test_normalize_entities_variants() -> None:
    values = [
        "Apollo project",
        "project Apollo",
        "Apollo",
        "",
        "project",
        "  ",
    ]

    normalized = extractor._normalize_entities(values)

    assert "Apollo project" in normalized
    assert "project Apollo" in normalized
    assert "Apollo" in normalized
    assert "project" not in normalized
