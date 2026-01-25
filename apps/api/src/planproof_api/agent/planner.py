from __future__ import annotations

import json

from openai import OpenAI

from planproof_api.agent.schemas import ExtractedMetadata, PlanItem
from planproof_api.observability.opik import opik

_SYSTEM_PROMPT = (
    "You are a planning assistant. Return ONLY valid JSON with keys: "
    "plan, assumptions, questions. "
    "Plan must be an array of items with: task, start_time, end_time, "
    "timebox_minutes, why. Use ISO-8601 timestamps. "
    "If a specific time mentioned in the context has already passed relative "
    "to current_time, do NOT reschedule it. Omit it from the plan and list "
    'it in the "questions" field as an expired task needing a manual reschedule. '
    "All questions must be natural language sentences, not JSON strings. "
    "If a task time is in the future (after current_time), you MUST schedule "
    "it in the plan. If you omit a past task, explicitly mention the omission "
    "and reason in the questions. "
    "You MUST output at least 2 assumptions. "
    "If the user did not specify a duration, ask about it in questions. "
    "Current time is provided in 12h format. Be extremely careful with AM/PM: "
    "3:15 PM is 15:15. If the current time is 6 AM, a 3 PM meeting is in the "
    "future and must be scheduled. "
    "Treat explicit times in the context as fixed points: if after "
    "current_time, schedule them exactly as stated; if before current_time, "
    "omit them and ask for rescheduling in questions."
)


class PlanGenerationError(RuntimeError):
    pass


@opik.track(name="generate_plan")
def generate_plan(
    context: str,
    metadata: ExtractedMetadata,
    current_time: str,
    timezone: str,
    repair_prompt: str | None = None,
) -> tuple[list[PlanItem], list[str], list[str]]:
    """Generate a plan from context and extracted metadata using the LLM.

    This implements the "Generation" step of the Sandwich Architecture.

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
        user_content = (
            "Context:\n"
            f"{context}\n\n"
            "Extracted metadata:\n"
            f"{metadata.model_dump_json()}\n\n"
            f"The user is in {timezone}. "
            f"Current local time is {current_time}. "
            "All constraints like '1 PM' refer to this local time. "
            "Do not confuse UTC with Local. "
            "Do not schedule any tasks before this time. "
            "Explicit times in the context are fixed points."
        )
        if repair_prompt:
            user_content = f"{user_content}\n\nRepair instructions:\n{repair_prompt}"

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": user_content,
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
