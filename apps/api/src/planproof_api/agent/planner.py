from __future__ import annotations

import json

from openai import OpenAI

from planproof_api.agent.schemas import ExtractedMetadata, PlanItem
from planproof_api.observability.opik import opik

_SYSTEM_PROMPT = (
    "You are a planning assistant. Return ONLY valid JSON with keys: "
    "plan, assumptions, questions. "
    "Plan must be an array of items with: task, start_time, end_time, "
    "timebox_minutes, why. Use ISO-8601 timestamps."
)


class PlanGenerationError(RuntimeError):
    pass


@opik.track(name="generate_plan")
def generate_plan(
    context: str,
    metadata: ExtractedMetadata,
    current_time: str,
    timezone: str,
) -> tuple[list[PlanItem], list[str], list[str]]:
    """Generate a plan from context and extracted metadata using the LLM.

    Args:
        context: Raw user context string.
        metadata: Extracted constraints, entities, and task keywords.
        current_time: ISO-8601 timestamp representing "now".
        timezone: IANA timezone string for the user.

    Returns:
        Tuple of (plan_items, assumptions, questions).
    """
    try:
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
                        f"{metadata.model_dump_json()}\n\n"
                        f"The current time is {current_time} in {timezone}. "
                        "Do not schedule any tasks before this time."
                    ),
                },
            ],
            response_format={"type": "json_object"},
            temperature=0,
        )
        content = response.choices[0].message.content or "{}"
        data = json.loads(content)
        raw_plan = data.get("plan")
        raw_assumptions = data.get("assumptions")
        raw_questions = data.get("questions")

        if not isinstance(raw_plan, list):
            raise ValueError("Expected 'plan' to be a list.")
        if not isinstance(raw_assumptions, list):
            raise ValueError("Expected 'assumptions' to be a list.")
        if not isinstance(raw_questions, list):
            raise ValueError("Expected 'questions' to be a list.")

        plan = [PlanItem(**item) for item in raw_plan]
        assumptions = [str(item) for item in raw_assumptions]
        questions = [str(item) for item in raw_questions]
        return plan, assumptions, questions
    except (json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
        raise PlanGenerationError(
            "Plan generation failed due to invalid JSON output."
        ) from exc
    except Exception as exc:
        raise PlanGenerationError("Plan generation failed due to API error.") from exc
