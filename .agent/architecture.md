# ICU Silent Deterioration Spotter — Technical Architecture

> Refined from high-level draft. All design decisions are scoped to the hackathon MVP window (April 30 – May 3, 2026).

---

## System Overview

The system is divided into two top-level components: a **Backend Data Processing Pipeline** and a **Frontend Dashboard UI**. These map to four logical layers (0–3).

```
┌─────────────────────────────────────────────────────────────────┐
│                     BACKEND (Python)                            │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Layer 0 — Raw Data & Ingestion                          │   │
│  │  MIMIC-IV CSV/Parquet → DataLoader → PatientDataObject   │   │
│  └─────────────────────────┬────────────────────────────────┘   │
│                            │  PatientDataObject (dict/dataclass) │
│  ┌─────────────────────────▼────────────────────────────────┐   │
│  │  Layer 1 — Parallel Agents (concurrent via asyncio)      │   │
│  │                                                          │   │
│  │   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │   │
│  │   │ Trend Agent  │  │  Lab-Vitals  │  │  Time Bomb   │  │   │
│  │   │              │  │Conflict Agent│  │    Agent     │  │   │
│  │   └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  │   │
│  │          │                 │                  │          │   │
│  └──────────┼─────────────────┼──────────────────┼──────────┘   │
│             │   TrendReport   │  ConflictReport  │TimeBombReport │
│  ┌──────────▼─────────────────▼──────────────────▼──────────┐   │
│  │  Layer 2 — Coordinator / Synthesis (LLM call → SBAR+)    │   │
│  │  Aggregates 3 reports → risk color → SBARBrief object    │   │
│  └──────────────────────────────┬───────────────────────────┘   │
└─────────────────────────────────┼───────────────────────────────┘
                                  │  SBARBrief (JSON via REST API)
┌─────────────────────────────────▼───────────────────────────────┐
│                     FRONTEND (React / Streamlit)                │
│                                                                 │
│  Layer 3 — Dashboard UI                                         │
│  Patient list (ranked by risk) → Click → SBAR+ Brief view      │
└─────────────────────────────────────────────────────────────────┘
```

---

## Tech Stack

| Component | Technology | Rationale |
|---|---|---|
| Language | Python 3.11+ | MIMIC-IV ecosystem, pandas/polars, asyncio native |
| Data processing | pandas + polars | pandas for prototyping, polars for speed on large MIMIC tables |
| Concurrency | `asyncio` + `asyncio.gather()` | Native parallel agent execution without thread overhead |
| LLM — Reasoning layer | Anthropic Claude API (`claude-sonnet-4-6`) | 200K context, best narrative generation for SBAR+ |
| LLM — Structured scoring | IBM watsonx.ai (Granite) | Native hackathon stack, strong on tabular/structured inference |
| Backend API | FastAPI | Async-native, auto-generates OpenAPI docs, lightweight |
| Frontend | Streamlit (MVP) → React (stretch) | Streamlit ships faster for hackathon; React for polish if time allows |
| IBM Bob integration | Bob IDE + BobShell | Agents authored and orchestrated through Bob; BobShell for auditability |
| Data source | MIMIC-IV (demo dataset via PhysioNet) | No credentialing needed for demo subset |

---

## Layer 0 — Raw Data & Ingestion

### Responsibility
Load MIMIC-IV raw tables, extract a configurable rolling window per patient, output a clean structured `PatientDataObject`.

### MIMIC-IV Tables Used

| Table | Data extracted |
|---|---|
| `chartevents` | Vitals: HR, RR, SBP, DBP, SpO2, Temperature |
| `labevents` | Labs: Lactate, Creatinine, WBC, Hemoglobin, Troponin |
| `outputevents` | Urine output per hour |
| `inputevents` | IV fluid administration |
| `prescriptions` | Medications scheduled + administered flag |
| `admissions` | Admit time, ICU stay ID, patient metadata |

### Data Window
- Default: **6-hour rolling window** (configurable via `WINDOW_HOURS` env var)
- Resampled to: **30-minute intervals** (for consistent time-series inputs to agents)
- Missing values: flagged as `None` with `data_quality.missing_fields: [...]` — agents must handle gracefully

### PatientDataObject Schema

