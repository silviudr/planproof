from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, StrictStr, validator


def _parse_iso8601(value: str) -> datetime:
    if not isinstance(value, str):
        raise TypeError("must be a string")
    candidate = value.replace("Z", "+00:00") if value.endswith("Z") else value
    try:
        return datetime.fromisoformat(candidate)
    except ValueError as exc:
        raise ValueError("must be ISO-8601 timestamp") from exc


class PlanRequest(BaseModel):
    context: StrictStr
    current_time: StrictStr
    timezone: StrictStr
    variant: Literal["v1_naive", "v2_structured", "v3_agentic_repair"]

    _validate_current_time = validator("current_time", allow_reuse=True)(_parse_iso8601)


class PlanItem(BaseModel):
    task: StrictStr
    start_time: StrictStr
    end_time: StrictStr
    timebox_minutes: int = Field(ge=0)
    why: StrictStr

    _validate_start_time = validator("start_time", allow_reuse=True)(_parse_iso8601)
    _validate_end_time = validator("end_time", allow_reuse=True)(_parse_iso8601)


class ValidationMetrics(BaseModel):
    constraint_violation_count: int = Field(ge=0)
    overlap_minutes: int = Field(ge=0)
    hallucination_count: int = Field(ge=0)
    keyword_recall_score: float = Field(ge=0.0, le=1.0)
    human_feasibility_flags: int = Field(ge=0)


class PlanValidation(BaseModel):
    status: Literal["pass", "fail"]
    metrics: ValidationMetrics
    errors: list[StrictStr]


class DebugInfo(BaseModel):
    repair_attempted: bool
    repair_success: bool
    variant: StrictStr


class PlanResponse(BaseModel):
    plan: list[PlanItem]
    validation: PlanValidation
    debug: DebugInfo
