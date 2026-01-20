from __future__ import annotations

from fastapi import APIRouter

from eval.hallucination import check_hallucinations
from eval.recall import calculate_recall
from eval.time_math import calculate_overlaps
from planproof_api.agent.extractor import extract_metadata
from planproof_api.agent.planner import generate_plan
from planproof_api.agent.schemas import (
    DebugInfo,
    PlanRequest,
    PlanResponse,
    PlanValidation,
    ValidationMetrics,
)
from planproof_api.observability.opik import opik

router = APIRouter()


@opik.track
def _validate_plan(plan, metadata) -> PlanValidation:
    constraint_violation_count = 0
    overlap_minutes = calculate_overlaps(plan)
    hallucination_count = check_hallucinations(
        plan, metadata.ground_truth_entities, metadata.task_keywords
    )
    keyword_recall_score = calculate_recall(plan, metadata.task_keywords)
    human_feasibility_flags = 0

    errors: list[str] = []
    if constraint_violation_count > 0:
        errors.append("constraint_violation_count > 0")
    if overlap_minutes > 0:
        errors.append("overlap_minutes > 0")
    if hallucination_count > 0:
        errors.append("hallucination_count > 0")
    if keyword_recall_score < 0.7:
        errors.append("keyword_recall_score < 0.7")

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
    plan = generate_plan(request.context, metadata)
    validation = _validate_plan(plan, metadata)

    return PlanResponse(
        plan=plan,
        extracted_metadata=metadata,
        assumptions=[],
        questions=[],
        confidence="low",
        validation=validation,
        debug=DebugInfo(
            repair_attempted=False,
            repair_success=False,
            variant=request.variant,
        ),
    )
