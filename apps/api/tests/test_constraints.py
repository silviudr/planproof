from __future__ import annotations

from planproof_api.agent.schemas import PlanItem

from eval.constraints import check_constraints


def _item(start_time: str, end_time: str) -> PlanItem:
    return PlanItem(
        task="Test task",
        start_time=start_time,
        end_time=end_time,
        timebox_minutes=0,
        why="Test",
    )


def test_check_constraints_start_gate_violation() -> None:
    items = [
        _item("2025-01-18T09:00:00-05:00", "2025-01-18T10:00:00-05:00"),
        _item("2025-01-18T10:30:00-05:00", "2025-01-18T11:00:00-05:00"),
    ]
    constraints = ["Busy until 10 AM"]

    count, errors = check_constraints(
        items, constraints, "2025-01-18T08:00:00-05:00"
    )

    assert count == 1
    assert errors


def test_check_constraints_deadline_violation() -> None:
    items = [
        _item("2025-01-18T14:00:00-05:00", "2025-01-18T18:00:00-05:00"),
    ]
    constraints = ["Leave by 5 PM"]

    count, errors = check_constraints(
        items, constraints, "2025-01-18T12:00:00-05:00"
    )

    assert count == 1
    assert errors
