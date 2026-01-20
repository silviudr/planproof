from __future__ import annotations

import json

from openai import OpenAI

from planproof_api.agent.schemas import ExtractedMetadata, PlanItem
from planproof_api.observability.opik import opik

_SYSTEM_PROMPT = (
    "You are a planning assistant. Return ONLY valid JSON with a top-level "
    "'plan' array. Each item must include: task, start_time, end_time, "
    "timebox_minutes, why. Use ISO-8601 timestamps."
)


@opik.track
def generate_plan(context: str, metadata: ExtractedMetadata) -> list[PlanItem]:
    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    "Context:\n"
                    f"{context}\n\n"
                    "Extracted metadata:\n"
                    f"{metadata.model_dump_json()}"
                ),
            },
        ],
        response_format={"type": "json_object"},
        temperature=0,
    )
    content = response.choices[0].message.content or "{}"
    data = json.loads(content)
    raw_plan = data.get("plan", [])
    if not isinstance(raw_plan, list):
        raise ValueError("Expected 'plan' to be a list.")
    return [PlanItem(**item) for item in raw_plan]
