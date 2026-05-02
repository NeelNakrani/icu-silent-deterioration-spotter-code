# MVP Goals — ICU Silent Deterioration Spotter
## What "submission-worthy" actually means. These are non-negotiable.

> If every item in this file is done, the project is submittable. Everything in ideation_dump.md is a bonus.

---

## The One-Line Goal

A working system that loads real MIMIC-IV patient data, runs three IBM Bob agents in parallel, and outputs a readable single-page risk brief — demonstrated on a patient who actually deteriorated.

---

## Must-Have Features

### 1. MIMIC-IV Data Loader
- [ ] Load at least 10–20 real patient ICU stays from MIMIC-IV (demo dataset or full credentialed access)
- [ ] Parse and normalize the following tables: `chartevents` (vitals), `labevents` (labs), `inputevents`/`outputevents` (I/O), `prescriptions` (meds)
- [ ] Extract a 6-hour rolling window of data per patient (configurable)
- [ ] Handle missing values gracefully — flag them, don't crash
- [ ] Output a clean structured patient data object that agents can consume

**Done when:** You can load a patient ID and get back a clean JSON/dict of their last 6 hours of vitals and labs.

---

### 2. Agent 1 — Trend Agent
- [ ] Calculate rate-of-change (not just current value) for: Heart Rate, Respiratory Rate, Systolic BP, SpO2, Temperature
- [ ] Use at least 4 time points across the 6-hour window (not just first and last)
- [ ] Score each vital's trajectory: stable / slow change / rapid change / reversal
- [ ] Produce a structured output: `{vital: str, current: float, delta_6h: float, velocity: float, trend_label: str, concern_level: int}`
- [ ] Include reasoning text: "Heart rate has risen 18 bpm over 5 hours, accelerating in the last 90 minutes."

**Done when:** Agent 1 can take a patient data object and return a scored trajectory for each tracked vital with plain-English reasoning.

---

### 3. Agent 2 — Lab-Vitals Conflict Agent
- [ ] Implement detection for at least these 3 clinical patterns:
  - **Compensated shock**: Normal BP + rising lactate
  - **Early AKI**: Rising creatinine + falling urine output (even if values are "in range")
  - **Pre-respiratory failure**: Stable SpO2 + rising RR (body compensating)
- [ ] Each pattern match produces: `{pattern_name: str, severity: int, evidence: [data_points], reasoning: str}`
- [ ] Handles case where labs are missing — flags data gap, doesn't fail

**Done when:** Agent 2 can detect compensated shock in a MIMIC patient who had it, and explain why in one sentence.

---

### 4. Agent 3 — Time Bomb Agent
- [ ] Identify pending items in the next 2–3 hours of the incoming shift:
  - Labs ordered but results not yet returned
  - Medications due in the next 2 hours
  - PRN medications not administered in 18+ hours (potential symptom escalation or over-sedation)
- [ ] Produce a priority-sorted list: `[{item: str, due_in_minutes: int, risk_if_missed: str}]`
- [ ] At least one item must reference something that actually changes the care plan if it comes back abnormal

**Done when:** Agent 3 can tell you "Troponin result pending since 4h, due within 90 minutes. If elevated, current care plan needs escalation."

---

### 5. Coordinator / Synthesis Layer
- [ ] Runs Agent 1, Agent 2, and Agent 3 in **parallel** (not sequential) — this is the IBM Bob multi-agent demo
- [ ] Aggregates outputs from all three agents
- [ ] Assigns an overall risk color: 🟢 Green / 🟡 Yellow / 🔴 Red — based on *trajectory*, not just threshold breach
- [ ] Produces a synthesized SBAR+ brief (see below)
- [ ] Preserves the full reasoning chain from all three agents, collapsible

**Done when:** You call `run_all_agents(patient_id)` and get back a complete SBAR+ brief object within a reasonable time.

---

