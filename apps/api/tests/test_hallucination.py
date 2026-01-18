from __future__ import annotations

from planproof_api.agent.schemas import PlanItem

from eval.hallucination import check_hallucinations


def _item(task: str, why: str) -> PlanItem:
    return PlanItem(
        task=task,
        start_time="2025-01-18T09:00:00-05:00",
        end_time="2025-01-18T10:00:00-05:00",
        timebox_minutes=0,
        why=why,
    )


def test_check_hallucinations_fuzzy_match() -> None:
    ground_truth = ["Project Apollo", "Sarah Jones"]
    task_keywords = ["project", "apollo"]
    items = [_item("Meeting with Sara", "discuss Project Apollo")]

    assert check_hallucinations(items, ground_truth, task_keywords) == 0


def test_check_hallucinations_missing_entity() -> None:
    ground_truth = ["Project Apollo", "Sarah Jones"]
    task_keywords = ["project", "apollo"]
    items = [_item("Call with Mike", "follow up")]

    assert check_hallucinations(items, ground_truth, task_keywords) == 1


def test_check_hallucinations_mundane_activity() -> None:
    ground_truth = []
    task_keywords = ["buy", "milk"]
    items = [_item("Wash car", "ok")]

    assert check_hallucinations(items, ground_truth, task_keywords) == 1
