from __future__ import annotations

import re
from typing import List, TYPE_CHECKING

from thefuzz import process

if TYPE_CHECKING:
    from planproof_api.agent.schemas import PlanItem

_WORD_PATTERN = re.compile(r"\b[a-zA-Z0-9\-\.]{2,}\b")
_TIME_PATTERN = re.compile(
    r"\b(?:[01]?\d|2[0-3]):[0-5]\d\b|\b\d{1,2}\s?(?:am|pm)\b",
    re.IGNORECASE,
)
_COMMON_VERBS = {
    "do",
    "make",
    "go",
    "buy",
    "get",
    "start",
    "finish",
    "ensure",
    "prepare",
    "meeting",
    "scheduled",
    "after",
    "attend",
    "take",
    "need",
    "complete",
    "prioritize",
    "stay",
}
_STOP_WORDS = {
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
    "at",
    "before",
    "between",
    "during",
    "in",
    "while",
    "on",
    "of",
    "to",
    "by",
    "this",
    "that",
    "these",
    "those",
    "ready",
    "upcoming",
    "second",
    "approximately",
    "organized",
    "starts",
    "following",
    "during",
    "within",
    "milk",
    "another",
    "first",
    "prior",
    "scheduled",
    "planned",
    "meeting",
    "ensure",
    "ready",
    "upcoming",
    "attend",
    "take",
    "approximately",
    "complete",
    "prioritize",
    "organized",
    "stay",
    "second",
    "following",
    "after",
    "need",
    "buy",
}


def _is_high_entropy(token: str) -> bool:
    if any(char.isdigit() for char in token):
        return True
    if "-" in token or "." in token:
        return True
    return len(token) >= 3


def _extract_significant_tokens(text: str) -> set[str]:
    words = {word.lower() for word in _WORD_PATTERN.findall(text)}
    time_tokens = {match.group(0).lower() for match in _TIME_PATTERN.finditer(text)}
    significant_words = {
        word
        for word in words
        if word not in _COMMON_VERBS | _STOP_WORDS and _is_high_entropy(word)
    }
    return significant_words | time_tokens


def check_hallucinations(
    plan_items: List["PlanItem"],
    ground_truth_entities: List[str],
    task_keywords: List[str],
) -> int:
    tokens: set[str] = set()
    for item in plan_items:
        tokens.update(_extract_significant_tokens(item.task))
        tokens.update(_extract_significant_tokens(item.why))

    if not tokens:
        return 0

    candidates = [
        candidate.lower()
        for candidate in (ground_truth_entities or []) + (task_keywords or [])
        if candidate
    ]
    if not candidates:
        return len(tokens)

    hallucination_count = 0
    for token in tokens:
        match = process.extractOne(token, candidates)
        if match is None or match[1] <= 80:
            hallucination_count += 1

    return hallucination_count
