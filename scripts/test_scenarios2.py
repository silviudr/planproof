from __future__ import annotations

import requests

from opik import Opik
from opik.evaluation import evaluate
from opik.evaluation.metrics import BaseMetric, score_result


URL = "http://localhost:10000/api/plan"
DATASET_NAME = "planproof_scenarios"

SCENARIOS = [
    {
        "context": "The current time is 8:00 AM. I have a meeting at 10:00 AM for 1 hour. I need to buy milk at 2:00 PM for 30 minutes. My day ends at 5:00 PM.",
        "label": "Control Case: Expected pass for baseline"
    },
    {
        "context": "The current time is 8:00 AM. I have a meeting at 10:00 AM for 1 hour. I need to buy milk at 2:00 PM for 30 minutes. My day ends at 5:00 PM.",
        "label": "Control Case: Expected pass for baseline"
    },
    {
        "context": "Meeting at 1 PM, meeting at 1 PM, buy milk",
        "label": "Overlap conflict",
    },
    {
        "context": "Busy until 10 AM, meeting at 9 AM, write report",
        "label": "Start-gate conflict",
    },
    {
        "context": "Leave by 5 PM, deep work from 4 PM to 6 PM",
        "label": "Deadline conflict",
    },
    {
        "context": "Meeting at 1 PM, buy milk, leave at 5 PM",
        "label": "Simple mixed tasks",
    },
    {
        "context": "Call Sarah about Apollo at 2 PM, buy groceries",
        "label": "Entity grounding",
    },
    {
        "context": "Write report, review Q4 plan, respond to emails",
        "label": "No explicit times",
    },
]


class PassMetric(BaseMetric):
    def score(
        self, plan_validity: float, **_: object
    ) -> score_result.ScoreResult:
        value = float(plan_validity)
        return score_result.ScoreResult(name=self.name, value=value)


def _send_request(context: str, variant: str) -> dict:
    response = requests.post(
        URL,
        json={
            "context": context,
            "current_time": "2026-01-25T11:00:00Z",
            "timezone": "America/New_York",
            "variant": variant,
        },
        timeout=30,
    )
    response.raise_for_status()
    payload = response.json()
    status = str(payload.get("validation", {}).get("status", "")).lower()
    payload["plan_validity"] = 1 if status == "pass" else 0
    return payload


def _evaluation_task_factory(variant: str):
    def evaluation_task(item: dict) -> dict:
        payload = _send_request(item["context"], variant)
        payload["scenario_label"] = item.get("label", "")
        return payload

    return evaluation_task


def _build_dataset(items: list[dict]) -> object:
    client = Opik()
    dataset = client.get_or_create_dataset(DATASET_NAME)
    dataset.insert(items)
    return dataset


if __name__ == "__main__":
    dataset = _build_dataset(SCENARIOS)
    metric = PassMetric(name="plan_validity")

    evaluate(
        dataset=dataset,
        task=_evaluation_task_factory("v1_naive"),
        scoring_metrics=[metric],
        experiment_name="v1_baseline",
    )

    evaluate(
        dataset=dataset,
        task=_evaluation_task_factory("v3_agentic_repair"),
        scoring_metrics=[metric],
        experiment_name="v3_with_repair",
    )