### 6. SBAR+ Output Brief
Each patient brief must contain, in this order:
- [ ] **Risk color badge** (🟢/🟡/🔴) — trajectory-based
- [ ] **One-sentence "what's changing"** — from Trend Agent
- [ ] **One-sentence "what combination is concerning"** — from Lab-Conflict Agent
- [ ] **One-sentence "what needs attention in the next 2 hours"** — from Time Bomb Agent
- [ ] **Collapsed reasoning chain** — all data points cited, expandable on demand
- [ ] Patient identifier, timestamp, data window covered

**Done when:** A non-clinical judge can read one brief in under 60 seconds and understand what's wrong and why.

---

### 7. UI — Minimum Viable Dashboard
- [ ] Single-screen web interface (or CLI with clean output — web preferred for demo)
- [ ] Patient list on the left, ranked by risk score (highest risk at top)
- [ ] Click a patient → see their SBAR+ brief
- [ ] Risk color is visible without clicking (the whole point is prioritization at a glance)
- [ ] Reasoning chain is expandable (collapsed by default)
- [ ] Readable on a laptop screen without scrolling for the brief itself

**Done when:** You can demo the full flow — patient list → click patient → read brief → expand reasoning — in under 2 minutes.

---

### 8. Demo Patient — The Money Shot
- [ ] Identify at least 1 real MIMIC-IV patient who deteriorated (coded, had rapid response, or transferred to higher level of care)
- [ ] Verify the system flags them 🔴 at least 2 hours before the event
- [ ] Document the exact data points that triggered the flags
- [ ] This patient is the centerpiece of the demo video

**Done when:** You can show the system output and then reveal the actual outcome from the MIMIC record. The gap in time is your impact claim.

---

## Minimum Technical Standards

| Requirement | Minimum Bar |
|---|---|
| Data | Real MIMIC-IV patients, not synthetic |
| IBM Bob usage | Agents must run through Bob — not just prompted LLM calls |
| Parallelism | Agents 1/2/3 must run concurrently, not sequentially |
| Reasoning | Every flag must cite the exact data points behind it |
| Reliability | System must not crash on missing data or incomplete records |
| Demo | Live demo or video showing real patient + real output |

---

## What is Explicitly NOT in MVP Scope

Cutting these prevents scope creep and keeps you submittable:

- ~~Bed management or resource allocation~~
- ~~Staffing ratios or scheduling~~
- ~~EHR integration (real hospital systems)~~
- ~~Real-time live patient monitoring (batch analysis only)~~
- ~~Multi-ICU or multi-hospital support~~
- ~~User authentication / access control~~
- ~~Mobile app~~
- ~~Alert fatigue tracking~~
- ~~Outcome feedback loop / model retraining~~
- ~~Free-text nursing note NLP (MIMIC notes are complex — skip for MVP)~~

---

## Definition of "Submission-Ready"

Check every box:

- [ ] All 3 agents produce output on at least 10 real patients
- [ ] Coordinator synthesizes into a complete SBAR+ brief
- [ ] UI shows patient list ranked by risk + clickable briefs
- [ ] Demo patient is identified and their outcome documented
- [ ] Code is in a repo with a README explaining how to run it
- [ ] Demo video recorded (max 3 minutes)
- [ ] Submission write-up drafted (see competition_submission.md)
- [ ] MIT license in the repo

---

## Risk Register

| Risk | Mitigation |
|---|---|
| MIMIC-IV credentialing takes too long | Use MIMIC-IV demo dataset (no credentialing needed, subset of real data) |
| IBM Bob API access unclear | Set up account on bob.ibm.com before hackathon starts; use 30-day free trial |
| Agent 2 patterns are hard to find in data | Pre-identify 5 MIMIC patient IDs known to have these patterns before coding starts |
| UI takes too long | CLI output with clean formatting is acceptable fallback — demo can still be compelling |
| Demo patient flag doesn't line up with outcome | Have 3–5 candidate patients pre-screened so you can pick the most dramatic |
