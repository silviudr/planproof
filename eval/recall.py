from __future__ import annotations

import re
from typing import List, TYPE_CHECKING

from thefuzz import process
from thefuzz import fuzz

if TYPE_CHECKING:
    from planproof_api.agent.schemas import PlanItem


def calculate_recall(
    plan_items: List["PlanItem"],
    actionable_tasks: List[str],
) -> float:
    keywords = [keyword for keyword in actionable_tasks if keyword]
    if not keywords:
        return 0.0

    candidates: list[str] = []
    for item in plan_items:
        if item.task:
            candidates.append(item.task)
        if item.why:
            candidates.append(item.why)

    if not candidates:
        return 0.0

    def _normalize(text: str) -> str:
        lowered = text.lower()
        stripped = re.sub(r"[^\w\s]", "", lowered)
        return re.sub(r"\s+", " ", stripped).strip()

    normalized_candidates = [_normalize(text) for text in candidates]
    matched = 0
    for keyword in keywords:
        normalized_keyword = _normalize(keyword)
        match = process.extractOne(
            normalized_keyword,
            normalized_candidates,
            scorer=fuzz.token_set_ratio,
        )
        if match is not None and match[1] >= 75:
            matched += 1
        else:
            print(
                f"DEBUG RECALL: Keyword '{keyword}' not found in plan tokens "
                f"{normalized_candidates}"
            )

    return matched / len(keywords)
