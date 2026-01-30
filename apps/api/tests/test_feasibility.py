from __future__ import annotations

from planproof_api.agent.schemas import PlanItem

from eval.feasibility import check_feasibility


def _item(start_time: str, end_time: str) -> PlanItem:
    return PlanItem(
        task="Test task",
        start_time=start_time,
        end_time=end_time,
        timebox_minutes=0,
        why="Test",
    )


def test_check_feasibility_no_long_blocks() -> None:
    items = [
        _item("2025-01-18T09:00:00-05:00", "2025-01-18T11:00:00-05:00"),
        _item("2025-01-18T11:15:00-05:00", "2025-01-18T13:00:00-05:00"),
    ]

    flags, _ = check_feasibility(items)
    assert flags == 0


def test_check_feasibility_single_block_over_limit() -> None:
    items = [_item("2025-01-18T09:00:00-05:00", "2025-01-18T13:30:00-05:00")]

    flags, _ = check_feasibility(items)
    assert flags == 1


def test_check_feasibility_multiple_blocks_over_limit() -> None:
    items = [
        _item("2025-01-18T09:00:00-05:00", "2025-01-18T13:30:00-05:00"),
        _item("2025-01-18T13:45:00-05:00", "2025-01-18T18:15:00-05:00"),
    ]

    flags, _ = check_feasibility(items)
    assert flags == 2


def test_check_feasibility_break_exactly_15_minutes() -> None:
    items = [
        _item("2025-01-18T09:00:00-05:00", "2025-01-18T13:00:00-05:00"),
        _item("2025-01-18T13:15:00-05:00", "2025-01-18T15:00:00-05:00"),
    ]

    flags, _ = check_feasibility(items)
    assert flags == 0


def test_check_feasibility_overlapping_tasks() -> None:
    items = [
        _item("2025-01-18T09:00:00-05:00", "2025-01-18T11:00:00-05:00"),
        _item("2025-01-18T10:30:00-05:00", "2025-01-18T15:30:00-05:00"),
    ]

    flags, _ = check_feasibility(items)
    assert flags == 1


def test_check_feasibility_short_meeting() -> None:
    items = [
        PlanItem(
            task="Team Meeting",
            start_time="2025-01-18T09:00:00-05:00",
            end_time="2025-01-18T09:10:00-05:00",
            timebox_minutes=0,
            why="Test",
        )
    ]

    flags, errors = check_feasibility(items)

    assert flags == 1
    assert "Meeting duration is realistically too short." in errors
