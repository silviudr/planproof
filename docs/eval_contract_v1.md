
***

# PlanProof — Evaluation Contract (v1)

This document is the single source of truth for the PlanProof system logic. It defines the interface between the extraction, generation, and validation layers.

---

## 1. Target
The system must generate a daily plan that is:
1. **Constraint-adherent:** Hard constraints (e.g., "Must leave at 3 PM") are respected.
2. **Time-feasible:** Total work + breaks ≤ available time; no overlapping tasks.
3. **Non-hallucinatory:** No entities (people, meetings, tools) created out of thin air.
4. **High Coverage:** Addresses the majority of the user's provided context.
5. **Humanly Feasible:** No impossible work marathons (e.g., 6 hours without a break).

---

## 2. Inputs

### 2.1 API Request Schema
`POST /api/plan`
```json
{
  "context": "string (unstructured daily notes/tasks)",
  "current_time": "ISO8601 string (e.g., 2023-10-27T09:00:00Z)",
  "timezone": "string (e.g., 'America/New_York')",
  "variant": "v1_naive | v2_structured | v3_agentic_repair"
}
```

---

## 3. The Pipeline (Logic Flow)
To prevent "Self-Reporting Bias," the system follows these steps:
1. **Extraction (Small Model):** Parse `context` into a list of `detected_constraints` and `user_intents`.
2. **Generation (Large Model):** Create the `plan` using `context` + `detected_constraints`.
3. **Validation (Code + Small Model):** Compare the `plan` against `detected_constraints` using deterministic logic.

---

## 4. Output

### 4.1 API Response Schema
```json
{
  "plan": [
    { "task": "string", "start_time": "ISO8601", "end_time": "ISO8601", "why": "string" }
  ],
  "extracted_metadata": {
    "detected_constraints": ["string"],
    "total_tasks_found": 0
  },
  "validation": {
    "status": "pass | fail",
    "metrics": {
      "constraint_violation_count": 0,
      "time_overflow_minutes": 0,
      "hallucination_count": 0,
      "context_coverage_score": 0.0,
      "human_feasibility_flags": 0
    },
    "errors": ["string"]
  }
}
```

---

## 5. Authoritative Metrics (Deterministic)

| Metric | Definition | Pass Threshold |
| :--- | :--- | :--- |
| **Constraint Violation** | Any task that conflicts with `detected_constraints`. | Exactly 0 |
| **Time Overflow** | `Sum(task_durations)` > `Available_Time_Window`. | Exactly 0 |
| **Hallucination** | Proper nouns/entities in Plan NOT found in Context. | Exactly 0 |
| **Context Coverage** | `Tasks_in_Plan / Total_Tasks_Found`. | ≥ 0.7 |
| **Human Feasibility** | Any continuous work block > 240 mins without break. | Exactly 0 |

---

## 6. Pass / Fail Rule (The "Hard Gate")

A plan is marked **FAIL** if any of the following occur:
- `constraint_violation_count > 0`
- `time_overflow_minutes > 0`
- `hallucination_count > 0`
- `context_coverage_score < 0.7`
- `human_feasibility_flags > 0`

---

## 7. Implementation Roadmap (4-Day Window)

### Step 1: Deterministic Time Validator
Write a Python utility that checks if ISO8601 time blocks in the plan overlap or exceed the day's boundary based on `current_time`.

### Step 2: Negative Entity Matcher (Hallucination)
A simple function that extracts capitalized words/phrases from the `plan` and checks if they exist as substrings in the `context`.

### Step 3: Coverage Calculator
The **Extractor** (Step 3.1) returns a list of tasks. The **Validator** checks how many of those task keywords appear in the final plan.

### Step 4: Opik Integration
Every request logs the `variant` and the `validation.metrics`.
- **Primary Dashboard View:** "Pass Rate per Variant"
- **Secondary Dashboard View:** "Average Coverage Score vs. Variant"

---

## 8. Known Failure Modes (To be monitored in Opik)
1. **The "Empty Day" Hack:** Model ignores all tasks to ensure it doesn't violate time. (Mitigated by `context_coverage_score`).
2. **Timezone Drift:** Model calculates time in UTC but user is in EST. (Mitigated by `timezone` input).
3. **Semantic Hallucination:** Model rewords a task so much that the entity matcher thinks it's a hallucination. (Requires prompt tuning on the Generator).