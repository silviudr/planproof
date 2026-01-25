from __future__ import annotations

import re
from datetime import datetime
from typing import List, TYPE_CHECKING

from dateutil.parser import isoparse

if TYPE_CHECKING:
    from planproof_api.agent.schemas import PlanItem

_TIME_PATTERN = re.compile(
    r"\b(?:[01]?\d|2[0-3])(?::[0-5]\d)?\s?(?:am|pm)\b"
    r"|\b(?:[01]?\d|2[0-3]):[0-5]\d\b",
    re.IGNORECASE,
)


def _extract_times(text: str) -> list[str]:
    return [match.group(0) for match in _TIME_PATTERN.finditer(text)]


def _default_date(reference: datetime) -> datetime:
    return reference.replace(hour=0, minute=0, second=0, microsecond=0)


def _parse_time_token(token: str, default_dt: datetime) -> datetime | None:
    cleaned = token.strip().lower()
    if not cleaned:
        return None

    if "am" in cleaned or "pm" in cleaned:
        normalized = cleaned.replace("am", " am").replace("pm", " pm")
        normalized = re.sub(r"\s+", " ", normalized).strip().upper()
        time_format = "%I:%M %p" if ":" in normalized else "%I %p"
        try:
            parsed = datetime.strptime(normalized, time_format)
        except ValueError:
            return None
        return default_dt.replace(
            hour=parsed.hour, minute=parsed.minute, second=0, microsecond=0
        )

    if ":" in cleaned:
        try:
            parsed = datetime.strptime(cleaned, "%H:%M")
        except ValueError:
            return None
        return default_dt.replace(
            hour=parsed.hour, minute=parsed.minute, second=0, microsecond=0
        )

    return None


def _format_time(value: datetime) -> str:
    time_value = value.strftime("%I:%M %p").lstrip("0")
    tz_label = value.tzname() or value.strftime("%z")
    return f"{time_value} {tz_label}".strip()


def _align_timezone(value: datetime, reference: datetime) -> datetime:
    if reference.tzinfo is None:
        return value
    if value.tzinfo is None:
        return value.replace(tzinfo=reference.tzinfo)
    return value.astimezone(reference.tzinfo)


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
) -> tuple[int, list[str]]:
    # NOTE: This implementation treats all constraints as positive "must-do at time X"
    # checks. It does not yet handle blocked/avoid windows (negative constraints).
    # TODO: Extend to parse and enforce blocked windows per the eval contract.
    if not plan_items or not detected_constraints:
        return 0, []

    reference_start = isoparse(plan_items[0].start_time)
    current_dt = _align_timezone(isoparse(current_time), reference_start)
    default_dt = _default_date(current_dt)

    violations = 0
    error_messages: list[str] = []
    for constraint in detected_constraints:
        constraint_text = constraint or ""
        times = _extract_times(constraint_text)
        if not times:
            continue

        constraint_type = _categorize_constraint(constraint_text)
        target_time = None
        time_token_used = None
        for time_token in times:
            try:
                parsed = _parse_time_token(time_token, default_dt)
            except (ValueError, TypeError):
                parsed = None
            if parsed is None:
                continue
            target_time = _align_timezone(parsed, reference_start)
            time_token_used = time_token
            break

        if target_time is None:
            continue

        print(f"DEBUG: Parsed Constraint (Local): {target_time}")
        print(f"DEBUG: Current Time (Local): {current_dt}")
        if current_dt > target_time:
            violations += 1
            if time_token_used:
                error_messages.append(
                    f"'{time_token_used}' constraint not met "
                    "(Constraint time already passed.)"
                )
            continue

        matched = False
        if constraint_type == "fixed_point":
            for item in plan_items:
                start_time = _align_timezone(
                    isoparse(item.start_time), reference_start
                )
                delta_minutes = abs((start_time - target_time).total_seconds()) / 60
                if delta_minutes <= 5:
                    matched = True
                    break
        elif constraint_type == "deadline":
            for item in plan_items:
                end_time = _align_timezone(isoparse(item.end_time), reference_start)
                if end_time > target_time:
                    matched = False
                    break
            else:
                matched = True
        elif constraint_type == "start_gate":
            for item in plan_items:
                start_time = _align_timezone(
                    isoparse(item.start_time), reference_start
                )
                if start_time < target_time:
                    matched = False
                    break
            else:
                matched = True

        if not matched:
            violations += 1
            time_label = _format_time(target_time)
            if constraint_type == "fixed_point" and time_token_used:
                error_messages.append(
                    f"'{time_token_used}' constraint not met "
                    f"(No task found within 5 minutes of {time_label})."
                )
            elif constraint_type == "deadline":
                error_messages.append(
                    f"'{constraint_text}' constraint not met "
                    f"(Task ends after {time_label})."
                )
            elif constraint_type == "start_gate":
                error_messages.append(
                    f"'{constraint_text}' constraint not met "
                    f"(Task starts before {time_label})."
                )
            elif time_token_used:
                error_messages.append(
                    f"'{time_token_used}' constraint not met "
                    f"(No task found near {time_label})."
                )

    return violations, error_messages
