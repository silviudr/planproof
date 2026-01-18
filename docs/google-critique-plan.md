# PlanProof — Project Plan for External Review

## 1. Project Overview

**PlanProof** is a productivity-focused AI assistant that converts messy daily context into realistic, prioritized work plans and systematically evaluates the quality of its own recommendations using observability and evaluation tooling.

Unlike typical productivity AI tools that optimize for engagement or motivational tone, PlanProof treats productivity advice as a **measurable system**. Every recommendation is observable, evaluated, and compared across variants to demonstrate improvement over time.

The project is being developed for a hackathon with an emphasis on:
- Evaluation and observability (Opik)
- Real-world usefulness
- Clear system design under time constraints

---

## 2. Problem Statement

Knowledge workers often receive AI-generated productivity advice that sounds helpful but is difficult to trust. Common issues include:
- Invented or incorrect assumptions (hallucinated meetings, deadlines, priorities)
- Poor adherence to user constraints (time, energy, dependencies)
- Lack of transparency about why tasks are recommended
- No evidence that recommendations improve over time

As a result, users either ignore AI suggestions or over-trust them—both outcomes reduce productivity rather than improve it.

---

## 3. Core User Story

**As a busy knowledge worker, I want to paste unstructured daily context and receive a realistic, prioritized plan that adapts as my day changes — and I want the system to prove, using data, that its recommendations are improving over time.**

---

## 4. Scope and Constraints

### Time Constraints
- Total development window: ~4–5 days
- Mid-hackathon checkpoint requires a live demo and visible progress

### Non-Goals (Explicitly Out of Scope)
- Long-term habit tracking
- Calendar integrations
- User accounts or authentication
- Personalization across days
- Complex frontend polish

The project deliberately focuses on **depth of evaluation**, not breadth of features.

---

## 5. System Architecture (High-Level)

### Public Application
- Single web app hosted on Render.com
- Backend serves both API and static UI
- No authentication required

### Backend Responsibilities
- Accept unstructured daily context
- Run a simple agent pipeline:
  1. Parse context
  2. Generate a plan
  3. Self-audit (assumptions, uncertainty)
- Return a structured plan

### Frontend Responsibilities
- Allow user to paste context
- Display plan, assumptions, questions, and confidence
- Allow lightweight re-planning

---

## 6. Evaluation-First Design

The system is designed around a formal evaluation framework:

### Target
Generate plans that are:
- Actionable
- Constraint-adherent
- Non-hallucinatory
- Aligned with stated user goals

### Test Sets
- Fixed datasets of “messy day” scenarios
- Realistic, ambiguous, constraint-heavy inputs
- Same scenarios reused across all agent variants

### Scoring Methods
- Rule-based checks:
  - Constraint violations
  - Hallucinated entities (meetings, people, deadlines)
  - Structural validity of plan
- LLM-as-judge rubric:
  - Actionability
  - Prioritization quality
  - Alignment with goals
  - Clarity

### Decision Rules
A plan is considered acceptable if:
- No constraint violations
- No hallucinations detected
- Actionability score ≥ defined threshold
- Alignment score ≥ defined threshold

These gates are used to compare agent variants.

---

## 7. Observability and Opik Integration

Opik is used as the system of record for:
- Tracing every agent step (parse → plan → audit)
- Capturing input context and outputs
- Logging evaluation metrics
- Running repeatable experiments across variants
- Visualizing improvement and failure modes via dashboards

Opik dashboards are private (authenticated), but:
- Key metrics are surfaced publicly in the app
- Dashboards are shown directly in the demo video

---

## 8. Development Workflow

### Tools
- VS Code with GitHub Copilot (GPT Codex) and Claude
- Google AI Studio (Gemini) for critique and dataset generation
- OpenAI API for core inference
- Opik Cloud for observability and evaluation
- Render.com for hosting

### Parallel Work Strategy
- Claude works on UI and wiring (`apps/api/static/`)
- Codex works on schemas, validation, and tests (`apps/api/src/`, `apps/api/tests/`)
- Gemini is used externally for:
  - Dataset generation
  - Spec critique
  - Evaluation blind-spot analysis

Strict folder ownership is enforced to avoid conflicts.

---

## 9. Phase-Based Delivery Plan

### Phase 1 (Completed)
- Project scope and evaluation-first design defined
- Repository scaffold created
- Hosting and tooling decisions finalized

### Phase 2 (In Progress)
- Live app with basic plan generation
- Opik tracing visible
- Initial evaluation runs logged
- Two agent variants compared

### Phase 3 (Final)
- Expanded evaluation dataset
- Polished demo
- Clear Opik dashboards
- Video walkthrough and presentation deck

---

## 10. Key Risks and Open Questions

- Are the evaluation metrics sufficient to capture real productivity value?
- Does the LLM-as-judge rubric introduce bias or inconsistency?
- Is “plan quality” a strong enough proxy for productivity improvement?
- Are there important failure modes not covered by the current checks?

---

## 11. Review Request

Please critique this plan as if you were:
- A skeptical ML engineer
- A hackathon judge
- Or a user evaluating whether this system would actually be useful

In particular:
- Identify blind spots or weak assumptions
- Suggest missing metrics or failure cases
- Highlight areas that may be under-specified or over-ambitious
