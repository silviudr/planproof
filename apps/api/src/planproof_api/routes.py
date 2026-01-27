from __future__ import annotations

import json
import re
import uuid

from fastapi import APIRouter

from dateutil import tz
from dateutil.parser import isoparse

from eval.constraints import check_constraints
from eval.feasibility import check_feasibility
from eval.hallucination import check_hallucinations
from eval.recall import calculate_recall
from eval.time_math import calculate_overlaps
from thefuzz import process, fuzz
from planproof_api.agent.extractor import extract_metadata
from planproof_api.agent.planner import PlanGenerationError, generate_plan
from planproof_api.agent.schemas import (
    DebugInfo,
    ExtractedMetadata,
    PlanItem,
    PlanRequest,
    PlanResponse,
    PlanValidation,
    ValidationMetrics,
)
from opik import opik_context
from planproof_api.observability.opik import opik

router = APIRouter()


def _derive_confidence(validation: PlanValidation) -> str:
    if validation.status == "fail":
        return "low"
    if (
        validation.metrics.keyword_recall_score >= 0.85
        and validation.metrics.hallucination_count == 0
        and validation.metrics.overlap_minutes == 0
    ):
        return "high"
    return "medium"


def _format_plan(plan: list[PlanItem]) -> str:
    return json.dumps([item.model_dump() for item in plan], indent=2)


def _normalize_timeboxes(plan: list[PlanItem]) -> list[PlanItem]:
    normalized: list[PlanItem] = []
    for item in plan:
        try:
            start_dt = isoparse(item.start_time)
            end_dt = isoparse(item.end_time)
        except (TypeError, ValueError):
            normalized.append(item)
            continue
        delta_minutes = int(round((end_dt - start_dt).total_seconds() / 60))
        if delta_minutes < 0:
            delta_minutes = 0
        if delta_minutes != item.timebox_minutes:
            normalized.append(
                item.model_copy(update={"timebox_minutes": delta_minutes})
            )
        else:
            normalized.append(item)
    return normalized


def _missing_keywords(plan: list[PlanItem], keywords: list[str]) -> list[str]:
    candidates: list[str] = []
    for item in plan:
        if item.task:
            candidates.append(item.task)
        if item.why:
            candidates.append(item.why)

    def _normalize(text: str) -> str:
        lowered = text.lower()
        stripped = re.sub(r"[^\w\s]", "", lowered)
        return re.sub(r"\s+", " ", stripped).strip()

    normalized_candidates = [_normalize(text) for text in candidates]
    missing: list[str] = []
    for keyword in keywords or []:
        if not keyword:
            continue
        normalized_keyword = _normalize(keyword)
        match = process.extractOne(
            normalized_keyword,
            normalized_candidates,
            scorer=fuzz.token_set_ratio,
        )
        if match is None or match[1] < 75:
            missing.append(keyword)
    return missing


@opik.track(name="initial_planning_step")
def _initial_planning_step(
    request: PlanRequest, metadata: ExtractedMetadata, current_time: str
) -> tuple[list[PlanItem], list[str], list[str]]:
    return generate_plan(
        request.context,
        metadata,
        current_time,
        request.timezone,
    )


