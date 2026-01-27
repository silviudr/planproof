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
    temporal_constraints: List[str],
    current_time: str,
    overlap_minutes: int = 0,
) -> tuple[int, list[str]]:
    # NOTE: This implementation treats all constraints as positive "must-do at time X"
    # checks. It does not yet handle blocked/avoid windows (negative constraints).
    # TODO: Extend to parse and enforce blocked windows per the eval contract.
    if not plan_items or not temporal_constraints:
        return 0, []

    reference_start = isoparse(plan_items[0].start_time)
    current_dt = _align_timezone(isoparse(current_time), reference_start)
    default_dt = _default_date(current_dt)

    deadline_times: list[datetime] = []
    start_gate_times: list[datetime] = []
    for constraint in temporal_constraints:
        constraint_text = constraint or ""
        constraint_type = _categorize_constraint(constraint_text)
        times = _extract_times(constraint_text)
        for time_token in times:
            parsed = _parse_time_token(time_token, default_dt)
            if parsed is None:
                continue
            parsed_time = _align_timezone(parsed, reference_start)
            if constraint_type == "deadline":
                deadline_times.append(parsed_time)
            elif constraint_type == "start_gate":
                start_gate_times.append(parsed_time)
            break

    earliest_deadline = min(deadline_times) if deadline_times else None
    latest_start_gate = max(start_gate_times) if start_gate_times else None
    violations = 0
    error_messages: list[str] = []
    matched_indices: set[int] = set()
    for constraint in temporal_constraints:
        constraint_text = constraint or ""
        times = _extract_times(constraint_text)
        if not times:
            continue

        constraint_type = _categorize_constraint(constraint_text)
        lowered_constraint = constraint_text.lower()
        if "from" in lowered_constraint and "to" in lowered_constraint and len(times) >= 2:
            constraint_type = "window"
        target_time = None
        time_token_used = None
        window_start = None
        window_end = None
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

        if constraint_type == "window":
            parsed_start = _parse_time_token(times[0], default_dt)
            parsed_end = _parse_time_token(times[1], default_dt)
            if parsed_start is not None and parsed_end is not None:
                window_start = _align_timezone(parsed_start, reference_start)
                window_end = _align_timezone(parsed_end, reference_start)
                if earliest_deadline and window_end > earliest_deadline:
                    window_end = earliest_deadline
            else:
                continue

        if target_time is None and constraint_type != "window":
            continue

        if (
            constraint_type == "fixed_point"
            and earliest_deadline
            and target_time
            and target_time > earliest_deadline
        ):
            continue

        if constraint_type != "window":
            print(f"DEBUG: Parsed Constraint (Local): {target_time}")
            print(f"DEBUG: Current Time (Local): {current_dt}")
        if constraint_type == "window" and window_end is not None:
            if current_dt > window_end:
                violations += 1
                error_messages.append(
                    f"'{constraint_text}' constraint not met "
                    "(Window already passed.)"
                )
                continue
        elif current_dt > target_time:
            violations += 1
            if time_token_used:
                error_messages.append(
                    f"'{time_token_used}' constraint not met "
                    "(Constraint time already passed.)"
                )
            continue

        matched = False
        if constraint_type == "fixed_point":
            if latest_start_gate and target_time < latest_start_gate:
                matched = True
            else:
                for idx, item in enumerate(plan_items):
                    if idx in matched_indices:
                        continue
                    start_time = _align_timezone(
                        isoparse(item.start_time), reference_start
                    )
                    delta_minutes = abs((start_time - target_time).total_seconds()) / 60
                    if delta_minutes <= 5:
                        matched = True
                        matched_indices.add(idx)
                        break
                if not matched and overlap_minutes == 0:
                    for idx, item in enumerate(plan_items):
                        if idx in matched_indices:
                            continue
                        start_time = _align_timezone(
                            isoparse(item.start_time), reference_start
                        )
                        if start_time < target_time:
                            continue
                        end_time = _align_timezone(
                            isoparse(item.end_time), reference_start
                        )
                        duration_minutes = abs(
                            (end_time - start_time).total_seconds() / 60
                        )
                        allowed_shift = max(30, duration_minutes)
                        shift_minutes = (start_time - target_time).total_seconds() / 60
                        if 0 <= shift_minutes <= allowed_shift:
                            matched = True
                            matched_indices.add(idx)
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
        elif constraint_type == "window" and window_start and window_end:
            for item in plan_items:
                start_time = _align_timezone(
                    isoparse(item.start_time), reference_start
                )
                if window_start <= start_time <= window_end:
                    matched = True
                    break

        if not matched:
            violations += 1
            time_label = _format_time(target_time) if target_time else ""
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
            elif constraint_type == "window" and window_start and window_end:
                error_messages.append(
                    f"'{constraint_text}' constraint not met "
                    "(No task scheduled within the window.)"
                )
            elif time_token_used:
                error_messages.append(
                    f"'{time_token_used}' constraint not met "
                    f"(No task found near {time_label})."
                )

    return violations, error_messages
