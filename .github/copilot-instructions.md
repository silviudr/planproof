# GitHub Copilot Instructions — PlanProof

These instructions apply to **all AI coding assistants** (GitHub Copilot, GPT Codex, Claude)
working inside this repository.

They are **mandatory**.

---

## 1. Authoritative Documents

You must follow these documents exactly:

1. `docs/eval_contract_v1_2.md` — evaluation logic, schemas, pass/fail rules
2. `CONTRIBUTING.md` — folder ownership, branching, PR discipline

If code conflicts with these documents, **the documents win**.

Do not invent new behavior that is not allowed by the evaluation contract.

---

## 2. Folder Ownership (Strict Enforcement)

### UI Lane (Claude)
You may edit **only**:
```
apps/api/static/**
```

You must NOT edit:
- `apps/api/src/**`
- `apps/api/tests/**`
- `eval/**`
- `docs/**`

---

### Backend + Evaluation Lane (GPT Codex)
You may edit **only**:
```
apps/api/src/**
apps/api/tests/**
eval/**
```

You must NOT edit:
- `apps/api/static/**`
- UI or frontend files

---

If you are unsure whether a file is allowed, **do not edit it**.

---

## 3. Pull Request Discipline

- Keep changes small and focused
- One PR = one theme
- Prefer 1–3 commits per PR
- Avoid refactors unless explicitly requested

Large PRs will be rejected.

---

## 4. Checkbox Task Lists (Mandatory)

When a task list is provided (for example in `docs/assistant_prompts/*.md`):

- Each task will include a checkbox `[ ]`
- You **must** tick `[x]` when the task is completed
- Do not tick boxes for unfinished work

Incomplete or unticked tasks indicate incomplete PRs.

---

## 5. Schema and Contract Safety

You must NOT:
- rename JSON fields
- remove required fields
- change validation thresholds
- soften pass/fail gates

Unless explicitly instructed to update `docs/eval_contract_v1_2.md`.

---

## 6. Deterministic Logic Preference

Prefer:
- deterministic checks
- explicit conditionals
- human-readable error messages

Avoid:
- clever prompts
- hidden heuristics
- silent fallbacks

If behavior cannot be explained in validation output, it should not exist.

---

## 7. Observability First

All non-trivial logic should:
- emit metrics
- produce traceable outcomes
- surface failures clearly

Silent success is considered a bug.

---

## 8. When Instructions Conflict

If user instructions conflict with:
- `docs/eval_contract_v1_2.md`
- `CONTRIBUTING.md`
- this file

You must **stop and ask for clarification** instead of guessing.

---

PlanProof prioritizes correctness, transparency, and explainability over cleverness.


---


These instructions are mandatory for all AI coding assistants (Copilot, Codex, Claude).

---

## 1. Project Principle: "The Sandwich Architecture"
You must strictly separate extraction, generation, and validation.
- **Extraction:** Identify constraints/keywords first.
- **Generation:** Create the plan based on extraction.
- **Validation:** Use **deterministic Python code** to verify the plan. 
- **The Rule:** An LLM must never grade its own plan. Python is the final judge.

## 2. The Micro-PR Mandate
- **One Checkbox = One PR.** 
- Do not combine tasks. 
- You are forbidden from submitting PRs larger than ~70 lines of logic.
- This is required for project visibility and incremental debugging.
- You must follow the PR discipline defined in `CONTRIBUTING.md` (one concern per PR, 1–3 commits, reviewable in under 5 minutes).
- These small PRs are required for project visibility and incremental debugging.

## 3. Folder Ownership (Strict)
- **UI Lane (Claude):** `apps/api/static/**` ONLY.
- **Backend Lane (Codex):** `apps/api/src/**`, `apps/api/tests/**`, `eval/**` ONLY.
- Crossing folders will result in PR rejection.

## 4. Post-Merge Accountability
Whenever the user informs you that a PR has been merged:
1. Open `CONTRIBUTING.md`.
2. Locate the corresponding task.
3. Change `[ ]` to `[x]`.
4. Check off the internal task file (`claude_tasks.md` or `codex_tasks.md`).

## 5. Technical Constraints
- **Time:** Use ISO-8601 strings for all `start_time` and `end_time` fields.
- **Math:** Use Python `datetime` for duration and overlap calculations.
- **Recall:** Keyword recall must be calculated via deterministic string/token matching.
- **Status:** `validation.status` is binary: "pass" or "fail".

## 6. Communication
If a task is ambiguous or conflicts with `docs/eval_contract_v1_2.md`, you must stop and ask for clarification. Do not guess.