@opik.track(name="validation_step")
def _validate_plan(
    plan: list[PlanItem],
    metadata: ExtractedMetadata,
    current_time: str,
    match_threshold: int = 80,
    variant: str | None = None,
) -> PlanValidation:
    """Validate a generated plan using deterministic checks.

    This is the "Validation" step of the Sandwich Architecture.

    Args:
        plan: Generated plan items to validate.
        metadata: Extracted metadata used for grounding.
        current_time: ISO-8601 timestamp representing "now".

    Returns:
        PlanValidation containing metrics and errors.
    """
    overlap_minutes = calculate_overlaps(plan)
    constraint_violation_count, constraint_errors = check_constraints(
        plan, metadata.temporal_constraints, current_time, overlap_minutes
    )
    hallucination_candidates = (
        (metadata.actionable_tasks or []) + (metadata.temporal_constraints or [])
    )
    hallucination_count = check_hallucinations(
        plan,
        metadata.ground_truth_entities,
        hallucination_candidates,
        match_threshold=match_threshold,
        variant=variant,
        detected_constraints=metadata.temporal_constraints,
    )
    keyword_recall_score = calculate_recall(
        plan, metadata.actionable_tasks
    )
    missing_keywords = _missing_keywords(plan, metadata.actionable_tasks)
    human_feasibility_flags = check_feasibility(plan)
    zero_duration_flags = 0

    errors: list[str] = list(constraint_errors)
    current_dt = isoparse(current_time)
    for item in plan:
        start_dt = isoparse(item.start_time)
        end_dt = isoparse(item.end_time)

        if start_dt < current_dt:
            constraint_violation_count += 1
            errors.append(f'Task "{item.task}" starts in the past.')

        duration_minutes = (end_dt - start_dt).total_seconds() / 60
        if abs(duration_minutes - item.timebox_minutes) > 1:
            errors.append(
                f'Task "{item.task}" timebox_minutes mismatch with duration.'
            )
        if start_dt == end_dt:
            zero_duration_flags += 1
            errors.append(
                f'Task "{item.task}" has zero duration. '
                "Every task must be at least 5 minutes."
            )

    if overlap_minutes > 0:
        errors.append("overlap_minutes > 0")
    if hallucination_count > 0:
        errors.append("hallucination_count > 0")
    if keyword_recall_score < 0.7:
        if missing_keywords:
            errors.append(f"Missing keywords: {', '.join(missing_keywords)}")
        else:
            errors.append("keyword_recall_score < 0.7")
    # if human_feasibility_flags > 0:
    #     errors.append("human_feasibility_flags > 0")

    status = "pass" if not errors else "fail"
    metrics = ValidationMetrics(
        constraint_violation_count=constraint_violation_count,
        overlap_minutes=overlap_minutes,
        hallucination_count=hallucination_count,
        keyword_recall_score=keyword_recall_score,
        human_feasibility_flags=human_feasibility_flags + zero_duration_flags,
    )
    try:
        opik_context.update_current_span(
            metadata={
                "constraint_violation_count": constraint_violation_count,
                "constraint_errors": constraint_errors,
                "overlap_minutes": overlap_minutes,
                "hallucination_count": hallucination_count,
                "keyword_recall_score": keyword_recall_score,
                "human_feasibility_flags": human_feasibility_flags
                + zero_duration_flags,
            }
        )
    except Exception:
        pass
    return PlanValidation(status=status, metrics=metrics, errors=errors)


@opik.track(name="repair_step")
def _repair_plan(
    request: PlanRequest,
    metadata: ExtractedMetadata,
    failed_plan: list[PlanItem],
    errors: list[str],
    current_time: str,
    keyword_recall_score: float,
    missing_keywords: list[str],
    constraint_violation_count: int,
) -> tuple[list[PlanItem], list[str], list[str]]:
    repair_prompt = (
        "Original context:\n"
        f"{request.context}\n\n"
        "Failed plan:\n"
        f"{_format_plan(failed_plan)}\n\n"
        "Detected constraints:\n"
        f"{json.dumps(metadata.temporal_constraints, indent=2)}\n\n"
        "Validation errors:\n"
        f"{json.dumps(errors, indent=2)}"
    )
    repair_prompt = (
        f"{repair_prompt}\n\n"
        "Constraint hierarchy:\n"
        "STRICT (0 Overlap): You are forbidden from overlapping tasks.\n"
        "STRICT (Availability): You must stay within 'Busy until' and "
        "'Leave by' windows.\n"
        "FLEXIBLE (Duration): If you cannot fit all tasks, shorten their "
        "duration. It is better to have a 15-minute 'Deep Work' block that "
        "fits, than a 60-minute one that overlaps."
    )
    repair_prompt = (
        f"{repair_prompt}\n\n"
        "YOU HAVE FAILED VALIDATION. Your task is to fix the plan.\n"
        "RULE 1: Constraints are absolute walls. If the user is busy until "
        "10 AM, NO task can start at 9:59 AM.\n"
        "RULE 2: Do not delete tasks to fix overlaps. Shorten them instead "
        "(e.g., change 60m to 15m)."
    )
    if constraint_violation_count > 0:
        repair_prompt = (
            f"{repair_prompt}\n\n"
            "URGENT: Your plan violates hard time boundaries. A task is "
            "scheduled during a \"Busy\" window. You MUST move this task "
            "later, even if the user mentioned an earlier time in their notes. "
            "The \"Busy Until\" constraint is more important than the task "
            "description."
        )
    if keyword_recall_score < 0.7:
        recall_percent = round(keyword_recall_score * 100)
        missing_list = ", ".join(missing_keywords) if missing_keywords else "unknown"
        repair_prompt = (
            f"{repair_prompt}\n\n"
            "CRITICAL FAILURE: You omitted requested tasks. "
            f"Your previous attempt only had a {recall_percent}% recall score. "
            f"You MUST include ALL requested tasks: {missing_list}. "
            "If they overlap, SHIFT their start times. DO NOT delete them."
        )
    return generate_plan(
        request.context,
        metadata,
        current_time,
        request.timezone,
        repair_prompt=repair_prompt,
    )


