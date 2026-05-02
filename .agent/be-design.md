# ICU Silent Deterioration Spotter — Backend Design

> Expanded from initial design notes. Covers system flow, the two core subsystems,
> and the pre-hackathon checklist for the BE team.

---

## How the System Works — End-to-End

```
┌─────────────────────────────────────────────────────────────────────────┐
│  MIMIC-IV Demo Dataset  (CSV / Parquet on disk)                         │
│  or Live Simulator      (emits patient vitals/labs every N seconds)     │
└───────────────────────────────┬─────────────────────────────────────────┘
                                │ raw rows
                                ▼
┌───────────────────────────────────────────────────────────────────────┐
│  Subsystem 1 — Scheduled Pipeline  (runs every 30 s for demo)         │
│                                                                       │
│  ┌─────────────┐    ┌──────────────────────────────────────────────┐  │
│  │  DataLoader │───▶│  PatientDataObject  (6-hour rolling window)  │  │
│  └─────────────┘    └──────────────────────────────────────────────┘  │
│                                          │                            │
│                          asyncio.gather()│                            │
│               ┌──────────────────────────┼──────────────────────┐    │
│               ▼                          ▼                       ▼    │
│        Trend Agent            Conflict Agent            TimeBomb Agent │
│        (LLM call)             (LLM call)                (rule-based)  │
│               │                          │                       │    │
│               └──────────────────────────┼──────────────────────┘    │
│                                          ▼                            │
│                               Coordinator (LLM call)                  │
│                               → SBARBrief object                      │
│                                          │                            │
│                                          ▼                            │
│                               Persist to Database                     │
└───────────────────────────────────────────────────────────────────────┘
                                          │
                                          │ JSON
                                          ▼
┌───────────────────────────────────────────────────────────────────────┐
│  Subsystem 2 — API Layer  (FastAPI)                                   │
│  GET /patients          → ranked patient list                         │
│  GET /patients/:id/brief → full SBARBrief                             │
│  POST /patients/:id/refresh → trigger fresh pipeline run              │
│  GET /health                                                          │
└───────────────────────────────────────────────────────────────────────┘
                                          │
                                          ▼
                              Frontend (Streamlit / React)
```

---

## Subsystem 1 — Scheduled Pipeline

### What it does
Every 30 seconds the pipeline runs for all active patients (or a single patient
in single-patient demo mode). In production this would be event-driven via a
message broker (e.g. RabbitMQ) rather than a polling interval.

### Steps

| Step | Module | Detail |
|------|--------|--------|
| **1. Ingest** | `src/loader.py` | Reads MIMIC-IV tables (`chartevents`, `labevents`, `outputevents`, `inputevents`, `prescriptions`, `admissions`). Builds a `PatientDataObject` covering the last 6-hour window, resampled to 30-min intervals. Missing values flagged in `data_quality`. |
| **2. Run agents (parallel)** | `src/agents/` | All three agents receive the same `PatientDataObject` and run concurrently via `asyncio.gather()`. Each agent is independently async and does not share state. |
| **3. Trend Agent** | `src/agents/trend_agent.py` | Computes slope, velocity, acceleration per vital. One Claude API call to generate `reasoning` text per vital. Returns `TrendReport`. |
| **4. Conflict Agent** | `src/agents/conflict_agent.py` | Evaluates cross-signal patterns (compensated shock, early AKI, pre-respiratory failure). One Claude API call for pattern reasoning. Returns `ConflictReport`. |
| **5. TimeBomb Agent** | `src/agents/timebomb_agent.py` | Pure rule-based logic — checks pending labs, upcoming meds, PRN gaps. No LLM call. Returns `TimeBombReport`. |
| **6. Coordinate** | `src/coordinator.py` | Aggregates all three reports. Applies risk color logic. One Claude API call to generate the SBAR+ narrative. Returns `SBARBrief`. |
| **7. Persist** | `src/db.py` (TBD) | Upserts `SBARBrief` to the database keyed on `(patient_id, stay_id)`. Frontend always reads the latest persisted brief. |

### LLM Call Budget

| Agent | Model | Calls per patient |
|-------|-------|-------------------|
| Trend Agent | `claude-sonnet-4-6` | 1 |
| Conflict Agent | `claude-sonnet-4-6` | 1 |
| TimeBomb Agent | — | 0 (rule-based) |
| Coordinator | `claude-sonnet-4-6` | 1 |
| **Total** | | **3 per patient** |

> These 3 calls can be batched into 1 call per patient to reduce latency if needed.

### Scheduler Note
For the hackathon demo, the scheduler is a simple `asyncio` loop or APScheduler
job that fires every 30 seconds. In production this step would be replaced by a
RabbitMQ consumer that triggers on new data events.

---

## Subsystem 2 — API Layer

