# Backend Implementation Plan

## Overview
This document outlines the complete backend structure for the ICU Silent Deterioration Spotter, organized as a flat structure within the BE folder for hackathon simplicity.

## File Structure

```
BE/
├── emitter.py                    # [EXISTS] Data emitter/simulator
├── loader.py                     # Layer 0: MIMIC-IV data loader
├── schemas.py                    # All dataclasses and Pydantic models
├── trend_agent.py                # Layer 1: Trend Analysis Agent
├── conflict_agent.py             # Layer 1: Lab-Vitals Conflict Agent
├── timebomb_agent.py             # Layer 1: Time Bomb Observer Agent
├── coordinator.py                # Layer 2: Coordinator & SBAR synthesis
├── llm.py                        # LLM API wrapper (Claude/Anthropic)
├── api_main.py                   # FastAPI application
├── db.py                         # Database operations (SQLite/PostgreSQL)
├── scheduler.py                  # Pipeline scheduler (asyncio/APScheduler)
├── config.py                     # Configuration and environment variables
├── utils.py                      # Shared utility functions
├── BE-Guidelines.md              # [EXISTS] Backend guidelines
└── BACKEND_PLAN.md               # [THIS FILE] Implementation plan
```

## Layer Breakdown

### Layer 0 - Data Ingestion
**File:** [`loader.py`](BE/loader.py)
- Load MIMIC-IV tables (chartevents, labevents, outputevents, inputevents, prescriptions, admissions)
- Extract 6-hour rolling window per patient
- Resample to 30-minute intervals
- Output: `PatientDataObject`

### Layer 1 - Parallel Agents
**Files:** 
- [`trend_agent.py`](BE/trend_agent.py) - Detects rate-of-change in vitals
- [`conflict_agent.py`](BE/conflict_agent.py) - Detects cross-signal patterns
- [`timebomb_agent.py`](BE/timebomb_agent.py) - Identifies forward-looking risks

All agents run concurrently via `asyncio.gather()`

### Layer 2 - Coordinator
**File:** [`coordinator.py`](BE/coordinator.py)
- Aggregates all three agent reports
- Assigns risk color (🟢/🟡/🔴)
- Generates SBAR+ narrative via LLM
- Output: `SBARBrief`

### API Layer
**File:** [`api_main.py`](BE/api_main.py)
- FastAPI endpoints:
  - `GET /health` - Health check
  - `GET /patients` - Ranked patient list
  - `GET /patients/{patient_id}/brief` - Full SBAR brief
  - `POST /patients/{patient_id}/refresh` - Re-run pipeline

### Supporting Modules
- [`schemas.py`](BE/schemas.py) - All data models and type definitions
- [`llm.py`](BE/llm.py) - Anthropic Claude API wrapper
- [`db.py`](BE/db.py) - Database persistence layer
- [`scheduler.py`](BE/scheduler.py) - Automated pipeline execution
- [`config.py`](BE/config.py) - Environment configuration
- [`utils.py`](BE/utils.py) - Shared utilities

## Key Data Models (from schemas.py)

### PatientDataObject
```python
@dataclass
class PatientDataObject:
    patient_id: str
    stay_id: str
    window_start: datetime
    window_end: datetime
    vitals: list[VitalReading]
    labs: list[LabReading]
    urine_output: list[OutputReading]
    medications: list[MedRecord]
    pending_labs: list[PendingLab]
    data_quality: DataQuality
```

### Agent Outputs
- `TrendReport` - From trend_agent.py
- `ConflictReport` - From conflict_agent.py
- `TimeBombReport` - From timebomb_agent.py

### Final Output
- `SBARBrief` - Synthesized risk assessment with SBAR+ narrative

## LLM Call Strategy
- **Trend Agent**: 1 Claude call per patient (reasoning for vital trends)
- **Conflict Agent**: 1 Claude call per patient (reasoning for patterns)
- **Time Bomb Agent**: 0 calls (rule-based only)
- **Coordinator**: 1 Claude call per patient (SBAR+ narrative)
- **Total**: 3 Claude API calls per patient

## Concurrency Model
```python
async def run_all_agents(patient_data: PatientDataObject):
    trend, conflict, timebomb = await asyncio.gather(
        trend_agent(patient_data),
        lab_conflict_agent(patient_data),
        time_bomb_agent(patient_data),
    )
    return trend, conflict, timebomb
```

## Environment Variables (config.py)
- `ANTHROPIC_API_KEY` - Claude API access
- `WATSONX_API_KEY` - IBM watsonx.ai (optional)
- `WINDOW_HOURS` - Data window size (default: 6)
- `SCHEDULER_INTERVAL_SECONDS` - Pipeline frequency (default: 30)
- `DATABASE_URL` - Database connection string

## Next Steps
1. Create all placeholder files with proper docstrings
2. Define all schemas in schemas.py
3. Implement data loader (loader.py)
4. Implement each agent independently
5. Implement coordinator
6. Build FastAPI endpoints
7. Add scheduler for automated runs
8. Test with MIMIC-IV demo data