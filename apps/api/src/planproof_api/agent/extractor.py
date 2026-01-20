from __future__ import annotations

import json
import re

from openai import OpenAI

from planproof_api.agent.schemas import ExtractedMetadata

_SYSTEM_PROMPT = (
    "You are a strict JSON extractor. Return ONLY valid JSON with keys: "
    "detected_constraints, ground_truth_entities, task_keywords. "
    "All values must be arrays of strings. No extra keys, no commentary."
)

_PROJECT_PREFIX = re.compile(r"^\s*project\s+", re.IGNORECASE)
_PROJECT_SUFFIX = re.compile(r"\s+project\s*$", re.IGNORECASE)


def _normalize_entities(entities: list[str]) -> list[str]:
    normalized: list[str] = []
    seen: set[str] = set()

    for entity in entities:
        if not entity:
            continue
        base = entity.strip()
        if base and base not in seen:
            normalized.append(base)
            seen.add(base)

        without_prefix = _PROJECT_PREFIX.sub("", base).strip()
        without_suffix = _PROJECT_SUFFIX.sub("", base).strip()

        for candidate in {without_prefix, without_suffix}:
            if candidate and candidate.lower() != "project" and candidate not in seen:
                normalized.append(candidate)
                seen.add(candidate)

    return normalized


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