```python
@dataclass
class PatientDataObject:
    patient_id: str
    stay_id: str
    window_start: datetime
    window_end: datetime
    vitals: list[VitalReading]        # time-series, 30-min intervals
    labs: list[LabReading]            # sparse — only when drawn
    urine_output: list[OutputReading] # per hour
    medications: list[MedRecord]      # scheduled + PRN + administered flag
    pending_labs: list[PendingLab]    # ordered but result not yet returned
    data_quality: DataQuality         # missing fields, gaps flagged
```

---

## Layer 1 — Parallel Agent Layer

### Concurrency Model

All three agents receive the same `PatientDataObject` and run **concurrently** via `asyncio.gather()`:

```python
async def run_all_agents(patient_data: PatientDataObject) -> tuple:
    trend, conflict, timebomb = await asyncio.gather(
        trend_agent(patient_data),
        lab_conflict_agent(patient_data),
        time_bomb_agent(patient_data),
    )
    return trend, conflict, timebomb
```

Each agent is independently async and does not share state. Failure in one agent returns a degraded report — the coordinator proceeds with whatever it has and notes the gap.

---

### Agent 1 — Trend Analysis Agent

**Goal:** Detect *rate-of-change* (trajectory), not just snapshot values.

**Tracked vitals:** HR, RR, SBP, SpO2, Temperature

**Algorithm:**
1. Extract at least 4 time points across the 6h window per vital
2. Fit a linear slope across the window (`numpy.polyfit` or manual delta)
3. Compare early-window slope vs late-window slope to detect acceleration
4. Score trajectory: `stable` / `slow_change` / `rapid_change` / `reversal`
5. LLM call (Claude): generate a one-sentence plain-English summary per vital

**Output schema:**
```python
@dataclass
class VitalTrend:
    vital: str               # e.g. "heart_rate"
    current: float
    delta_6h: float          # total change over window
    velocity: float          # bpm/hour or equivalent
    acceleration: float      # is the rate itself increasing?
    trend_label: str         # stable / slow_change / rapid_change / reversal
    concern_level: int       # 0=none, 1=watch, 2=concern, 3=urgent
    reasoning: str           # "Heart rate risen 18 bpm over 5h, accelerating last 90 min"

@dataclass
class TrendReport:
    patient_id: str
    vitals: list[VitalTrend]
    overall_trend_score: int  # 0–10, composite
    dominant_concern: str     # which vital is most alarming
    agent_id: str = "trend_agent"
    timestamp: datetime = field(default_factory=datetime.utcnow)
```

**LLM usage:** Claude API — one call per agent run. Prompt includes raw vital time-series; response is the `reasoning` string per vital and a one-sentence `dominant_concern` summary.

---

### Agent 2 — Lab-Vitals Conflict Detection Agent

**Goal:** Detect *cross-signal patterns* that are clinically dangerous but invisible when looking at labs or vitals alone.

**Patterns implemented (MVP):**

| Pattern | Trigger condition |
|---|---|
| Compensated Shock | Normal/stable SBP **AND** rising lactate (≥ 2 mmol/L or ↑ 0.5 in window) |
| Early AKI | Rising creatinine (any rise over baseline) **AND** falling urine output (< 0.5 ml/kg/hr) |
| Pre-Respiratory Failure | Stable SpO2 (≥ 93%) **AND** rising RR (↑ ≥ 4 breaths/min over window) |

**Algorithm:**
1. For each pattern: evaluate boolean trigger logic on `PatientDataObject`
2. If triggered: collect the exact data points that triggered it (evidence trail)
3. LLM call (Claude): generate one-sentence reasoning per detected pattern

**Output schema:**
```python
@dataclass
class ConflictPattern:
    pattern_name: str          # e.g. "compensated_shock"
    severity: int              # 1=mild, 2=moderate, 3=high
    evidence: list[dict]       # exact data points: [{field, value, timestamp}, ...]
    reasoning: str             # one-sentence clinical explanation
    data_gap: bool             # True if a required field was missing

@dataclass
class ConflictReport:
    patient_id: str
    patterns_detected: list[ConflictPattern]
    overall_conflict_score: int  # 0–10
    agent_id: str = "lab_conflict_agent"
    timestamp: datetime = field(default_factory=datetime.utcnow)
```

**Missing data handling:** If a required lab (e.g., lactate) is absent, the pattern is skipped and `data_gap=True` is logged. The coordinator notes the gap in the SBAR+ brief.

