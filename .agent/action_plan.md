# Action Plan — ICU Silent Deterioration Spotter

> Two phases: **Pre-competition** (today, April 29) and **During competition** (April 30 – May 3).
> The pre-competition phase is the difference between a winning project and a panicked one.

---

## Phase 1: Pre-Competition (Today — April 29)

The hackathon hasn't started. You cannot write competition code yet, but you can do everything that turns 48 hours of panic into 48 hours of execution. Do these in order.

---

### Block 1 — Accounts & Access (Do First, Takes Time to Activate)
**Time estimate: 30–60 minutes, but set it up now so approvals come through**

- [ ] **Create PhysioNet account** at [physionet.org](https://physionet.org) and complete the CITI training to get MIMIC-IV access. This can take hours. Start immediately. *(Alternatively: the MIMIC-IV demo dataset requires no credentialing — confirm it has the tables you need: chartevents, labevents, inputevents, outputevents, prescriptions)*
- [ ] **Confirm IBM Bob account** at [bob.ibm.com](https://bob.ibm.com). Activate the 30-day free trial if not already done. Understand what the API looks like — can you call Bob agents programmatically? What's the SDK interface?
- [ ] **Register on lablab.ai** if not already done. Find the IBM Bob Hackathon page and hit "participate." Join the lablab.ai Discord.
- [ ] **Register for the April 30 IBM Dev Day event** at [ibmdevday-bob.bemyapp.com](https://ibmdevday-bob.bemyapp.com) — the talks include IBM experts and will give you positioning intel on what judges want to see.

---

### Block 2 — MIMIC-IV Data Reconnaissance
**Time estimate: 2–3 hours**

This is the highest-value pre-work you can do. Understanding the data schema before the clock starts is worth 6 hours during the competition.

- [ ] Download the **MIMIC-IV demo dataset** (no credentialing, free, real data subset). It lives at [physionet.org/content/mimic-iv-demo/](https://physionet.org/content/mimic-iv-demo/)
- [ ] Open a Jupyter notebook (or any environment) and explore these specific tables:
  - `chartevents.csv` — vitals. Find the `itemid` values for: Heart Rate, Respiratory Rate, Systolic BP, SpO2, Temperature. Write these down.
  - `labevents.csv` — labs. Find `itemid` for: Lactate, Creatinine, BUN, WBC, Hemoglobin.
  - `inputevents.csv` + `outputevents.csv` — fluid I/O. Understand how urine output is recorded.
  - `prescriptions.csv` — medication orders. Understand the time fields.
  - `admissions.csv` + `patients.csv` — for patient demographics and admission context.
- [ ] **Identify 5 patient `subject_id` + `hadm_id` + `stay_id` combinations** that you can tell have deterioration events (look for patients with multiple ICU stays, or those with short ICU stays followed by death/readmission — the demo dataset has real outcomes).
- [ ] Write a simple data loader function (just exploration, not "competition code") that: takes a `stay_id`, queries the last 6 hours of chartevents, returns a DataFrame. This is reconnaissance — you're mapping the terrain.

**Key itemids to find (approximate, verify against MIMIC-IV `d_items` table):**
| Vital | Common MIMIC itemid |
|---|---|
| Heart Rate | 220045 |
| Respiratory Rate | 220210 |
| SpO2 | 220277 |
| Systolic BP | 220179 |
| Temperature | 223761 (F) / 223762 (C) |
| Urine Output (Foley) | 226559 |

---

### Block 3 — IBM Bob Architecture Research
**Time estimate: 1–2 hours**

- [ ] Read the IBM Bob documentation. Answer these specific questions for yourself:
  - How do you define and run a Bob agent programmatically?
  - How do you run multiple agents in parallel?
  - What does BobShell output look like? Can you capture it programmatically?
  - Is there a Python SDK? What does a basic agent call look like?
- [ ] Find at least one example of Bob being used for multi-agent orchestration (the press release and IBM Developer blog are good starting points)
- [ ] Sketch out (on paper/notes, not code) the exact function signatures for your 3 agents:
  - `trend_agent(patient_data: dict) -> TrendReport`
  - `lab_conflict_agent(patient_data: dict) -> ConflictReport`
  - `time_bomb_agent(patient_data: dict) -> TimeBombReport`
  - `coordinator(trend: TrendReport, conflict: ConflictReport, timebomb: TimeBombReport) -> SBARBrief`

---

### Block 4 — Tech Stack Decision
**Time estimate: 30 minutes**

Make these decisions now so you don't debate them at 2 AM on Day 1:

- [ ] **Language**: Python (recommended — MIMIC data is CSV, pandas is the fastest path, Bob almost certainly has a Python SDK)
- [ ] **UI framework**: Streamlit (fastest path to a web UI in Python with zero frontend overhead) OR plain React if you're comfortable (better-looking demo). Decide now.
- [ ] **Data storage**: SQLite or just pandas DataFrames in memory (no Postgres setup overhead)
- [ ] **Repo setup**: Create the GitHub repo now with the folder structure below. MIT license. README stub.

```
ICU-Silent-Deterioration-Spotter/
├── data/                    # MIMIC-IV data files go here (gitignored)
├── agents/
│   ├── trend_agent.py
│   ├── lab_conflict_agent.py
│   ├── time_bomb_agent.py
│   └── coordinator.py
├── data_loader/
│   └── mimic_loader.py
├── ui/
│   └── app.py               # Streamlit or React
├── outputs/                 # Generated SBAR briefs
├── demo/                    # Demo patient data + screenshots
├── requirements.txt
├── README.md
└── LICENSE                  # MIT
```

- [ ] Set up a Python virtual environment and install: `pandas`, `numpy`, `streamlit` (or your UI choice), and the IBM Bob SDK (whatever that package name turns out to be)

---

### Block 5 — Clinical Context Fast-Read
**Time estimate: 45 minutes — this makes your reasoning chains sound credible**

You don't need to become a nurse. You need to understand 3 clinical patterns well enough to write detection logic for them. Read these:

- [ ] **NEWS2 scoring system** — National Early Warning Score. It's a standard 6-variable score (RR, SpO2, BP, HR, Temp, consciousness). Know what the thresholds are. Your system should reference these. ([Google "NEWS2 scoring chart"](https://www.google.com/search?q=NEWS2+scoring+chart))
- [ ] **SOFA score** — Sequential Organ Failure Assessment. Used in ICU. Know what organ systems it covers. ([Wikipedia article is fine](https://en.wikipedia.org/wiki/SOFA_score))
- [ ] **Compensated shock** — What does it look like in vitals before BP drops? (Answer: rising HR, rising lactate, falling urine output, normal BP — the triad that kills)
- [ ] **Early AKI** — Creatinine rising + urine output falling before either reaches "abnormal" threshold. That's the window.
- [ ] **Pre-respiratory failure** — Rising RR with stable SpO2 means the patient is working harder to maintain oxygenation. The SpO2 crash comes later.

---

### Block 6 — Demo Patient Pre-Screening
**Time estimate: 1 hour (do after Block 2)**

- [ ] From your 5 candidate patients in Block 2, pick the **3 most dramatic** deterioration cases
- [ ] For each, note: what happened (rapid response? coding? transfer?), at what timestamp, and what the vitals looked like in the 6 hours before
- [ ] Pick the ONE patient who will be your demo centerpiece — the one where the 6-hour trend is most visually obvious and the outcome is most dramatic
- [ ] Write down this patient's `subject_id`, `hadm_id`, `stay_id`, and the timestamp of their adverse event. This is sacred. Don't lose it.

---

### Block 7 — Submission Write-Up Draft
**Time estimate: 30 minutes**

- [ ] Open `competition_submission.md` and draft the 5 submission sections (Problem Statement, Solution, How IBM Bob is Used, Data, Impact) in rough form
- [ ] You'll polish this during the competition, but having the skeleton means you won't be writing from scratch at midnight on May 2

---

## Phase 2: During Competition (April 30 – May 3)

The hackathon runs ~72 hours. You only need 48 of them to execute. The extra time is buffer for sleep, debugging, and polish.

---

### Day 1 (April 30) — Foundation

**Morning: IBM Dev Day talks (11AM ET)**
- [ ] Attend the IBM Dev Day event — 11AM ET kickoff
- [ ] Take notes on: what features of Bob do the IBM team emphasize? What demos do they show? What do they seem proudest of?
- [ ] Listen for clues about judging preferences — what the team built is what they'll reward

**Afternoon: Data + Loader (3–8 hours)**
- [ ] Clone your pre-set-up repo and add MIMIC-IV data to `/data/` (gitignored)
- [ ] Build `mimic_loader.py` — the data loading and normalization function
  - Input: `stay_id`, `hours_back` (default 6)
  - Output: clean dict with vitals time series, labs time series, meds list, I/O totals
- [ ] Test on your pre-screened demo patient — make sure data loads correctly
- [ ] Handle edge cases: missing vitals, sparse labs, no urine output recorded

**Evening: Agent 1 (3–4 hours)**
- [ ] Build `trend_agent.py` through IBM Bob
- [ ] Test on 5 patients — verify the rate-of-change scoring feels clinically sensible
- [ ] The output should be human-readable without any formatting (plain dicts/text)

---

### Day 2 (May 1) — Core Agents + Synthesis

**Morning: Agents 2 and 3 (4–5 hours)**
- [ ] Build `lab_conflict_agent.py` — compensated shock, early AKI, pre-respiratory failure patterns
- [ ] Build `time_bomb_agent.py` — pending labs, meds due, PRN gaps
- [ ] Test both on the demo patient and 4 others

**Afternoon: Coordinator + SBAR+ Output (3–4 hours)**
- [ ] Build `coordinator.py` — parallel agent invocation, output synthesis
- [ ] Implement risk color scoring logic (trajectory-based, not threshold-based)
- [ ] Generate SBAR+ brief as a structured Python object and as formatted text
- [ ] Verify the demo patient gets flagged 🔴 with the right reasoning

**Evening: UI (3–4 hours)**
- [ ] Build `ui/app.py` — Streamlit dashboard
  - Patient list ranked by risk color
  - Click to expand SBAR+ brief
  - Reasoning chain collapsible
- [ ] Get the full end-to-end flow working: load data → run agents → display brief

---

### Day 3 (May 2) — Polish + Demo

**Morning: Testing + Tuning (3–4 hours)**
- [ ] Run all 10–20 patients through the full pipeline
- [ ] Review outputs — are the flags clinically sensible? Fix obvious errors
- [ ] Tune coordinator weighting if risk scores feel off
- [ ] Fix any crashes or data edge cases

**Afternoon: Demo Prep (2–3 hours)**
- [ ] Finalize the demo patient case — document their outcome from MIMIC record
- [ ] Rehearse the demo flow: problem setup → patient list → click demo patient → SBAR+ brief → reveal outcome
- [ ] Polish the UI — colors, layout, the collapsible reasoning chain

**Evening: Video + Write-Up (3 hours)**
- [ ] Record the demo video (OBS, Loom, or QuickTime — whatever works)
  - Script: problem (30s) → show system loading patients (30s) → click demo patient (30s) → read the brief aloud (30s) → reveal the real outcome (30s) = ~2.5 minutes
- [ ] Finalize the submission write-up (5 sections from competition_submission.md)
- [ ] Push final code to GitHub, verify README has run instructions

---

### Day 4 (May 3) — Submit

**Morning: Submission**
- [ ] Final read-through of submission form
- [ ] Verify demo video plays correctly
- [ ] Verify GitHub repo is public with MIT license
- [ ] Submit on lablab.ai **before the deadline** — don't cut it close
- [ ] Share on lablab.ai Discord (community visibility = extra judge attention sometimes)

---

## Time Budget (48 Active Hours)

| Phase | Hours |
|---|---|
| Data loader + MIMIC setup | 4–5h |
| Agent 1 (Trend) | 3–4h |
| Agent 2 (Lab-Conflict) | 3–4h |
| Agent 3 (Time Bomb) | 2–3h |
| Coordinator + synthesis | 3–4h |
| UI | 3–4h |
| Testing + tuning | 4–5h |
| Demo video | 1–2h |
| Submission write-up + README | 1–2h |
| Buffer / sleep / debugging | 10–12h |
| **Total** | **~48h** |

---

## Mental Model for the Competition

**Build order = dependency order.** Data loader first, agents second, coordinator third, UI last. If you run out of time, a CLI output with good formatting is a valid UI — the agents and the demo patient are what win, not the frontend.

**Test on the demo patient constantly.** Every agent should be validated against your pre-screened patient with the known outcome. Don't build in the abstract.

**IBM Bob is the story, not just the tool.** Every time you make a decision during build, ask: "Does this showcase what Bob can do?" Parallel agents, audit trails, explainability — these are Bob features, not just good engineering. Name them explicitly in your submission.

**The demo video is the submission.** Judges will watch the video before they read the writeup. The 90-second reveal — "here's what the system said at 6 AM, here's what happened at 8:30 AM" — is the entire argument for why this project should win.
