from __future__ import annotations

import json
import re

from openai import OpenAI

from planproof_api.agent.schemas import ExtractedMetadata
from planproof_api.observability.opik import opik

_SYSTEM_PROMPT = (
    "You are a strict JSON extractor. Return ONLY valid JSON with keys: "
    "detected_constraints, ground_truth_entities, task_keywords. "
    "All values must be arrays of strings. No extra keys, no commentary."
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


@opik.track
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
    data = json.loads(content)
    if isinstance(data, dict):
        entities = data.get("ground_truth_entities")
        if isinstance(entities, list):
            data["ground_truth_entities"] = _normalize_entities(entities)

    return ExtractedMetadata(**data)
