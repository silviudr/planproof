from __future__ import annotations

from typing import List, TYPE_CHECKING

from thefuzz import process

if TYPE_CHECKING:
    from planproof_api.agent.schemas import PlanItem


def calculate_recall(plan_items: List["PlanItem"], task_keywords: List[str]) -> float:
    keywords = [keyword for keyword in task_keywords if keyword]
    if not keywords:
        return 0.0

    candidates: list[str] = []
    for item in plan_items:
        if item.task:
            candidates.append(item.task.lower())
        if item.why:
            candidates.append(item.why.lower())

    if not candidates:
        return 0.0

    matched = 0
    for keyword in keywords:
        match = process.extractOne(
            keyword.lower(),
            candidates,
        )
        if match is not None and match[1] > 80:
            matched += 1

    return matched / len(keywords)
