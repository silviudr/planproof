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


def _categorize_constraint(text: str) -> str:
    lowered = text.lower()
    if any(token in lowered for token in ["by", "before", "no later than"]):
        return "deadline"
    if "until" in lowered:
        return "start_gate"
    if any(token in lowered for token in ["at", "meeting", "appointment"]):
        return "fixed_point"
    return "fixed_point"


def check_constraints(
    plan_items: List["PlanItem"],
    detected_constraints: List[str],
    current_time: str,
) -> int:
    # NOTE: This implementation treats all constraints as positive "must-do at time X"
    # checks. It does not yet handle blocked/avoid windows (negative constraints).
    # TODO: Extend to parse and enforce blocked windows per the eval contract.
    if not plan_items or not detected_constraints:
        return 0

    reference_start = isoparse(plan_items[0].start_time)
    default_dt = _default_date(reference_start)
    current_dt = isoparse(current_time)

    violations = 0
    for constraint in detected_constraints:
        constraint_text = constraint or ""
        times = _extract_times(constraint_text)
        if not times:
            continue

        constraint_type = _categorize_constraint(constraint_text)
        target_time = None
        for time_token in times:
            try:
                target_time = parse_datetime(time_token, default=default_dt)
                break
            except (ValueError, TypeError):
                continue

        if target_time is None:
            continue

        if current_dt > target_time:
            violations += 1
            continue

        matched = False
        if constraint_type == "fixed_point":
            for item in plan_items:
                start_time = isoparse(item.start_time)
                delta_minutes = abs((start_time - target_time).total_seconds()) / 60
                if delta_minutes <= 5:
                    matched = True
                    break
        elif constraint_type == "deadline":
            for item in plan_items:
                end_time = isoparse(item.end_time)
                if end_time > target_time:
                    matched = False
                    break
            else:
                matched = True
        elif constraint_type == "start_gate":
            for item in plan_items:
                start_time = isoparse(item.start_time)
                if start_time < target_time:
                    matched = False
                    break
            else:
                matched = True

        if not matched:
            violations += 1

    return violations
