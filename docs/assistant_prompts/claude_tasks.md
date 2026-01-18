# Claude Tasks — PlanProof (UI Lane)

You are Claude working as a coding assistant in VS Code.

## Rules (must follow)

- **Only edit files under:** `apps/api/static/`
- **Do not edit backend code** (`apps/api/src/**`) or eval code (`eval/**`)
- **Do not rename JSON fields** returned by the API
- Keep work in **small PRs**. Each PR should be 1 theme and ideally 1–3 commits.
- After completing an item, **tick the checkbox** by changing `[ ]` to `[x]`.
- **Micro-PR Mandate:** Each checkbox `[ ]` is exactly ONE Pull Request.
- **Folder Ownership:** Only edit files under `apps/api/static/`.
- **Post-Merge:** Once a PR is merged, update the corresponding checkbox in `CONTRIBUTING.md`.
- **Contract Reference:** Follow `docs/eval_contract_v1_2.md`. Use `start_time` and `end_time`.

## Contract Reference

- Output format and meanings are defined in: `docs/eval_contract_v1_2.md`
- The UI must render these fields (do not invent new ones):
  - `plan[]` with `task`, `start_time`, `end_time`, `why`
  - `assumptions[]`, `questions[]`, `confidence`
  - `validation.status`, `validation.errors[]`, `validation.metrics.*`
  - `debug.variant` (if present)

---

## Phase 1 — UI: Timeline & Validation Scaffolding

- [X] **PR 1.1:** Update `index.html` with a chronological timeline container for `plan[]`.
- [X] **PR 1.2:** Implement the Validation Status badge (PASS/FAIL) and Errors list sidebar.
- [X] **PR 1.3:** Map `plan[]` items to render `task`, `start_time`, `end_time`, and `why`.
- [X] **PR 1.4:** Render a `validation.metrics` table (Constraint violations, Overlaps, Hallucinations).

## Phase 2 — UI: Metadata & Repair Visibility

- [X] **PR 2.1:** Add a "Context Extracted" section to render `extracted_metadata.detected_constraints`.
- [ ] **PR 2.2:** Add a visual progress bar or score for `keyword_recall_score` (Target >= 0.7).
- [ ] **PR 2.3:** Add a "Repair Attempt" log that displays if `debug.repair_attempted` is true.

## Phase 3 — UI: Polish & Resilience

- [ ] **PR 3.1:** Implement loading states (spinner + disable "Generate" button during flight).
- [ ] **PR 3.2:** Implement defensive rendering (prevent crashes if `metrics` or `plan` fields are missing).
- [ ] **PR 3.3:** Apply "Rejected" styling (gray/muted) to plans where `validation.status == "fail"`.

---

**Acceptance Test:** The UI must render a full timeline with valid ISO-8601 times and show a clear "FAIL" state if the API returns validation errors.
