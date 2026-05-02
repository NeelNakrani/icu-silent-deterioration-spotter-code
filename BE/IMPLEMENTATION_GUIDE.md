# Backend Implementation Guide

## Complete File Structure & Content Plan

This guide provides the complete structure and placeholder content for all backend files.

---

## 1. Layer 0 - Data Loading

### File: `loader.py`
**Purpose:** Load MIMIC-IV data and create PatientDataObject

**Key Functions:**
- `load_mimic_tables()` - Load raw MIMIC-IV CSV/Parquet files
- `extract_patient_window()` - Extract 6-hour rolling window
- `resample_to_intervals()` - Resample to 30-min intervals
- `create_patient_data_object()` - Build PatientDataObject

**Dependencies:** pandas, polars, datetime

---

## 2. Layer 1 - Agent Files

### File: `trend_agent.py`
**Purpose:** Detect rate-of-change in vitals (HR, RR, SBP, SpO2, Temp)

**Key Functions:**
- `async def analyze_trends(patient_data: PatientDataObject) -> TrendReport`
- `calculate_slope()` - Linear regression on time series
- `detect_acceleration()` - Compare early vs late window slopes
- `score_trajectory()` - Assign concern level (0-3)
- `generate_reasoning()` - LLM call for plain-English summary

**Output:** TrendReport with VitalTrend objects

---

### File: `conflict_agent.py`
**Purpose:** Detect cross-signal patterns (compensated shock, early AKI, pre-respiratory failure)

**Key Functions:**
- `async def detect_conflicts(patient_data: PatientDataObject) -> ConflictReport`
- `check_compensated_shock()` - Normal SBP + rising lactate
- `check_early_aki()` - Rising creatinine + falling urine output
- `check_pre_respiratory_failure()` - Stable SpO2 + rising RR
- `generate_pattern_reasoning()` - LLM call for clinical explanation

**Output:** ConflictReport with ConflictPattern objects

---

### File: `timebomb_agent.py`
**Purpose:** Identify forward-looking risks (pending labs, meds due, PRN gaps)

**Key Functions:**
- `async def identify_timebombs(patient_data: PatientDataObject) -> TimeBombReport`
- `check_pending_labs()` - Labs ordered but not returned
- `check_medications_due()` - Scheduled meds in next 2h
- `check_prn_gaps()` - PRN not given in 18+ hours
- `prioritize_items()` - Sort by urgency

**Output:** TimeBombReport with TimeBombItem objects (rule-based, no LLM)

---

## 3. Layer 2 - Coordinator

### File: `coordinator.py`
**Purpose:** Aggregate agent reports and synthesize SBAR+ brief

**Key Functions:**
- `async def run_all_agents(patient_data: PatientDataObject) -> tuple`
- `async def coordinate(patient_data: PatientDataObject) -> SBARBrief`
- `calculate_risk_color()` - Assign 🟢/🟡/🔴 based on agent outputs
- `generate_sbar_narrative()` - LLM call for SBAR+ synthesis
- `aggregate_reports()` - Combine all agent outputs

**Concurrency:**
```python
trend, conflict, timebomb = await asyncio.gather(
    trend_agent(patient_data),
    conflict_agent(patient_data),
    timebomb_agent(patient_data),
)
```

**Output:** SBARBrief object

---

## 4. API Layer

### File: `api_main.py`
**Purpose:** FastAPI REST endpoints

**Endpoints:**
- `GET /health` - Health check
- `GET /patients` - List all patients with risk colors
- `GET /patients/{patient_id}/brief` - Full SBAR brief for one patient
- `POST /patients/{patient_id}/refresh` - Re-run pipeline on demand

**Dependencies:** FastAPI, uvicorn, pydantic

---

## 5. Supporting Files

### File: `schemas.py`
**Purpose:** All dataclasses and Pydantic models

**Key Classes:**
- `PatientDataObject` - Input to agents
- `VitalReading`, `LabReading`, `OutputReading`, `MedRecord` - Data components
- `VitalTrend`, `TrendReport` - Trend agent output
- `ConflictPattern`, `ConflictReport` - Conflict agent output
- `TimeBombItem`, `TimeBombReport` - Time bomb agent output
- `SBARBrief` - Final coordinator output
- `DataQuality` - Missing data tracking

---

### File: `llm.py`
**Purpose:** LLM API wrapper for Claude/Anthropic

**Key Functions:**
- `async def call_claude(prompt: str, system: str) -> str`
- `format_trend_prompt()` - Prompt for trend reasoning
- `format_conflict_prompt()` - Prompt for pattern reasoning
- `format_sbar_prompt()` - Prompt for SBAR synthesis
- `handle_api_timeout()` - Retry logic with fallback

**Dependencies:** anthropic, asyncio

---

### File: `db.py`
**Purpose:** Database operations for persisting SBARBrief objects

**Key Functions:**
- `init_db()` - Create tables
- `upsert_brief(brief: SBARBrief)` - Save/update patient brief
- `get_brief(patient_id: str) -> SBARBrief`
- `get_all_patients() -> list[dict]` - Patient list with risk colors

**Database:** SQLite (MVP) or PostgreSQL

