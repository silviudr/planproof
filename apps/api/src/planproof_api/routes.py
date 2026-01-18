from __future__ import annotations

from fastapi import APIRouter

from planproof_api.agent.schemas import (
    DebugInfo,
    PlanItem,
    PlanRequest,
    PlanResponse,
    PlanValidation,
    ValidationMetrics,
)

router = APIRouter()


@router.post("/api/plan", response_model=PlanResponse)
def create_plan(request: PlanRequest) -> PlanResponse:
    return PlanResponse(
        plan=[
            PlanItem(
                task="Review inbox",
                start_time="2025-01-18T09:00:00-05:00",
                end_time="2025-01-18T09:30:00-05:00",
                timebox_minutes=30,
                why="Quick triage to prioritize the day.",
            ),
            PlanItem(
                task="Write project update",
                start_time="2025-01-18T09:45:00-05:00",
                end_time="2025-01-18T11:15:00-05:00",
                timebox_minutes=90,
                why="Draft and polish the weekly update.",
            ),
            PlanItem(
                task="Client check-in call",
                start_time="2025-01-18T13:00:00-05:00",
                end_time="2025-01-18T13:30:00-05:00",
                timebox_minutes=30,
                why="Confirm next steps and deliverables.",
            ),
        ],
        validation=PlanValidation(
            status="pass",
            metrics=ValidationMetrics(
                constraint_violation_count=1,
                overlap_minutes=15,
                hallucination_count=2,
                keyword_recall_score=0.75,
                human_feasibility_flags=1,
            ),
            errors=[],
        ),
        debug=DebugInfo(
            repair_attempted=False,
            repair_success=False,
            variant="v1_naive",
        ),
    )
