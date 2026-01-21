from __future__ import annotations

from unittest.mock import patch

from planproof_api.agent.schemas import ExtractedMetadata, PlanItem, PlanRequest
from planproof_api.routes import create_plan


def _item(task: str, start_time: str, end_time: str, minutes: int) -> PlanItem:
    return PlanItem(
        task=task,
        start_time=start_time,
        end_time=end_time,
        timebox_minutes=minutes,
        why="",
    )


def test_repair_loop_success() -> None:
    request = PlanRequest(
        context="Plan my day with Alpha and Beta.",
        current_time="2025-01-18T08:00:00-05:00",
        timezone="America/New_York",
        variant="v3_agentic_repair",
    )
    metadata = ExtractedMetadata(
        detected_constraints=[],
        ground_truth_entities=["alpha", "beta"],
        task_keywords=["alpha", "beta"],
    )

    failing_plan = [
        _item("Alpha", "2025-01-18T09:00:00-05:00", "2025-01-18T10:00:00-05:00", 60),
        _item("Beta", "2025-01-18T09:30:00-05:00", "2025-01-18T10:30:00-05:00", 60),
    ]
    repaired_plan = [
        _item("Alpha", "2025-01-18T09:00:00-05:00", "2025-01-18T10:00:00-05:00", 60),
        _item("Beta", "2025-01-18T10:15:00-05:00", "2025-01-18T11:15:00-05:00", 60),
    ]

    with patch("planproof_api.routes.extract_metadata", return_value=metadata), patch(
        "planproof_api.routes.generate_plan"
    ) as mock_generate:
        mock_generate.side_effect = [
            (failing_plan, ["assumed focus block"], ["Any other tasks?"]),
            (repaired_plan, ["assumed focus block"], ["Any other tasks?"]),
        ]

        response = create_plan(request)

    assert response.debug.repair_attempted is True
    assert response.debug.repair_success is True
    assert mock_generate.call_count == 2
    assert "repair_prompt" in mock_generate.call_args_list[1].kwargs
