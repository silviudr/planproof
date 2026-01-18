# PlanProof — Productivity through Measurable Trust

PlanProof is a productivity planning API that treats trust as a measurable outcome, not a vibe.
It produces daily plans and grades them against deterministic rules so users can rely on the result.

## The Core Problem
Most AI productivity advice is untrustworthy because it is generated and judged by the same model.
The output can look confident while violating constraints, inventing details, or overlapping timeblocks.
This makes the plan feel helpful but fail in practice.

## The Solution: The Sandwich Architecture
PlanProof separates the pipeline into three explicit stages:
1) Extraction: Parse the user's context into constraints and keywords.
2) Generation: Produce a plan with explicit start and end times.
3) Deterministic Validation: Enforce constraints, check overlaps, and score recall in Python.

This architecture prevents a model from grading its own output.

## Key Technical Features
- Deterministic time math for overlap detection.
- Hallucination filters to prevent invented entities or times.
- Keyword recall metrics to ensure coverage of user-provided tasks.

## Observability with Opik
Each pipeline step is traced with Opik to measure:
- hard pass rate
- repair success rate
- entity accuracy
- confidence calibration

This makes the system debuggable and comparable across model variants.

## Tech Stack
- FastAPI
- Pydantic v2
- Opik
- OpenAI / Gemini (LLM backends)

## Local Setup
Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate
```

Install dependencies:
```bash
pip install -e .
```

Run the API:
```bash
uvicorn planproof_api.main:app --host 0.0.0.0 --port 10000 --reload
```

The UI (static assets) is served at the root path.
