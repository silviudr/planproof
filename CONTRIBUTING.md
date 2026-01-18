# Contributing to PlanProof

This project is developed under tight time constraints and with multiple AI coding assistants.
To maintain velocity, correctness, and clarity, **strict contribution rules apply**.

These rules are not suggestions.

---

## 1. Source of Truth

The following documents are authoritative:

- `docs/eval_contract_v1_2.md` — evaluation logic, schemas, pass/fail rules
- This file (`CONTRIBUTING.md`) — contribution and workflow rules

If code and contract disagree, the contract wins.
If the contract needs to change, update it **before** modifying code.

---

## 2. Folder Ownership (Strict)

Each assistant or contributor may only modify the directories listed below.

### Claude (UI Lane)

**May edit only:**

```
apps/api/static/**
```

**Must NOT edit:**

- `apps/api/src/**`
- `eval/**`
- `docs/**`

---

### GPT Codex (Backend + Evaluation Lane)

**May edit only:**

```
apps/api/src/**
apps/api/tests/**
eval/**
```

**Must NOT edit:**

- `apps/api/static/**`
- UI files of any kind

---

### Human Maintainer

- May edit any file
- Responsible for merges, conflict resolution, and architectural decisions

---

## 3. Branching Rules

- `main` must always be demo-ready
- All work happens on feature branches
- One branch = one theme

Recommended branch naming:

```
feat/ui-*
feat/schema-*
feat/validators-*
docs/*
```

---

## 4. Pull Request Size Discipline

Small PRs are mandatory.

A good PR:

- touches **one concern**
- contains **1–3 commits**
- can be reviewed in under 5 minutes

If a PR feels large, it is too large.

---

## 5. Checkbox Task Lists (Mandatory)

If a task list is provided (for example in `docs/assistant_prompts/*.md`):

- Each task **must** have a checkbox
- Contributors **must tick `[x]`** when the task is completed
- Unticked boxes indicate incomplete work

PRs with completed-but-unticked tasks may be rejected.

---

## 6. Commit Message Style

Use clear, scoped commit messages:

```
ui: render validation status
api: add PlanResponse schema
eval: implement time overflow validator
docs: finalize eval contract v1.2
```

Avoid vague messages such as:

- “update stuff”
- “fix bug”
- “misc changes”

---

## 7. No Silent Behavior Changes

Any change that affects:

- validation logic
- pass/fail rules
- metrics
- schema fields

**must be reflected in `docs/eval_contract_v1_2.md`.**

Code and contract must remain in sync at all times.

---

## 8. Observability First

All non-trivial logic should be:

- testable
- observable
- explainable

If a decision cannot be explained via logs or validation errors,
it does not belong in the system.

---

## 9. When in Doubt

Prefer:

- simpler logic
- deterministic checks
- explicit failure

Over:

- clever prompts
- implicit behavior
- silent success

PlanProof values correctness over persuasion.

# PlanProof — Project Progress Registry

## UI Lane (Claude)

- [X] PR 1.1: Timeline HTML Scaffold
- [X] PR 1.2: Validation Sidebar
- [X] PR 1.3: Plan Data Mapping
- [X] PR 1.4: Metrics Table Mapping
- [X] PR 2.1: Metadata (Constraints) Section
- [ ] PR 2.2: Keyword Recall Progress Bar
- [ ] PR 2.3: Repair Attempt Display
- [ ] PR 3.1: Loading/Interaction States
- [ ] PR 3.2: Defensive Rendering
- [ ] PR 3.3: Failure/Rejection Styles

## Backend Lane (Codex)

- [X] PR 1.1: Request & Item Models
- [X] PR 1.2: Metrics & Response Models
- [X] PR 1.3: API Route Stub
- [X] PR 2.0.1: Schema Expansion
- [X] PR 2.1: Overlap Validator
- [ ] PR 2.2: Hallucination Validator
- [ ] PR 2.3: Recall Validator
- [ ] PR 2.4: Validator Unit Tests
- [ ] PR 3.1: Metadata Extractor
- [ ] PR 3.2: Validation Wiring
- [ ] PR 3.3: 1-Shot Repair Loop
- [ ] PR 4.1: Opik Trace Scaffolding
- [ ] PR 4.2: Opik Metrics Integration

## Infrastructure

- [X] Infrastructure: Docker
