# Codex Tasks — PlanProof (Backend + Deterministic Evaluation Lane)

You are GPT Codex working as a coding assistant in VS Code.

## Rules (Strict)

- **Only edit files under:**
  - `apps/api/src/**`
  - `apps/api/tests/**`
  - `eval/**`
- **Do not edit UI files** (`apps/api/static/**`)
- Keep work in **small PRs**. Each PR should be 1 theme and ideally 1–3 commits.
- After completing an item, **tick the checkbox** by changing `[ ]` to `[x]`.
- Follow the contract exactly: `docs/eval_contract_v1_2.md`
- **Micro-PR Mandate:** Each checkbox `[ ]` is exactly ONE Pull Request.
- **Folder Ownership:** Only edit `apps/api/src/**`, `apps/api/tests/**`, and `eval/**`.
- **Post-Merge:** Once a PR is merged, update the corresponding checkbox in `CONTRIBUTING.md`.
- **Contract Reference:** Follow `docs/eval_contract_v1_2.md` exactly.

## Contract Reference

The implementation must conform to:

- Request fields: `context`, `current_time`, `timezone`, `variant`
- Response fields: `plan[]` with `task`, `start_time`, `end_time`, `why`, etc.
- Validation gates:
  - constraint violations
  - time overlap minutes
  - time overflow minutes
  - hallucination flags
  - keyword recall score threshold (>= 0.7)

---

## Phase 1 — API: Schemas & Stubs

- [X] **PR 1.1:** Implement Pydantic models for `PlanRequest` and `PlanItem` (with ISO-8601 validation).
- [X] **PR 1.2:** Implement `ValidationMetrics` and `PlanResponse` models.
- [X] **PR 1.3:** Update `routes.py` to return a static JSON stub matching the full `PlanResponse` schema.

## Phase 2 — Eval: Deterministic Validators

- [X] **PR 2.1:** Implement `eval/time_math.py` to detect overlaps between `start_time` and `end_time`.
- [X] **PR 2.2:** Implement `eval/hallucination.py` for Proper Noun matching between context and plan.
- [ ] **PR 2.3:** Implement `eval/recall.py` for Keyword Recall score calculation (deterministic string match).
- [X] **PR 2.4:** Add unit tests for all validators in `apps/api/tests/`.

## Phase 3 — Agent: The Sandwich Pipeline

- [ ] **PR 3.1:** Implement the "Extractor" logic (LLM call to parse constraints and keywords).
- [ ] **PR 3.2:** Wire the Validator to run after the Planner and populate `validation.status` and `errors`.
- [ ] **PR 3.3:** Implement the 1-shot "Repair Attempt" logic (if FAIL, retry once with errors in prompt).

## Phase 4 — Observability

- [ ] **PR 4.1:** Integrate Opik tracing hooks for each step (Extract -> Plan -> Validate -> Repair).
- [ ] **PR 4.2:** Ensure `validation.metrics` are logged as properties in the Opik trace.

---

**Acceptance Test:** `pytest` must pass for all validators. The API must fail plans with overlapping times or low keyword recall (< 0.7).
