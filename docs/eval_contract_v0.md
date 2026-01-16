# PlanProof — Evaluation Contract (v0)

This document is the single source of truth for:
- what PlanProof must output
- how we evaluate it
- which metrics are authoritative vs advisory
- what “pass/fail” means
- how agent variants are compared in Opik

The goal is to treat productivity advice as a **measurable system**.

---

## 1. Target

Generate a daily plan that is:
1) **Constraint-adherent** (hard constraints are never violated)
2) **Time-feasible** (time math works)
3) **Non-hallucinatory** (no invented meetings/deadlines/people)
4) **Actionable** (tasks are specific and timeboxed)
5) **Aligned** with the user’s stated goals and priorities

Important: We do **not** claim the model “learns.”  
We claim the **system design iterates**, and we prove each release reduces concrete failure modes.

---

## 2. Inputs

### 2.1 API Request Schema (v0)

`POST /api/plan`

```json
{
  "context": "string (unstructured daily notes, tasks, constraints, deadlines, etc.)",
  "variant": "string (optional; e.g. v1_naive | v2_constraints | v3_validator | v4_repair)"
}
```

---

## 3. Output

### 3.1 API Response Schema (v0)

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
    "hard_fail_reasons": ["string"],
    "metrics": {
      "constraints_declared": 0,
      "constraints_violated": 0,
      "time_available_minutes": 0,
      "time_planned_minutes": 0,
      "time_overflow_minutes": 0,
      "hallucination_flags": 0,
      "human_feasibility_flags": 0
    }
  },

  "debug": {
    "variant": "string",
    "context_preview": "string"
  }
}
```

---

## 4. Evaluation Components

### 4.1 Deterministic Validators (Authoritative)

Deterministic validators produce **hard gates**.

- Constraint adherence
- Time math feasibility
- Hallucination detection
- Basic human feasibility heuristics

### 4.2 LLM-as-Judge (Advisory)

Used only for subjective qualities:
- actionability
- clarity
- prioritization
- alignment

LLM judges **never override** deterministic failures.

---

## 5. Pass / Fail Rule

A plan **passes** only if:
- `constraints_violated == 0`
- `hallucination_flags == 0`
- if `time_available_minutes > 0` then `time_overflow_minutes == 0`

Otherwise: **FAIL**.

---

## 6. Self-Audit & Repair

1. Generate plan
2. Validate deterministically
3. If FAIL, attempt **one repair**
4. Re-validate
5. Return result with full trace

---

## 7. Test Sets

- ~10 canonical scenarios (hand-written)
- ~50 permutations (synthetic variations)

---

## 8. Opik Logging

Log:
- inputs
- variant
- trace spans
- validation metrics
- judge scores (if used)

---

## 9. Variants

- v1_naive
- v2_constraints
- v3_validator
- v4_repair

---

## 10. Known Failure Modes

- Time hallucination
- Context collapse
- Overconfidence vs correctness
- Human infeasibility
