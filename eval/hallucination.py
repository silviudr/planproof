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
    "run",
    "slot",
    "period",
}

_SAFETY_WORDS = {
    "scheduled",
    "specified",
    "required",
    "planned",
    "needed",
    "intended",
    "approximate",
    "assigned",
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


def _normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower().strip())


def check_hallucinations(
    plan_items: List["PlanItem"],
    ground_truth_entities: List[str],
    task_keywords: List[str],
    _match_threshold: int = 80,
    _variant: str | None = None,
    detected_constraints: List[str] | None = None,
    user_context: str | None = None,
    **_: object,
) -> int:
    context_text = _normalize_text(user_context or "")
    hallucination_count = 0

    for item in plan_items:
        if not item.task:
            continue
        for token in _WORD_PATTERN.findall(item.task):
            token_lower = token.lower()
            if len(token_lower) <= 4:
                continue
            if (
                token_lower
                in _COMMON_VERBS | _STOP_WORDS | _PRODUCTIVITY_WHITELIST | _SAFETY_WORDS
            ):
                continue
            if token_lower in context_text:
                continue
            hallucination_count += 1

    return hallucination_count


def get_hallucinated_tokens(
    plan_items: List["PlanItem"],
    ground_truth_entities: List[str],
    task_keywords: List[str],
    _match_threshold: int = 80,
    _variant: str | None = None,
    detected_constraints: List[str] | None = None,
    user_context: str | None = None,
    **_: object,
) -> list[str]:
    context_text = _normalize_text(user_context or "")
    flagged: list[str] = []

    for item in plan_items:
        if not item.task:
            continue
        for token in _WORD_PATTERN.findall(item.task):
            token_lower = token.lower()
            if len(token_lower) <= 4:
                continue
            if (
                token_lower
                in _COMMON_VERBS | _STOP_WORDS | _PRODUCTIVITY_WHITELIST | _SAFETY_WORDS
            ):
                continue
            if token_lower in context_text:
                continue
            print(f"DEBUG HALLUCINATION: Word '{token}' flagged (No context)")
            flagged.append(token)

    return sorted(set(flagged))