def _normalize_current_time(current_time: str, timezone: str) -> str:
    current_dt = isoparse(current_time)
    local_tz = tz.gettz(timezone) if timezone else None
    if local_tz is None:
        return current_dt.isoformat()
    if current_dt.tzinfo is None:
        current_dt = current_dt.replace(tzinfo=tz.UTC)
    local_dt = current_dt.astimezone(local_tz)
    return local_dt.isoformat()


@router.post("/api/plan", response_model=PlanResponse)
@opik.track(name="plan_request")
def create_plan(request: PlanRequest) -> PlanResponse:
    try:
        opik_context.update_current_trace(metadata={"variant": request.variant})
    except Exception:
        pass

    local_current_time = _normalize_current_time(
        request.current_time, request.timezone
    )
    metadata = extract_metadata(request.context)
    plan: list[PlanItem] = []
    assumptions: list[str] = []
    questions: list[str] = []
    repair_attempted = False
    repair_success = False
    validation: PlanValidation
    try:
        plan, assumptions, questions = _initial_planning_step(
            request, metadata, local_current_time
        )
    except PlanGenerationError as exc:
        validation = PlanValidation(
            status="fail",
            metrics=ValidationMetrics(
                constraint_violation_count=0,
                overlap_minutes=0,
                hallucination_count=0,
                keyword_recall_score=0.0,
                human_feasibility_flags=0,
            ),
            errors=[str(exc)],
        )
    else:
        plan = _normalize_timeboxes(plan)
        match_threshold = 70 if request.variant == "v3_agentic_repair" else 80
        validation = _validate_plan(
            plan, metadata, local_current_time, match_threshold, request.variant
        )
        missing_keywords = _missing_keywords(plan, metadata.actionable_tasks)
        if validation.status == "fail" and request.variant == "v3_agentic_repair":
            repair_attempted = True
            try:
                plan, assumptions, questions = _repair_plan(
                    request,
                    metadata,
                    plan,
                    validation.errors,
                    local_current_time,
                    validation.metrics.keyword_recall_score,
                    missing_keywords,
                    validation.metrics.constraint_violation_count,
                )
                plan = _normalize_timeboxes(plan)
                validation = _validate_plan(
                    plan,
                    metadata,
                    local_current_time,
                    match_threshold,
                    request.variant,
                )
                repair_success = validation.status == "pass"
            except PlanGenerationError as exc:
                validation = PlanValidation(
                    status="fail",
                    metrics=ValidationMetrics(
                        constraint_violation_count=0,
                        overlap_minutes=0,
                        hallucination_count=0,
                        keyword_recall_score=0.0,
                        human_feasibility_flags=0,
                    ),
                    errors=[str(exc)],
                )

    try:
        opik_context.update_current_trace(
            feedback_scores=[
                {
                    "name": "plan_validity",
                    "value": 1.0 if validation.status == "pass" else 0.0,
                }
            ]
        )
    except Exception:
        pass

    plan.sort(key=lambda item: item.start_time)

    trace_id = None
    try:
        trace_id = opik_context.get_current_trace_id()
    except Exception:
        trace_id = None
    if not trace_id:
        fallback_id = str(uuid.uuid4())
        try:
            opik_context.update_current_trace(tags=[fallback_id])
        except Exception:
            pass
        trace_id = fallback_id
    print(f"DEBUG: Opik Trace ID: {trace_id}")

    return PlanResponse(
        plan=plan,
        extracted_metadata=metadata,
        assumptions=assumptions,
        questions=questions,
        confidence=_derive_confidence(validation),
        validation=validation,
        debug=DebugInfo(
            repair_attempted=repair_attempted,
            repair_success=repair_success,
            variant=request.variant,
            trace_id=trace_id,
        ),
    )
