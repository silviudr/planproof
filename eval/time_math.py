from __future__ import annotations

from datetime import datetime
from typing import List, TYPE_CHECKING

from dateutil.parser import isoparse

if TYPE_CHECKING:
    from planproof_api.agent.schemas import PlanItem


def _parse_time(value: str) -> datetime:
    return isoparse(value)


def calculate_overlaps(items: List["PlanItem"]) -> int:
    intervals: list[tuple[datetime, datetime]] = []
    for item in items:
        start = _parse_time(item.start_time)
        end = _parse_time(item.end_time)
        if end <= start:
            raise ValueError(
                f"Invalid plan item interval: end_time ({item.end_time}) must be after "
                f"start_time ({item.start_time})."
            )
        intervals.append((start, end))

    overlap_minutes = 0
    for i in range(len(intervals)):
        for j in range(i + 1, len(intervals)):
            overlap_start = max(intervals[i][0], intervals[j][0])
            overlap_end = min(intervals[i][1], intervals[j][1])
            if overlap_start < overlap_end:
                overlap_minutes += (overlap_end - overlap_start).total_seconds() // 60

    return overlap_minutes
