# Implementation Checklist - ICU Silent Deterioration Spotter

## Planning Phase Complete ✅

The following planning documents have been created:

1. ✅ [`BE/BACKEND_PLAN.md`](BE/BACKEND_PLAN.md) - High-level backend architecture
2. ✅ [`BE/IMPLEMENTATION_GUIDE.md`](BE/IMPLEMENTATION_GUIDE.md) - Detailed implementation guide with file templates
3. ✅ [`BE/README.md`](BE/README.md) - Comprehensive backend documentation

---

## Next Steps: Switch to Code Mode

The planning phase is complete. Now we need to switch to **Code mode** to create the actual files.

---

## Files to Create in Code Mode

### 1. Root Directory

#### `requirements.txt`
**Location:** Root directory  
**Content:** All Python dependencies (see section below)

---

### 2. Backend Directory (BE/)

The following files need to be created as **empty placeholders** with proper docstrings:

#### Layer 0 - Data Loading
- [ ] `BE/loader.py` - MIMIC-IV data loader and PatientDataObject creation

#### Layer 1 - Agents
- [ ] `BE/trend_agent.py` - Trend Analysis Agent (rate-of-change detection)
- [ ] `BE/conflict_agent.py` - Lab-Vitals Conflict Agent (cross-signal patterns)
- [ ] `BE/timebomb_agent.py` - Time Bomb Observer Agent (forward-looking risks)

#### Layer 2 - Coordinator
- [ ] `BE/coordinator.py` - Coordinator and SBAR+ synthesis

#### API Layer
- [ ] `BE/api_main.py` - FastAPI REST endpoints

#### Supporting Modules
- [ ] `BE/schemas.py` - All dataclasses and Pydantic models
- [ ] `BE/llm.py` - LLM API wrapper (Claude/Anthropic)
- [ ] `BE/db.py` - Database operations
- [ ] `BE/scheduler.py` - Pipeline scheduler
- [ ] `BE/config.py` - Configuration and environment variables
- [ ] `BE/utils.py` - Shared utility functions

#### Existing Files
- ✅ `BE/emitter.py` - Already exists (empty placeholder)
- ✅ `BE/BE-Guidelines.md` - Already exists (empty)

---

## Requirements.txt Content

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

## File Template Structure

Each Python file should follow this template:

```python
"""
Module: [filename]
Purpose: [brief description from IMPLEMENTATION_GUIDE.md]
Layer: [0/1/2/API/Support]

Part of ICU Silent Deterioration Spotter
Hackathon: IBM Bob Challenge 2026
"""

import asyncio
from datetime import datetime
from typing import Optional, List

# TODO: Add imports as needed

# TODO: Add constants

# TODO: Add main functions

if __name__ == "__main__":
    # TODO: Add test/demo code
    pass
```

---

## Detailed File Specifications

### `BE/loader.py`
```python
"""
Module: loader.py
Purpose: Load MIMIC-IV data and create PatientDataObject
Layer: 0 (Data Ingestion)

Responsibilities:
- Load MIMIC-IV tables (chartevents, labevents, outputevents, inputevents, prescriptions, admissions)
- Extract 6-hour rolling window per patient
- Resample to 30-minute intervals
- Handle missing data gracefully
- Output clean PatientDataObject
"""
```

### `BE/schemas.py`
```python
"""
Module: schemas.py
Purpose: All dataclasses and Pydantic models
Layer: Support

Key Classes:
- PatientDataObject - Input to agents
- VitalReading, LabReading, OutputReading, MedRecord - Data components
- VitalTrend, TrendReport - Trend agent output
- ConflictPattern, ConflictReport - Conflict agent output
- TimeBombItem, TimeBombReport - Time bomb agent output
- SBARBrief - Final coordinator output
- DataQuality - Missing data tracking
"""
```

### `BE/trend_agent.py`
```python
"""
Module: trend_agent.py
Purpose: Detect rate-of-change in vitals (HR, RR, SBP, SpO2, Temp)
Layer: 1 (Agent)

Responsibilities:
- Calculate slope, velocity, acceleration per vital
- Score trajectory: stable / slow_change / rapid_change / reversal
- Generate plain-English reasoning via LLM
- Output: TrendReport with concern levels (0-3)
"""
```

### `BE/conflict_agent.py`
```python
"""
Module: conflict_agent.py
Purpose: Detect cross-signal patterns (compensated shock, early AKI, pre-respiratory failure)
Layer: 1 (Agent)

Responsibilities:
- Check compensated shock: Normal SBP + rising lactate
- Check early AKI: Rising creatinine + falling urine output
- Check pre-respiratory failure: Stable SpO2 + rising RR
- Generate clinical reasoning via LLM
- Output: ConflictReport with severity levels (1-3)
"""
```

