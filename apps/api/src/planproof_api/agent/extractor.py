from __future__ import annotations

import json
import re

from openai import OpenAI

from planproof_api.agent.schemas import ExtractedMetadata
from planproof_api.observability.opik import opik

_SYSTEM_PROMPT = (
    "SYSTEM: You are a stateless extractor. Analyze ONLY the text provided "
    "in the CURRENT request. Do not include entities or keywords from any "
    "previous context. If the text does not mention milk, DO NOT include "
    "milk in the output. "
    "You are a strict JSON extractor. Return ONLY valid JSON with keys: "
    "actionable_tasks, temporal_constraints, ground_truth_entities. "
    "All values must be arrays of strings. No extra keys, no commentary. "
    "Analyze the user context and categorize every meaningful phrase into one "
    "of two roles: ACTIONABLE_TASK (a discrete activity that requires a time "
    "block, e.g., 'buy milk', 'deep work') or TEMPORAL_CONSTRAINT (a boundary, "
    "deadline, or fixed point that limits when tasks can happen, e.g., 'Leave "
    "by 5 PM', 'Busy until 10 AM'). "
    "CRITICAL: Do NOT put a Temporal Constraint into the Actionable Task list. "
    "If the user says 'Leave by 5 PM', that is a constraint, NOT a task to be "
    "scheduled. Do not create an actionable task called 'Leave'. "
    "If multiple tasks are requested at the same time, include the time in "
    "temporal_constraints for EACH task separately (e.g., [\"1 PM\", \"1 PM\"]). "
    "Differentiate between Hard Deadlines (Leave by, Must end by) and Task "
    "Preferences (Work from 4 to 6). If a deadline makes a preference "
    "impossible, the deadline takes absolute priority. "
    "Only extract items explicitly present in the provided context. "
    "Do not invent requirements."
)

_PROJECT_PREFIX = re.compile(r"^\s*project\s+", re.IGNORECASE)
_PROJECT_SUFFIX = re.compile(r"\s+project\s*$", re.IGNORECASE)
# Generic nouns that should not be treated as standalone entities.
# Keep this list tight to avoid suppressing real names.
_GENERIC_ENTITY_WORDS = {
    "project",
    "initiative",
    "task",
    "plan",
    "work",
    "assignment",
    "deliverable",
    "meeting",
    "call",
    "email",
    "report",
    "document",
    "notes",
    "invoice",
    "calendar",
    "errand",
    "groceries",
    "milk",
    "laundry",
}


def _normalize_entities(entities: list[str]) -> list[str]:
    normalized: list[str] = []
    seen: set[str] = set()

    for entity in entities:
        if not entity:
            continue
        base = entity.strip()
        if not base:
            continue
        if base.lower() not in _GENERIC_ENTITY_WORDS and base not in seen:
            normalized.append(base)
            seen.add(base)

        without_prefix = _PROJECT_PREFIX.sub("", base).strip()
        without_suffix = _PROJECT_SUFFIX.sub("", base).strip()

        for candidate in {without_prefix, without_suffix}:
            if (
                candidate
                and candidate.lower() not in _GENERIC_ENTITY_WORDS
                and candidate not in seen
            ):
                normalized.append(candidate)
                seen.add(candidate)

    return normalized


@opik.track(name="extraction_step")
def extract_metadata(context: str) -> ExtractedMetadata:
    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": f"Context:\n{context}"},
        ],
        response_format={"type": "json_object"},
        temperature=0,
    )
    content = response.choices[0].message.content or "{}"
    raw = json.loads(content)
    data: dict[str, list[str]] = {
        "temporal_constraints": [],
        "ground_truth_entities": [],
        "actionable_tasks": [],
    }
    if isinstance(raw, dict):
        constraints = raw.get("temporal_constraints")
        entities = raw.get("ground_truth_entities")
        keywords = raw.get("actionable_tasks")
        if isinstance(constraints, list):
            data["temporal_constraints"] = list(constraints)
        if isinstance(entities, list):
            data["ground_truth_entities"] = _normalize_entities(list(entities))
        if isinstance(keywords, list):
            data["actionable_tasks"] = list(keywords)

    if data["actionable_tasks"] and data["temporal_constraints"]:
        boundary_words = {"leave", "until", "by", "before"}
        constraints_text = " ".join(data["temporal_constraints"]).lower()
        data["actionable_tasks"] = [
            keyword
            for keyword in data["actionable_tasks"]
            if not (
                keyword
                and keyword.lower() in boundary_words
                and keyword.lower() in constraints_text
            )
        ]

    return ExtractedMetadata(**data)
