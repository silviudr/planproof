from __future__ import annotations

import re
from datetime import datetime
from typing import List, TYPE_CHECKING

from dateutil.parser import parse as parse_datetime, isoparse

if TYPE_CHECKING:
    from planproof_api.agent.schemas import PlanItem

_TIME_PATTERN = re.compile(
    r"\b(?:[01]?\d|2[0-3]):[0-5]\d\b|\b\d{1,2}\s?(?:am|pm)\b",
    re.IGNORECASE,
)


def _extract_times(text: str) -> list[str]:
    return [match.group(0) for match in _TIME_PATTERN.finditer(text)]


def _default_date(reference: datetime) -> datetime:
    return reference.replace(hour=0, minute=0, second=0, microsecond=0)


def check_constraints(plan_items: List["PlanItem"], detected_constraints: List[str]) -> int:
    if not plan_items or not detected_constraints:
        return 0

    reference_start = isoparse(plan_items[0].start_time)
    default_dt = _default_date(reference_start)

    violations = 0
    for constraint in detected_constraints:
        times = _extract_times(constraint or "")
        if not times:
            continue

        matched = False
        for time_token in times:
            try:
                target_time = parse_datetime(time_token, default=default_dt)
            except (ValueError, TypeError):
                continue

            for item in plan_items:
                start_time = isoparse(item.start_time)
                delta_minutes = abs((start_time - target_time).total_seconds()) / 60
                if delta_minutes <= 5:
                    matched = True
                    break
            if matched:
                break

        if not matched:
            violations += 1

    return violations
