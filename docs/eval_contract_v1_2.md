
***

# PlanProof — Evaluation Contract (v1.2)

This document is the single source of truth for the PlanProof system logic.

---

## 1. Target
Generate a daily plan that is:
1. **Constraint-adherent:** Hard constraints (e.g., "Must leave at 3 PM") are respected.
2. **Time-feasible:** Tasks do not overlap; total time fits within availability; starts after `current_time`.
3. **Non-hallucinatory:** No invented Proper Nouns (People/Places) or specific Times/Deadlines.
4. **High Coverage:** Addresses the specific tasks/keywords provided in the context.
5. **Humanly Feasible:** Includes breaks; no continuous work blocks > 4 hours.

---

## 2. Inputs

### 2.1 API Request Schema
`POST /api/plan`
```json
{
  "context": "string (unstructured daily notes/tasks)",
  "current_time": "ISO-8601 timestamp",
  "timezone": "IANA timezone string",
  "variant": "v1_naive | v2_structured | v3_agentic_repair"
}
```

---

## 3. Output

### 3.1 API Response Schema
```json
{
  "plan": [
    { 
      "task": "string", 
      "start_time": "ISO-8601", 
      "end_time": "ISO-8601", 
      "timebox_minutes": 0,
      "why": "string"
    }
  ],
  "extracted_metadata": {
    "detected_constraints": ["string"],
    "task_keywords": ["string"]
  },

  "assumptions": ["string"],
  "questions": ["string"],
  "confidence": "low | medium | high",
    
  "validation": {
    "status": "pass | fail",
    "metrics": {
      "constraint_violation_count": 0,
      "overlap_minutes": 0,
      "hallucination_count": 0,
      "keyword_recall_score": 0.0,
      "human_feasibility_flags": 0
    },
    "errors": ["string"]
  },
  "debug": {
    "repair_attempted": false,
    "repair_success": false,
    "variant": "string"
  }
}
```

---

## 4. Evaluation Architecture (The Sandwich)
1. **Extraction (Small Model):** Parse `context` into a JSON list of `required_entities` (People/Projects/Deadlines) and `task_keywords`.
2. **Generation (Primary Model):** Create the `plan` with explicit `start_time` and `end_time`.
3. **Validation (Python/Logic):** Deterministically check the plan against the extracted metadata.

---

## 5. Authoritative Metrics (Deterministic)

| Metric | Definition | Pass Threshold |
| :--- | :--- | :--- |
| **Constraint Violation** | Any task occurring during a "blocked" window or missing a "must-do." | Exactly 0 |
| **Overlap/Overflow** | Sum of minutes where `Task A` and `Task B` time-ranges overlap. | Exactly 0 |
| **Hallucination** | Proper Nouns or Times in Plan NOT found in Extracted Metadata. | Exactly 0 |
| **Keyword Recall** | `% of Extracted Task Keywords` that appear in the final Plan. | ≥ 0.7 (70%) |
| **Human Feasibility** | Any continuous work block > 240 mins without a 15+ min break. | Exactly 0 |

---

## 6. Pass / Fail Rule
A plan is marked **FAIL** and rejected if:
- `constraint_violation_count > 0`
- `overlap_minutes > 0`
- `hallucination_count > 0`
- `keyword_recall_score < 0.7`

---

## 7. Self-Audit & Repair Logic
1. **Initial Run:** Generate `Plan_v1`.
2. **Audit:** Run Deterministic Validators.
3. **If Fail:** Pass the `validation.errors` back to the Generator for one `Repair_Attempt`.
4. **Final Check:** If `Plan_v2` still fails, return `status: "fail"` and do not present the plan as "Recommended."

---

## 8. Opik Logging & Comparison
To prove improvement, we track the following across variants:
- **Hard Pass Rate:** % of requests that result in a "Pass" status.
- **Repair Success Rate:** How often the `Repair_Attempt` converts a "Fail" to a "Pass."
- **Entity Accuracy:** Consistency between `Extracted_Entities` and `Plan_Entities`.
- **Confidence Calibration:** Do "High Confidence" plans actually pass more often than "Low Confidence" plans?

---

## 9. Known Failure Modes (Specific to Hackathon)
- **The Synonym Problem:** Extractor finds "Meeting," Plan says "Sync." (Mitigation: Use broad keyword matching or fuzzy-string-match logic).
- **Timezone Math:** Python's `datetime` math vs. LLM's "hallucinated math." (Mitigation: Force LLM to provide ISO-8601 strings and let Python calculate durations).
- **Ambiguous Context:** User provides no times. (Mitigation: System defaults to `current_time` as the start of the first task).