---

### File: `scheduler.py`
**Purpose:** Automated pipeline execution

**Key Functions:**
- `async def run_pipeline()` - Execute full pipeline for all patients
- `schedule_pipeline()` - Set up recurring execution
- `handle_pipeline_error()` - Error handling and logging

**Dependencies:** APScheduler or asyncio loop

---

### File: `config.py`
**Purpose:** Configuration and environment variables

**Key Variables:**
- `ANTHROPIC_API_KEY` - Claude API key
- `WATSONX_API_KEY` - IBM watsonx.ai key (optional)
- `WINDOW_HOURS` - Data window size (default: 6)
- `SCHEDULER_INTERVAL_SECONDS` - Pipeline frequency (default: 30)
- `DATABASE_URL` - Database connection string
- `MIMIC_DATA_PATH` - Path to MIMIC-IV files

**Dependencies:** python-dotenv

---

### File: `utils.py`
**Purpose:** Shared utility functions

**Key Functions:**
- `parse_datetime()` - Date/time parsing
- `calculate_delta()` - Time difference calculations
- `format_risk_emoji()` - Convert risk color to emoji
- `validate_patient_data()` - Data quality checks

---

### File: `emitter.py`
**Purpose:** [EXISTING] Data emitter/simulator for testing

**Note:** This file already exists as a placeholder. It will simulate patient data streams for testing without requiring full MIMIC-IV access.

---

## 6. Requirements.txt Content

```txt
# Core Python Dependencies
python>=3.11

# Data Processing
pandas>=2.0.0
polars>=0.19.0
numpy>=1.24.0

# API Framework
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
pydantic>=2.0.0

# LLM Integration
anthropic>=0.7.0
ibm-watsonx-ai>=0.1.0  # Optional for Granite

# Async & Scheduling
asyncio>=3.4.3
apscheduler>=3.10.0

# Database
sqlalchemy>=2.0.0
aiosqlite>=0.19.0  # For async SQLite
psycopg2-binary>=2.9.0  # Optional for PostgreSQL

# Configuration
python-dotenv>=1.0.0

# Utilities
python-dateutil>=2.8.0
pytz>=2023.3

# Testing (Optional)
pytest>=7.4.0
pytest-asyncio>=0.21.0
httpx>=0.25.0  # For testing FastAPI

# Development (Optional)
black>=23.0.0
flake8>=6.0.0
mypy>=1.5.0
```

---

## 7. Implementation Order

### Phase 1: Foundation
1. Create all placeholder files with docstrings
2. Define all schemas in [`schemas.py`](BE/schemas.py)
3. Set up configuration in [`config.py`](BE/config.py)
4. Implement LLM wrapper in [`llm.py`](BE/llm.py)

### Phase 2: Data Layer
5. Implement data loader in [`loader.py`](BE/loader.py)
6. Set up database in [`db.py`](BE/db.py)
7. Test with sample MIMIC-IV data

### Phase 3: Agents
8. Implement [`trend_agent.py`](BE/trend_agent.py)
9. Implement [`conflict_agent.py`](BE/conflict_agent.py)
10. Implement [`timebomb_agent.py`](BE/timebomb_agent.py)
11. Test each agent independently

### Phase 4: Coordination
12. Implement [`coordinator.py`](BE/coordinator.py)
13. Test full pipeline with asyncio.gather()

### Phase 5: API & Automation
14. Implement FastAPI endpoints in [`api_main.py`](BE/api_main.py)
15. Implement scheduler in [`scheduler.py`](BE/scheduler.py)
16. End-to-end testing

---

## 8. File Templates

### Standard Python File Header
```python
"""
Module: [filename]
Purpose: [brief description]
Layer: [0/1/2/API/Support]

Part of ICU Silent Deterioration Spotter
Hackathon: IBM Bob Challenge 2026
"""

import asyncio
from datetime import datetime
from typing import Optional, List

# Import schemas
from schemas import PatientDataObject, [OtherSchemas]

# Module-specific imports
# ...

# Constants
# ...

# Main functions
# ...
```

---

## 9. Testing Strategy

### Unit Tests
- Test each agent independently with mock PatientDataObject
- Test coordinator with mock agent outputs
- Test API endpoints with mock database

### Integration Tests
- Test full pipeline with sample MIMIC-IV data
- Test concurrent agent execution
- Test error handling (missing data, API timeouts)

### Demo Preparation
- Identify 3-5 MIMIC-IV patients with known deterioration
- Verify system flags them 🔴 before the event
- Document exact data points that triggered flags

---

## 10. Next Steps

1. **Review this plan** - Ensure all team members understand the structure
2. **Switch to Code mode** - Create all placeholder files
3. **Create requirements.txt** - In root directory
4. **Begin implementation** - Follow Phase 1-5 order
5. **Test incrementally** - Don't wait until everything is done

---

## Questions to Resolve

- [ ] SQLite or PostgreSQL for database?
- [ ] Should we batch 3 LLM calls into 1 per patient?
- [ ] What MIMIC-IV itemid values map to each vital/lab?
- [ ] Do we need authentication on API endpoints?
- [ ] Should emitter.py simulate real-time or batch data?
