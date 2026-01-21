from __future__ import annotations

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


@opik.track(name="validate_plan")
def _validate_plan(
    plan: list[PlanItem], metadata: ExtractedMetadata, current_time: str
) -> PlanValidation:
    """Validate a generated plan using deterministic checks.

    Args:
        plan: Generated plan items to validate.
        metadata: Extracted metadata used for grounding.
        current_time: ISO-8601 timestamp representing "now".

    Returns:
        PlanValidation containing metrics and errors.
    """
    constraint_violation_count = check_constraints(
        plan, metadata.detected_constraints
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
    if human_feasibility_flags > 0:
        errors.append("human_feasibility_flags > 0")

    status = "pass" if not errors else "fail"
    metrics = ValidationMetrics(
        constraint_violation_count=constraint_violation_count,
        overlap_minutes=overlap_minutes,
        hallucination_count=hallucination_count,
        keyword_recall_score=keyword_recall_score,
        human_feasibility_flags=human_feasibility_flags,
    )
    return PlanValidation(status=status, metrics=metrics, errors=errors)


@router.post("/api/plan", response_model=PlanResponse)
def create_plan(request: PlanRequest) -> PlanResponse:
    metadata = extract_metadata(request.context)
    try:
        plan, assumptions, questions = generate_plan(
            request.context, metadata, request.current_time, request.timezone
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

    return PlanResponse(
        plan=plan,
        extracted_metadata=metadata,
        assumptions=assumptions,
        questions=questions,
        confidence=_derive_confidence(validation),
        validation=validation,
        debug=DebugInfo(
            repair_attempted=False,
            repair_success=False,
            variant=request.variant,
        ),
    )