---

### Agent 3 — Time Bomb Observer Agent

**Goal:** Identify forward-looking risks in the next 2–3 hours of the incoming shift.

**Checks:**

| Check | Logic |
|---|---|
| Pending labs | `pending_labs` where `ordered_at` was > 2h ago and result not yet returned |
| Medications due | `medications` where `scheduled_time` is within next 2h and `administered=False` |
| PRN gaps | PRN medications not given in 18+ hours (risk of symptom escalation or withdrawal) |

**Output schema:**
```python
@dataclass
class TimeBombItem:
    item: str                # "Troponin result pending since 4h"
    category: str            # "pending_lab" / "med_due" / "prn_gap"
    due_in_minutes: int      # estimated time to maturity / overdue
    risk_if_missed: str      # "If elevated, escalate care plan immediately"
    priority: int            # 1=high, 2=medium, 3=low

@dataclass
class TimeBombReport:
    patient_id: str
    items: list[TimeBombItem]  # sorted by priority then due_in_minutes
    highest_priority: str      # summary of most urgent item
    agent_id: str = "time_bomb_agent"
    timestamp: datetime = field(default_factory=datetime.utcnow)
```

---

## Layer 2 — Coordinator / Synthesis

### Responsibility
Aggregate all three agent reports for one patient into a single `SBARBrief`. Assign overall risk color. Make one LLM call to generate the narrative synthesis.

### Risk Color Logic

| Color | Condition |
|---|---|
| 🔴 Red | Any `concern_level == 3` from Trend Agent OR any `severity == 3` pattern from Conflict Agent |
| 🟡 Yellow | Any `concern_level == 2` OR two or more patterns detected in Conflict Agent |
| 🟢 Green | All vitals stable, no conflict patterns, no high-priority time bombs |

Risk color is **trajectory-based** — a patient can be 🔴 with all vitals in normal range if the trend is alarming.

### LLM Call (Claude — Coordinator)

Single call to `claude-sonnet-4-6` with all three reports serialized as JSON. System prompt establishes clinical context. Claude returns the three narrative sentences (one per agent) that form the SBAR+ body.

### SBARBrief Schema

```python
@dataclass
class SBARBrief:
    patient_id: str
    stay_id: str
    timestamp: datetime
    window_covered: str           # "Last 6 hours: 2026-04-30 06:00 – 12:00"

    # Risk summary
    risk_color: str               # "red" / "yellow" / "green"
    risk_emoji: str               # "🔴" / "🟡" / "🟢"
    risk_score: int               # 0–10 composite

    # SBAR+ narrative (one sentence each)
    situation: str                # "What is changing" — from Trend Agent
    background: str               # "What combination is concerning" — from Conflict Agent
    assessment: str               # "What needs attention in next 2h" — from Time Bomb Agent
    recommendation: str           # Coordinator synthesis sentence

    # Full reasoning (collapsible in UI)
    trend_report: TrendReport
    conflict_report: ConflictReport
    timebomb_report: TimeBombReport

    # Meta
    data_quality_warnings: list[str]  # any missing fields noted
```

---

## Layer 3 — Frontend Dashboard

### Screens

**Screen 1: Patient List**
- Columns: Risk badge | Patient ID | Top concern (1 sentence) | Last updated
- Sorted: 🔴 first, then 🟡, then 🟢
- Auto-refreshes every 60 seconds (or manual refresh button for MVP)

**Screen 2: Patient Brief (click-through)**
- Risk color badge (large, top-left)
- SBAR+ brief (Situation / Background / Assessment / Recommendation)
- Expandable "Full Reasoning" section — all data points, agent outputs
- Timestamp + window covered

### MVP Frontend Choice: Streamlit

Streamlit is the fastest path to a working demo UI in Python without a separate frontend build step. If time allows, upgrade to React + FastAPI.

```
streamlit run app.py
```

Key Streamlit components:
- `st.sidebar` — patient list with color-coded selectbox
- `st.metric` — current vital values with delta arrows
- `st.expander` — collapsible reasoning chain
- `st.badge` / colored markdown — risk color display

---

## API Layer (FastAPI — Backend ↔ Frontend)

### Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/patients` | List all patient IDs with their current risk color and top concern |
| `GET` | `/patients/{patient_id}/brief` | Full `SBARBrief` for one patient |
| `POST` | `/patients/{patient_id}/refresh` | Re-run all 3 agents for a patient and update brief |
| `GET` | `/health` | Basic health check |

