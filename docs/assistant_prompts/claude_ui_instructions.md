
***

# PlanProof — UI Design Directive: "The Motivational Dashboard"

## 1. The Core Philosophy
**Dashboard Trust = Motivational Fuel.**
Knowledge workers are motivated when they believe a plan is **mathematically achievable**. The UI must balance the **warmth** of a personal coach with the **precision** of a flight computer.

---

## 2. Visual Style Guide

### 2.1 Color Palette (Deep Slate & Vibrant Accents)
- **Primary Background:** `#0f172a` (Deep Slate / Navy).
- **Surface/Card Background:** `#1e293b` (Slightly lighter slate).
- **Accents (Motivational):** 
  - Electric Violet (`#8b5cf6`) for "Focus" tasks.
  - Sky Blue (`#0ea5e9`) for "Meetings."
- **Status Indicators (Dashboard):**
  - Success: Emerald (`#10b981`).
  - Failure/Warning: Rose (`#f43f5e`).
- **Text:** 
  - Slate-200 for body text.
  - White for headings.

### 2.2 Typography (The Hybrid Approach)
- **The "Human" Layer (Sans-Serif):** Use **Inter** or **Outfit**. 
  - *Use for:* Task names, "Why" descriptions, and success messages.
  - *Vibe:* Encouraging, modern, readable.
- **The "System" Layer (Monospace):** Use **JetBrains Mono** or **Roboto Mono**.
  - *Use for:* Timestamps (`09:00 AM`), metrics, and validation error logs.
  - *Vibe:* Precise, technical, "The math is verified."

---

## 3. Component Design

### 3.1 The Human Plan (Middle Column)
- **Task Cards:** High-contrast cards with subtle borders.
- **The "Why" Factor:** Every task must prominently display its "Why" string. This provides the purpose needed for motivation.
- **Timeline:** A vertical line on the left of the cards. Use a **glowing pulse** or a bright dot to indicate the "Current Time" relative to the plan.

### 3.2 The Proof Sidebar (Right Column)
- **Status Badge:** A large, high-visibility badge at the top. 
  - `PASS` = "SYSTEM VERIFIED: FEASIBLE"
  - `FAIL` = "LOGISTICAL CONFLICTS DETECTED"
- **The Pre-Flight Checklist:** A list of deterministic checks (Time Overlap, Hallucination, Coverage). Use checkmarks (`[✓]`) and X's (`[!]`) that look like a CI/CD build log.
- **Metric Widgets:** Small "data tiles" for `keyword_recall_score` and `time_overflow`.

---

## 4. Layout Architecture

- **Left 40% (Input):** Minimalism. A large, dark text area for the "Context Dump."
- **Right 60% (Output):**
  - **Left Sub-Column:** The "Human Plan" Timeline.
  - **Right Sub-Column:** The "Validation Proof" Sidebar.

---

## 5. Implementation Instructions for Claude

When starting **PR 1.1**, apply these style rules:
1. **Precision:** No "bubbly" buttons. Use 4px-6px border-radius for a professional "tool" feel.
2. **Transparency:** If the API returns a "FAIL" status, do not hide the plan. Instead, **gray out** the plan cards and highlight the specific validation error in red.
3. **Motion:** Use subtle transitions (0.2s) for status changes. If a plan is "Repairing," show a technical "Scanning..." animation in the sidebar.

---

## 6. The "Success" State
When a plan passes validation, the UI should feel like a **Certificate of Achievement**. The user should look at the screen and think: *"This plan is perfect, the math works, and I know exactly why I'm doing these tasks. Let's go."*