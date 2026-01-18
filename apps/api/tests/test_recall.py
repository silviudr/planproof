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
