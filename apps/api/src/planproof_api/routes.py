from __future__ import annotations

import json

from fastapi import APIRouter

from dateutil.parser import isoparse

from eval.constraints import check_constraints
from eval.feasibility import check_feasibility
from eval.hallucination import check_hallucinations
from eval.recall import calculate_recall
from eval.time_math import calculate_overlaps
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


@opik.track(name="initial_planning_step")
def _initial_planning_step(
    request: PlanRequest, metadata: ExtractedMetadata
) -> tuple[list[PlanItem], list[str], list[str]]:
    return generate_plan(
        request.context,
        metadata,
        request.current_time,
        request.timezone,
    )


@opik.track(name="validation_step")
def _validate_plan(
    plan: list[PlanItem], metadata: ExtractedMetadata, current_time: str
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
    constraint_violation_count = check_constraints(
        plan, metadata.detected_constraints, current_time
    )
    overlap_minutes = calculate_overlaps(plan)
    hallucination_count = check_hallucinations(
        plan, metadata.ground_truth_entities, metadata.task_keywords
    )
    keyword_recall_score = calculate_recall(plan, metadata.task_keywords)
    human_feasibility_flags = check_feasibility(plan)

    errors: list[str] = []
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

    if constraint_violation_count > 0:
        errors.append("constraint_violation_count > 0")
    if overlap_minutes > 0:
        errors.append("overlap_minutes > 0")
    if hallucination_count > 0:
        errors.append("hallucination_count > 0")
    if keyword_recall_score < 0.7:
        errors.append("keyword_recall_score < 0.7")
    # if human_feasibility_flags > 0:
    #     errors.append("human_feasibility_flags > 0")

    status = "pass" if not errors else "fail"
    metrics = ValidationMetrics(
        constraint_violation_count=constraint_violation_count,
        overlap_minutes=overlap_minutes,
        hallucination_count=hallucination_count,
        keyword_recall_score=keyword_recall_score,
        human_feasibility_flags=human_feasibility_flags,
    )
    try:
        opik_context.update_current_span(
            metadata={
                "constraint_violation_count": constraint_violation_count,
                "overlap_minutes": overlap_minutes,
                "hallucination_count": hallucination_count,
                "keyword_recall_score": keyword_recall_score,
                "human_feasibility_flags": human_feasibility_flags,
            }
        )
    except Exception:
        pass
    return PlanValidation(status=status, metrics=metrics, errors=errors)


@opik.track(name="repair_step")
def _repair_plan(
    request: PlanRequest, metadata: ExtractedMetadata, failed_plan: list[PlanItem], errors: list[str]
) -> tuple[list[PlanItem], list[str], list[str]]:
    repair_prompt = (
        "Original context:\n"
        f"{request.context}\n\n"
        "Failed plan:\n"
        f"{_format_plan(failed_plan)}\n\n"
        "Validation errors:\n"
        f"{json.dumps(errors, indent=2)}"
    )
    return generate_plan(
        request.context,
        metadata,
        request.current_time,
        request.timezone,
        repair_prompt=repair_prompt,
    )


@router.post("/api/plan", response_model=PlanResponse)
@opik.track(name="plan_request")
def create_plan(request: PlanRequest) -> PlanResponse:
    try:
        opik_context.update_current_trace(metadata={"variant": request.variant})
    except Exception:
        pass

    metadata = extract_metadata(request.context)
    print(
        f"DEBUG: Extractor produced {len(metadata.task_keywords)} keywords"
    )
    try:
        plan, assumptions, questions = _initial_planning_step(request, metadata)
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
        return PlanResponse(
            plan=[],
            extracted_metadata=metadata,
            assumptions=[],
            questions=[],
            confidence=_derive_confidence(validation),
            validation=validation,
            debug=DebugInfo(
                repair_attempted=False,
                repair_success=False,
                variant=request.variant,
            ),
        )

    validation = _validate_plan(plan, metadata, request.current_time)
    print(
        "DEBUG: Validation - Overlaps: "
        f"{validation.metrics.overlap_minutes}, "
        "Recall: "
        f"{validation.metrics.keyword_recall_score}"
    )
    repair_attempted = False
    repair_success = False

    if validation.status == "fail":
        repair_attempted = True
        try:
            plan, assumptions, questions = _repair_plan(
                request, metadata, plan, validation.errors
            )
            validation = _validate_plan(plan, metadata, request.current_time)
            repair_success = validation.status == "pass"
            print(
                "DEBUG: Validation (repair) - Overlaps: "
                f"{validation.metrics.overlap_minutes}, "
                "Recall: "
                f"{validation.metrics.keyword_recall_score}"
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
    trace_id = "No Trace"
    try:
        trace_id = opik_context.get_current_trace_id() or "No Trace"
    except Exception:
        pass
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
        ),
    )
