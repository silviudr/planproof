from __future__ import annotations

import re
from typing import List, TYPE_CHECKING

from thefuzz import process

if TYPE_CHECKING:
    from planproof_api.agent.schemas import PlanItem

_WORD_PATTERN = re.compile(r"\b[a-zA-Z]{3,}\b")
_COMMON_VERBS = {
    "do",
    "make",
    "go",
    "buy",
    "get",
    "call",
    "meet",
    "meeting",
    "email",
    "review",
    "write",
    "draft",
    "plan",
    "schedule",
    "check",
    "follow",
    "send",
    "talk",
    "sync",
    "work",
    "start",
    "finish",
    "prepare",
    "update",
    "read",
    "discuss",
    "coordinate",
    "book",
    "travel",
    "wash",
}
_COMMON_WORDS = {
    "the",
    "and",
    "with",
    "for",
    "from",
    "into",
    "onto",
    "about",
    "over",
    "under",
    "after",
    "before",
    "between",
    "during",
    "while",
    "this",
    "that",
    "these",
    "those",
}


def _extract_significant_words(text: str) -> set[str]:
    words = {word.lower() for word in _WORD_PATTERN.findall(text)}
    return {word for word in words if word not in _COMMON_VERBS | _COMMON_WORDS}


def check_hallucinations(
    plan_items: List["PlanItem"],
    ground_truth_entities: List[str],
    task_keywords: List[str],
) -> int:
    words: set[str] = set()
    for item in plan_items:
        words.update(_extract_significant_words(item.task))
        words.update(_extract_significant_words(item.why))

    if not words:
        return 0

    candidates = [
        candidate.lower()
        for candidate in (ground_truth_entities or []) + (task_keywords or [])
        if candidate
    ]
    if not candidates:
        return len(words)

    hallucination_count = 0
    for word in words:
        match = process.extractOne(word, candidates)
        if match is None or match[1] <= 80:
            hallucination_count += 1

    return hallucination_count
