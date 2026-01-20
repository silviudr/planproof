from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, StrictStr, field_validator


def _parse_iso8601(value: str) -> str:
    if not isinstance(value, str):
        raise TypeError("must be a string")
    candidate = value.replace("Z", "+00:00") if value.endswith("Z") else value
    try:
        datetime.fromisoformat(candidate)
    except ValueError as exc:
        raise ValueError("must be ISO-8601 timestamp") from exc
    return value


class PlanRequest(BaseModel):
    context: StrictStr
    current_time: StrictStr
    timezone: StrictStr
    variant: Literal["v1_naive", "v2_structured", "v3_agentic_repair"]

    @field_validator("current_time")
    @classmethod
    def validate_current_time(cls, value: str) -> str:
        return _parse_iso8601(value)


class PlanItem(BaseModel):
    task: StrictStr
    start_time: StrictStr
    end_time: StrictStr
    timebox_minutes: int = Field(ge=0)
    why: StrictStr

    @field_validator("start_time")
    @classmethod
    def validate_start_time(cls, value: str) -> str:
        return _parse_iso8601(value)

    @field_validator("end_time")
    @classmethod
    def validate_end_time(cls, value: str) -> str:
        return _parse_iso8601(value)


class ExtractedMetadata(BaseModel):
    detected_constraints: list[StrictStr]
    ground_truth_entities: list[StrictStr]
    task_keywords: list[StrictStr]


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
    variant: Literal["v1_naive", "v2_structured", "v3_agentic_repair"]


class PlanResponse(BaseModel):
    plan: list[PlanItem]
    extracted_metadata: ExtractedMetadata
    assumptions: list[StrictStr]
    questions: list[StrictStr]
    confidence: Literal["low", "medium", "high"]
    validation: PlanValidation
    debug: DebugInfo
