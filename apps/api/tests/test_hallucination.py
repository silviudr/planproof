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
    task_keywords = ["project", "apollo", "meeting"]
    items = [_item("Meeting with Sarah", "Project Apollo")]

    assert check_hallucinations(items, ground_truth, task_keywords) == 0


def test_check_hallucinations_missing_entity() -> None:
    ground_truth = ["Project Apollo", "Sarah Jones"]
    task_keywords = ["call"]
    items = [_item("Call with Mike", "")]

    assert check_hallucinations(items, ground_truth, task_keywords) == 1


def test_check_hallucinations_mundane_activity() -> None:
    ground_truth = []
    task_keywords = ["buy", "milk"]
    items = [_item("Wash car", "")]

    assert check_hallucinations(items, ground_truth, task_keywords) == 1


def test_check_hallucinations_empty_plan_items() -> None:
    assert check_hallucinations([], ["Project Apollo"], ["project"]) == 0


def test_check_hallucinations_empty_fields() -> None:
    items = [_item("", "")]

    assert check_hallucinations(items, ["Project Apollo"], ["project"]) == 0


def test_check_hallucinations_multiple_missing_words() -> None:
    items = [
        _item("Alpha Beta", ""),
        _item("Gamma", ""),
    ]

    assert check_hallucinations(items, [], []) == 3


def test_check_hallucinations_exact_match() -> None:
    items = [_item("Mike", "")]

    assert check_hallucinations(items, ["Mike"], []) == 0


def test_check_hallucinations_case_insensitive_match() -> None:
    items = [_item("MIKE", "")]

    assert check_hallucinations(items, ["mike"], []) == 0


def test_check_hallucinations_ai_keyword() -> None:
    ground_truth = []
    task_keywords = ["AI", "report"]
    items = [_item("AI report", "")]

    assert check_hallucinations(items, ground_truth, task_keywords) == 1
