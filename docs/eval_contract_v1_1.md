# PlanProof — Evaluation Contract (v1.1)

This document is the single source of truth for:
- what PlanProof must output
- how we evaluate it
- which metrics are authoritative vs advisory
- what “pass/fail” means
- how agent variants are compared in Opik

The goal is to treat productivity advice as a **measurable system**, not a persuasive one.

---

## 1. Target

Generate a daily plan that is:
1) **Constraint-adherent** (hard constraints are never violated)
2) **Time-feasible** (time math works)
3) **Non-hallucinatory** (no invented meetings, deadlines, or entities)
4) **Actionable** (tasks are specific and realistically timeboxed)
5) **Aligned** with the user’s stated goals and priorities

Important:
- We do **not** claim the model “learns.”
- We claim the **system design iterates**, and we prove that each release reduces concrete, measurable failure modes.

---

## 2. Inputs

### 2.1 API Request Schema

`POST /api/plan`

```json
{
  "context": "string (unstructured daily notes, tasks, constraints, deadlines, etc.)",
  "current_time": "ISO-8601 timestamp",
  "timezone": "IANA timezone string (e.g. America/Toronto)",
  "variant": "string (optional; e.g. v1_naive | v2_constraints | v3_validator | v4_repair)"
}
```

Notes:
- `context` may range from short notes to multi‑page brain dumps.
- `current_time` and `timezone` are required for correct time math.
- `variant` selects the planning strategy under evaluation.

---

## 3. Output

### 3.1 API Response Schema

```json
{
  "plan": [
    {
      "task": "string",
      "timebox_minutes": 0,
      "why": "string"
    }
  ],
  "assumptions": ["string"],
  "questions": ["string"],
  "confidence": "low | medium | high",

  "validation": {
    "status": "pass | fail",
    "errors": [
      "Planned 240 minutes of work but only 180 minutes available after 3 PM cutoff"
    ],
    "metrics": {
      "constraints_declared": 0,
      "constraints_violated": 0,
      "time_available_minutes": 0,
      "time_planned_minutes": 0,
      "time_overflow_minutes": 0,
      "hallucination_flags": 0,
      "human_feasibility_flags": 0,
      "context_coverage_ratio": 0.0
    }
  },

  "debug": {
    "variant": "string",
    "context_preview": "string"
  }
}
```

### 3.2 Semantics

- `plan` must contain **3–7 items**.
- `timebox_minutes` must be a positive integer (≥ 5).
- `assumptions` and `questions` must be present even if empty.
- `confidence` is the planner’s self‑reported confidence and is **not authoritative**.

Only plans that **PASS validation** are eligible to be presented as “recommended.”
Failed plans must be surfaced as **rejected**, with explanations.

---

## 4. Evaluation Architecture

Evaluation is intentionally separated into distinct roles to avoid self‑preference bias:

1. **Extraction** — Lightweight extractor (rule‑based or constrained LLM)
2. **Generation** — Primary planner model
3. **Validation** — Deterministic enforcement layer
4. **(Optional) Advisory Judgment** — LLM‑as‑judge for subjective qualities

This “sandwich architecture” prevents any single model from grading its own output.

---

## 5. Deterministic Validators (Authoritative)

Deterministic validators produce **hard gates**.
They are repeatable, explainable, and do not rely on LLM judgment.

### 5.1 Hard Constraint Adherence
- Extract explicit constraints (meetings, deadlines, availability windows).
- Track:
  - `constraints_declared`
  - `constraints_violated`

Examples of violations:
- Scheduling work during a blocked window
- Ignoring a stated “must do today”
- Exceeding stated availability

### 5.2 Time Math Feasibility
Compute:
- `time_planned_minutes = sum(plan[i].timebox_minutes)`
- `time_available_minutes` from extracted constraints
- `time_overflow_minutes = max(0, time_planned_minutes - time_available_minutes)`

Hard fail condition:
- If `time_available_minutes > 0` and `time_overflow_minutes > 0` → FAIL

### 5.3 Hallucination Detection
Flag if the plan introduces:
- meetings not present in input
- deadlines not present in input
- people or entities not present in input

Hard fail condition:
- `hallucination_flags > 0` → FAIL

### 5.4 Context Coverage
Measure how well the plan addresses extracted tasks.

```
context_coverage_ratio = tasks_in_plan / tasks_extracted
```

Coverage is computed using **normalized task intents** (extractor labels or semantic tokens),
not raw string matching.

Hard fail condition:
- `context_coverage_ratio < 0.7` → FAIL

### 5.5 Human Feasibility Heuristics
Examples:
- No continuous work block > 180 minutes unless explicitly requested
- Require at least one break if total planned work ≥ 240 minutes

These produce `human_feasibility_flags` and are **advisory** in v1.1.

---

## 6. Pass / Fail Decision Rule

A plan **PASSES** only if all of the following are true:
- `constraints_violated == 0`
- `hallucination_flags == 0`
- If `time_available_minutes > 0` then `time_overflow_minutes == 0`
- `context_coverage_ratio ≥ 0.7`

Otherwise the plan **FAILS** and must include human‑readable `errors`.

---

## 7. Self‑Audit and Self‑Correction

A self‑audit that does not change behavior is insufficient.

System behavior:
1. Generate plan
2. Run deterministic validation
3. If FAIL:
   - attempt **one repair** using validation errors as input
4. Re‑validate
5. Return the best available result, with full trace data

If repair still fails, the system returns a rejected plan with explanations.

---

## 8. Test Sets

### 8.1 Canonical Scenarios
~10 hand‑written “messy day” scenarios.

### 8.2 Synthetic Permutations
~50 variations created by modifying:
- times
- names
- ordering
- urgency wording

All variants are evaluated on identical datasets for fair comparison.

---

## 9. Opik Logging Requirements

Each `/api/plan` call must log:
- input context (or safe preview)
- extracted constraints
- selected variant
- trace spans: extract → plan → validate → (repair) → validate
- validation metrics and status
- advisory judge scores (if used)

---

## 10. Variant Naming and Comparison

Examples:
- `v1_naive`
- `v2_constraints`
- `v3_validator`
- `v4_repair`

Improvement is demonstrated by comparing variants on:
- pass rate
- constraint violations
- time overflow frequency
- hallucination flags
- confidence vs accuracy mismatches

---

## 11. Known Failure Modes

Tracked explicitly:
- Time hallucination
- Context collapse in long inputs
- Overconfidence with incorrect outputs
- Humanly impossible schedules