### `BE/timebomb_agent.py`
```python
"""
Module: timebomb_agent.py
Purpose: Identify forward-looking risks (pending labs, meds due, PRN gaps)
Layer: 1 (Agent)

Responsibilities:
- Check pending labs (ordered but not returned)
- Check medications due in next 2 hours
- Check PRN gaps (not given in 18+ hours)
- Prioritize items by urgency
- Output: TimeBombReport (rule-based, no LLM)
"""
```

### `BE/coordinator.py`
```python
"""
Module: coordinator.py
Purpose: Aggregate agent reports and synthesize SBAR+ brief
Layer: 2 (Coordinator)

Responsibilities:
- Run all 3 agents concurrently via asyncio.gather()
- Assign risk color: 🟢 Green / 🟡 Yellow / 🔴 Red
- Generate SBAR+ narrative via LLM
- Output: SBARBrief object
"""
```

### `BE/api_main.py`
```python
"""
Module: api_main.py
Purpose: FastAPI REST endpoints
Layer: API

Endpoints:
- GET /health - Health check
- GET /patients - Ranked patient list
- GET /patients/{patient_id}/brief - Full SBAR brief
- POST /patients/{patient_id}/refresh - Re-run pipeline
"""
```

### `BE/llm.py`
```python
"""
Module: llm.py
Purpose: LLM API wrapper for Claude/Anthropic
Layer: Support

Responsibilities:
- Async Claude API calls
- Prompt formatting for each agent
- Retry logic with fallback
- Error handling
"""
```

### `BE/db.py`
```python
"""
Module: db.py
Purpose: Database operations for persisting SBARBrief objects
Layer: Support

Responsibilities:
- Initialize database tables
- Upsert SBARBrief (save/update)
- Retrieve briefs by patient_id
- Get all patients with risk colors
"""
```

### `BE/scheduler.py`
```python
"""
Module: scheduler.py
Purpose: Automated pipeline execution
Layer: Support

Responsibilities:
- Run pipeline every N seconds (configurable)
- Handle errors gracefully
- Log execution status
"""
```

### `BE/config.py`
```python
"""
Module: config.py
Purpose: Configuration and environment variables
Layer: Support

Environment Variables:
- ANTHROPIC_API_KEY
- WATSONX_API_KEY (optional)
- WINDOW_HOURS (default: 6)
- SCHEDULER_INTERVAL_SECONDS (default: 30)
- DATABASE_URL
- MIMIC_DATA_PATH
"""
```

### `BE/utils.py`
```python
"""
Module: utils.py
Purpose: Shared utility functions
Layer: Support

Utilities:
- Date/time parsing and formatting
- Risk emoji conversion
- Data validation
- Common calculations
"""
```

---

## Architecture Diagram

```
MIMIC-IV Data
     ↓
┌─────────────────────────────────────┐
│  Layer 0: loader.py                 │
│  → PatientDataObject                │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│  Layer 1: Parallel Agents           │
│  ┌──────────┐ ┌──────────┐ ┌──────┐│
│  │ trend_   │ │conflict_ │ │time  ││
│  │ agent.py │ │agent.py  │ │bomb_ ││
│  │          │ │          │ │agent ││
│  └────┬─────┘ └────┬─────┘ └──┬───┘│
└───────┼────────────┼──────────┼────┘
        │            │          │
        └────────────┼──────────┘
                     ▼
┌─────────────────────────────────────┐
│  Layer 2: coordinator.py            │
│  → SBARBrief                        │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│  db.py → Database                   │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│  api_main.py → REST API             │
│  → Frontend Dashboard               │
└─────────────────────────────────────┘
```

---

## Summary

### What We've Done (Plan Mode)
✅ Analyzed team vision from `.agent/` folder  
✅ Created comprehensive backend architecture plan  
✅ Created detailed implementation guide  
✅ Created backend README with full documentation  
✅ Defined all file structures and responsibilities  
✅ Specified requirements.txt content  

### What's Next (Code Mode)
1. Create `requirements.txt` in root directory
2. Create all 12 placeholder Python files in `BE/` folder
3. Each file should have proper docstring and module structure
4. Files should be empty but ready for implementation

### Ready to Switch Modes
The planning is complete. Please approve switching to **Code mode** to create the actual files.

---

## Questions for User

Before switching to Code mode, please confirm:

1. ✅ Are you satisfied with the flat file structure in BE/ folder?
2. ❓ Should we use SQLite or PostgreSQL for the database?
3. ❓ Do you want any additional files or modifications?
4. ❓ Ready to switch to Code mode to create the files?
