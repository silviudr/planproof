from __future__ import annotations

from planproof_api.agent.schemas import PlanItem

from eval.time_math import calculate_overlaps


def _item(start_time: str, end_time: str) -> PlanItem:
    return PlanItem(
        task="Test task",
        start_time=start_time,
        end_time=end_time,
        timebox_minutes=0,
        why="Test",
    )


def test_calculate_overlaps_no_overlap() -> None:
    items = [
        _item("2025-01-18T09:00:00-05:00", "2025-01-18T10:00:00-05:00"),
        _item("2025-01-18T10:00:00-05:00", "2025-01-18T11:00:00-05:00"),
    ]

    assert calculate_overlaps(items) == 0


def test_calculate_overlaps_empty_list() -> None:
    assert calculate_overlaps([]) == 0


def test_calculate_overlaps_single_item() -> None:
    items = [_item("2025-01-18T09:00:00-05:00", "2025-01-18T10:00:00-05:00")]

    assert calculate_overlaps(items) == 0


def test_calculate_overlaps_partial_overlap() -> None:
    items = [
        _item("2025-01-18T09:00:00-05:00", "2025-01-18T10:00:00-05:00"),
        _item("2025-01-18T09:30:00-05:00", "2025-01-18T10:30:00-05:00"),
    ]

    assert calculate_overlaps(items) == 30


def test_calculate_overlaps_complete_overlap() -> None:
    items = [
        _item("2025-01-18T09:00:00-05:00", "2025-01-18T12:00:00-05:00"),
        _item("2025-01-18T09:30:00-05:00", "2025-01-18T10:30:00-05:00"),
    ]

    assert calculate_overlaps(items) == 60


def test_calculate_overlaps_multiple_items_pairwise_sum() -> None:
    items = [
        _item("2025-01-18T09:00:00-05:00", "2025-01-18T10:00:00-05:00"),
        _item("2025-01-18T09:30:00-05:00", "2025-01-18T10:30:00-05:00"),
        _item("2025-01-18T09:45:00-05:00", "2025-01-18T10:15:00-05:00"),
    ]

    assert calculate_overlaps(items) == 75


def test_calculate_overlaps_different_timezones() -> None:
    items = [
        _item("2025-01-18T09:00:00-05:00", "2025-01-18T10:00:00-05:00"),
        _item("2025-01-18T08:30:00-06:00", "2025-01-18T09:30:00-06:00"),
    ]

    assert calculate_overlaps(items) == 30