### Response format
All responses return JSON. `SBARBrief` is serialized with `dataclasses.asdict()` or Pydantic.

---

## IBM Bob Integration Points

| Where | How Bob is used |
|---|---|
| Agent scaffolding | Bob IDE used to author and iterate on all 3 agent modules |
| BobShell pipeline | MIMIC-IV data ingestion scripts run via BobShell for self-documenting, auditable execution |
| Coordinator orchestration | Bob's multi-agent orchestration wires the `asyncio.gather()` coordinator pattern |
| Code review | Bob's agentic review validates clinical logic and flags data-handling bugs |

---

## LLM API Call Strategy

| Agent | Model | Call type | Purpose |
|---|---|---|---|
| Trend Agent | `claude-sonnet-4-6` | 1 call per patient | Generate `reasoning` text for each vital trend |
| Conflict Agent | `claude-sonnet-4-6` | 1 call per patient | Generate `reasoning` text for each detected pattern |
| Time Bomb Agent | Rule-based only (no LLM) | — | Deterministic logic; LLM not needed |
| Coordinator | `claude-sonnet-4-6` | 1 call per patient | Generate SBAR+ narrative (Situation / Background / Assessment / Recommendation) |

**Total LLM calls per patient: 3**
Time Bomb Agent uses pure Python logic — no LLM call needed since it's deterministic scheduling math.

Note: this can be grouped into single call per patient which will reduce the latency.

---

## Error Handling & Resilience

| Failure mode | Handling |
|---|---|
| Missing vital in MIMIC data | Flag in `data_quality.missing_fields`, agent skips that vital gracefully |
| Missing lab required for conflict pattern | Pattern skipped, `data_gap=True` logged in `ConflictPattern` |
| Agent exception | Returns a degraded report with `error: str` field; coordinator notes partial output |
| LLM API timeout | Retry once with 5s delay; on second failure, use a template fallback string |
| Patient with < 4 vital readings | Trend agent flags `insufficient_data`, scores as `unknown` (not green) |

---

## Project File Structure

```
ICU Silent Deterioration Spotter/
├── data/
│   ├── raw/                   # MIMIC-IV CSV files (gitignored)
│   └── processed/             # Cached PatientDataObjects (JSON)
├── src/
│   ├── loader.py              # Layer 0: DataLoader + PatientDataObject
│   ├── agents/
│   │   ├── trend_agent.py     # Layer 1: Trend Analysis Agent
│   │   ├── conflict_agent.py  # Layer 1: Lab-Vitals Conflict Agent
│   │   └── timebomb_agent.py  # Layer 1: Time Bomb Agent
│   ├── coordinator.py         # Layer 2: Coordinator + SBARBrief
│   ├── schemas.py             # All dataclasses / Pydantic models
│   └── llm.py                 # Anthropic Claude API wrapper
├── api/
│   └── main.py                # FastAPI app
├── frontend/
│   └── app.py                 # Streamlit dashboard
├── pre_comp_preparations/
│   ├── high_level_architecture.txt
│   ├── architecture.md        # ← this file
│   ├── mvp_goals.md
│   ├── action_plan.md
│   ├── competition_submission.md
│   └── ideation_dump.md
├── .env                       # ANTHROPIC_API_KEY, WATSONX_API_KEY (gitignored)
├── requirements.txt
└── README.md
```

---

## What the Draft Was Missing (Improvements Made)

1. **Tech stack was unspecified** — Python + FastAPI + Streamlit + asyncio now explicitly chosen
2. **Coordinator wasn't in the layer diagram** — added as explicit part of Layer 2
3. **No data schemas** — all agent input/output contracts now fully defined
4. **No concurrency mechanism** — `asyncio.gather()` now specified
5. **No LLM strategy** — which agent calls which model is now mapped out (3 Claude calls per patient)
6. **No error handling** — failure modes and graceful degradation now defined
7. **No API layer** — FastAPI endpoints defined to connect backend → frontend
8. **Frontend was vague** — Streamlit chosen for MVP with specific components named
9. **MIMIC-IV tables were unspecified** — exact tables and fields now listed
10. **IBM Bob integration was abstract** — specific integration points with Bob IDE + BobShell now listed
