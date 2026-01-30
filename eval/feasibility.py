from __future__ import annotations

from typing import List, TYPE_CHECKING

from dateutil.parser import isoparse

if TYPE_CHECKING:
    from planproof_api.agent.schemas import PlanItem


def check_feasibility(plan_items: List["PlanItem"]) -> tuple[int, list[str]]:
    if not plan_items:
        return 0, []

    items = sorted(plan_items, key=lambda item: isoparse(item.start_time))
    block_start = isoparse(items[0].start_time)
    block_end = isoparse(items[0].end_time)
    flags = 0
    errors: list[str] = []

    for item in items[1:]:
        start_time = isoparse(item.start_time)
        end_time = isoparse(item.end_time)
        gap_minutes = (start_time - block_end).total_seconds() / 60

        if gap_minutes >= 15:
            block_minutes = (block_end - block_start).total_seconds() / 60
            if block_minutes > 240:
                flags += 1
            block_start = start_time
            block_end = end_time
        else:
            if end_time > block_end:
                block_end = end_time

    for item in items:
        label = (item.task or "").lower()
        if "meeting" in label or "sync" in label:
            start_time = isoparse(item.start_time)
            end_time = isoparse(item.end_time)
            duration_minutes = (end_time - start_time).total_seconds() / 60
            if duration_minutes < 20:
                flags += 1
                errors.append("Meeting duration is realistically too short.")

    block_minutes = (block_end - block_start).total_seconds() / 60
    if block_minutes > 240:
        flags += 1

    return flags, errors