Built with **FastAPI** (async-native, auto-generates OpenAPI docs).

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Liveness check |
| `GET` | `/patients` | Ranked patient list (red → yellow → green) |
| `GET` | `/patients/{patient_id}/brief` | Full `SBARBrief` for one patient |
| `POST` | `/patients/{patient_id}/refresh` | Re-run pipeline for a patient on demand |

Full request/response schemas are in [api-spec.yaml](./api-spec.yaml).

---

## Data Model Notes

The definitive data model is driven by the MIMIC-IV tables. Key objects:

- **`PatientDataObject`** — pipeline-internal; never sent over the API
- **`TrendReport`** / **`ConflictReport`** / **`TimeBombReport`** — agent outputs; embedded in the brief
- **`SBARBrief`** — the primary API response object

The exact field values, ranges, and units can only be finalised after exploring
the real MIMIC-IV demo dataset. This is reflected in the pre-hackathon checklist below.

---

## Pre-Hackathon Checklist

These tasks must be completed **before** the hackathon starts (by April 30, 2026)
so the team can code without blockers.

### Phase 1 — Data Exploration

- [ ] **Download MIMIC-IV demo dataset** from PhysioNet (no credentialing needed for the demo subset)
- [ ] **Explore raw tables** — open each relevant CSV and understand its columns, types, and row counts:
  - `chartevents` (vitals: HR, RR, SBP, DBP, SpO2, Temp)
  - `labevents` (labs: Lactate, Creatinine, WBC, Hemoglobin, Troponin)
  - `outputevents` (urine output)
  - `inputevents` (IV fluids)
  - `prescriptions` (medications)
  - `admissions` (patient metadata, ICU stay IDs)
- [ ] **Identify `itemid` values** for each vital and lab we care about — MIMIC uses numeric item IDs, not field names
- [ ] **Check data density** — how many patients have complete vitals + labs within a 6-hour window? This determines demo viability
- [ ] **Document findings** — note units, value ranges, and any data quality issues per field

### Phase 2 — Data Model Finalisation

- [ ] **Confirm field names and units** for `VitalReading`, `LabReading`, `OutputReading` based on exploration
- [ ] **Decide on normal ranges** for each vital/lab — needed for Trend Agent concern-level thresholds
- [ ] **Validate conflict pattern trigger logic** against real data:
  - Compensated Shock: does the dataset have co-occurring stable SBP + rising lactate?
  - Early AKI: rising creatinine + falling urine output?
  - Pre-Respiratory Failure: stable SpO2 + rising RR?
- [ ] **Update `api-spec.yaml`** — patch any field names, types, or enums that differ from real data
- [ ] **Settle on database** — SQLite (zero-setup, fine for demo) vs PostgreSQL

### Phase 3 — Environment & Tooling

- [ ] **Set up `.env` file** with required keys:
  - `ANTHROPIC_API_KEY`
  - `WATSONX_API_KEY` (if using Granite for structured scoring)
  - `WINDOW_HOURS=6`
  - `SCHEDULER_INTERVAL_SECONDS=30`
- [ ] **Confirm Anthropic API access** — run a minimal test call to `claude-sonnet-4-6`
- [ ] **Install and verify dependencies** — `fastapi`, `uvicorn`, `anthropic`, `pandas`, `polars`, `numpy`, `apscheduler` (or equivalent)
- [ ] **Agree on Python version** — 3.11+ (required for `asyncio` features used in the architecture)
- [ ] **Create project scaffold** — match the directory structure in `architecture.md`:
  ```
  src/loader.py
  src/agents/trend_agent.py
  src/agents/conflict_agent.py
  src/agents/timebomb_agent.py
  src/coordinator.py
  src/schemas.py
  src/llm.py
  api/main.py
  ```

### Phase 4 — Alignment Between BE and FE

- [ ] **Both partners review `api-spec.yaml`** — agree on response shapes before writing any code
- [ ] **Agree on mock data format** — FE can start building against a static JSON fixture while BE builds the real pipeline
- [ ] **Decide on CORS settings** for local dev (FE and BE will run on different ports)
- [ ] **Agree on error response shape** — `{"detail": "..."}` is the current spec; confirm FE can handle it

---

## Open Questions (Resolve Before Hackathon)

| # | Question | Owner |
|---|----------|-------|
| 1 | Which MIMIC-IV `itemid` values map to each vital/lab? | BE |
| 2 | Will we use SQLite or PostgreSQL for persisting briefs? | BE |
| 3 | Should the 3 LLM calls per patient be batched into 1 to reduce latency? | BE |
| 4 | What is the static JSON fixture shape for FE to mock against? | BE + FE |
| 5 | Do we need authentication on the API for the demo? (Recommended: no, keep it open) | BE |
