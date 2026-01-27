from __future__ import annotations

import re
from typing import List, TYPE_CHECKING


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
    "call",
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
    "later",
    "earlier",
    "between",
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
    "reschedule",
    "rescheduled",
    "shifting",
    "conflict",
    "resolved",
    "adjusting",
    "adjusted",
    "shifted",
    "allocated",
    "allocation",
    "remaining",
    "timeframe",
    "specified",
    "overlap",
    "constraint",
    "modified",
    "original",
    "block",
    "slot",
    "moved",
}

_PRODUCTIVITY_WHITELIST = {
    "attend",
    "meeting",
    "scheduled",
    "shifted",
    "adjusted",
    "block",
    "session",
    "duration",
    "time",
    "pm",
    "am",
    "task",
    "prepare",
    "ensure",
    "within",
    "following",
    "prior",
    "another",
    "second",
    "leaving",
}

_REPAIR_META_WORDS = {
    "reschedule",
    "rescheduled",
    "shifting",
    "adjusted",
    "shifted",
    "adjusting",
    "modified",
    "original",
    "conflict",
    "resolved",
    "break",
    "gap",
    "overlap",
    "fixed",
    "allocated",
    "allocation",
    "remaining",
    "timeframe",
    "specified",
}


def _is_high_entropy(token: str) -> bool:
    if any(char.isdigit() for char in token):
        return True
    if "-" in token or "." in token:
        return True
    return len(token) >= 4


def _extract_significant_tokens(text: str) -> set[str]:
    words: set[str] = set()
    for match in _WORD_PATTERN.finditer(text):
        token = match.group(0)
        token_lower = token.lower()
        if token_lower in _COMMON_VERBS | _STOP_WORDS:
            continue
        if token_lower in _PRODUCTIVITY_WHITELIST:
            continue
        if len(token) <= 3:
            continue
        if not _is_high_entropy(token_lower):
            continue
        words.add(token_lower)

    time_tokens = {match.group(0).lower() for match in _TIME_PATTERN.finditer(text)}
    return words | time_tokens


_PROPER_NOUN_PATTERN = re.compile(r"\b[A-Z][a-zA-Z0-9\-\.]*\b")


def check_hallucinations(
    plan_items: List["PlanItem"],
    ground_truth_entities: List[str],
    _task_keywords: List[str],
    _match_threshold: int = 80,
    _variant: str | None = None,
    _detected_constraints: List[str] | None = None,
    **_: object,
) -> int:
    tokens: set[str] = set()
    for item in plan_items:
        if not item.task:
            continue
        for token in _PROPER_NOUN_PATTERN.findall(item.task):
            token_lower = token.lower()
            if token_lower in _COMMON_VERBS | _STOP_WORDS | _PRODUCTIVITY_WHITELIST:
                continue
            tokens.add(token)

    if not tokens:
        return 0

    if not ground_truth_entities:
        return len(tokens)

    entities = [entity.lower() for entity in ground_truth_entities if entity]
    hallucination_count = 0
    for token in tokens:
        token_lower = token.lower()
        if not any(token_lower in entity for entity in entities):
            hallucination_count += 1

    return hallucination_count


def get_hallucinated_tokens(
    plan_items: List["PlanItem"],
    ground_truth_entities: List[str],
    _task_keywords: List[str],
    _match_threshold: int = 80,
    _variant: str | None = None,
    _detected_constraints: List[str] | None = None,
    **_: object,
) -> list[str]:
    tokens: set[str] = set()
    for item in plan_items:
        if not item.task:
            continue
        for token in _PROPER_NOUN_PATTERN.findall(item.task):
            token_lower = token.lower()
            if token_lower in _COMMON_VERBS | _STOP_WORDS | _PRODUCTIVITY_WHITELIST:
                continue
            tokens.add(token)

    if not tokens:
        return []

    if not ground_truth_entities:
        return sorted(tokens)

    entities = [entity.lower() for entity in ground_truth_entities if entity]
    flagged: list[str] = []
    for token in tokens:
        token_lower = token.lower()
        if not any(token_lower in entity for entity in entities):
            print(f"DEBUG HALLUCINATION: Word '{token}' flagged (No ground truth)")
            flagged.append(token)

    return sorted(flagged)
