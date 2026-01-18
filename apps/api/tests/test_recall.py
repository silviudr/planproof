from __future__ import annotations

import pytest

from planproof_api.agent.schemas import PlanItem

from eval.recall import calculate_recall


def _item(task: str, why: str) -> PlanItem:
    return PlanItem(
        task=task,
        start_time="2025-01-18T09:00:00-05:00",
        end_time="2025-01-18T10:00:00-05:00",
        timebox_minutes=0,
        why=why,
    )


def test_calculate_recall_two_of_three_keywords() -> None:
    items = [
        _item("Morning exercise", "short workout session"),
        _item("Write report", "draft the weekly report"),
    ]
    keywords = ["exercise", "report", "groceries"]

    assert calculate_recall(items, keywords) == pytest.approx(0.66, abs=0.01)


def test_calculate_recall_empty_keywords() -> None:
    items = [_item("Write report", "draft the weekly report")]

    assert calculate_recall(items, []) == 0.0
    assert calculate_recall(items, [""]) == 0.0


def test_calculate_recall_empty_plan_items() -> None:
    assert calculate_recall([], ["report"]) == 0.0


def test_calculate_recall_empty_task_and_why() -> None:
    items = [_item("", "")]

    assert calculate_recall(items, ["report"]) == 0.0


def test_calculate_recall_exact_match() -> None:
    items = [_item("Write report", "")]

    assert calculate_recall(items, ["report"]) == 1.0


def test_calculate_recall_case_insensitive_match() -> None:
    items = [_item("MIKE", "")]

    assert calculate_recall(items, ["mike"]) == 1.0


def test_calculate_recall_threshold_boundary(monkeypatch) -> None:
    def fake_extract_one(_: str, __: list[str], ___=None) -> tuple[str, int]:
        return ("alpha", 80)

    monkeypatch.setattr("eval.recall.process.extractOne", fake_extract_one)

    items = [_item("Alpha", "")]

    assert calculate_recall(items, ["alpha"]) == 0.0


def test_calculate_recall_threshold_above(monkeypatch) -> None:
    def fake_extract_one(_: str, __: list[str], ___=None) -> tuple[str, int]:
        return ("alpha", 81)

    monkeypatch.setattr("eval.recall.process.extractOne", fake_extract_one)

    items = [_item("Alpha", "")]

    assert calculate_recall(items, ["alpha"]) == 1.0


def test_calculate_recall_no_matches() -> None:
    items = [_item("Do laundry", "")]

    assert calculate_recall(items, ["groceries"]) == 0.0


def test_calculate_recall_perfect_matches() -> None:
    items = [_item("Buy groceries", "plan trip itinerary")]
    keywords = ["groceries", "trip"]

    assert calculate_recall(items, keywords) == 1.0
