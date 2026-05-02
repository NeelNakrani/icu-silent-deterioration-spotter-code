# ICU Silent Deterioration Spotter - Backend

> Multi-agent system for early detection of patient deterioration in ICU settings using MIMIC-IV data

---

## Overview

This backend implements a three-layer architecture with parallel agent execution:

- **Layer 0**: Data ingestion from MIMIC-IV
- **Layer 1**: Three concurrent agents (Trend, Conflict, Time Bomb)
- **Layer 2**: Coordinator synthesizing SBAR+ briefs
- **API Layer**: FastAPI REST endpoints for frontend

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  MIMIC-IV Data → DataLoader → PatientDataObject             │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  Parallel Agents (asyncio.gather)                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Trend Agent  │  │Conflict Agent│  │ TimeBomb Agent│      │
│  │  (LLM call)  │  │  (LLM call)  │  │ (rule-based) │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
└─────────┼──────────────────┼──────────────────┼─────────────┘
          │                  │                  │
          └──────────────────┼──────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────┐
│  Coordinator (LLM call) → SBARBrief → Database              │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  FastAPI REST API → Frontend Dashboard                      │
└─────────────────────────────────────────────────────────────┘
```

---

## File Structure

```
BE/
├── emitter.py              # Data emitter/simulator
├── loader.py               # Layer 0: MIMIC-IV data loader
├── schemas.py              # All dataclasses and Pydantic models
├── trend_agent.py          # Layer 1: Trend Analysis Agent
├── conflict_agent.py       # Layer 1: Lab-Vitals Conflict Agent
├── timebomb_agent.py       # Layer 1: Time Bomb Observer Agent
├── coordinator.py          # Layer 2: Coordinator & SBAR synthesis
├── llm.py                  # LLM API wrapper (Claude/Anthropic)
├── api_main.py             # FastAPI application
├── db.py                   # Database operations
├── scheduler.py            # Pipeline scheduler
├── config.py               # Configuration and environment variables
├── utils.py                # Shared utility functions
├── BE-Guidelines.md        # Backend development guidelines
├── BACKEND_PLAN.md         # High-level backend plan
├── IMPLEMENTATION_GUIDE.md # Detailed implementation guide
└── README.md               # This file
```

---

## Key Components

### Layer 0: Data Loading
**File:** [`loader.py`](loader.py)

Loads MIMIC-IV tables and creates structured `PatientDataObject`:
- 6-hour rolling window (configurable)
- 30-minute interval resampling
- Missing data flagging
- Tables: chartevents, labevents, outputevents, inputevents, prescriptions, admissions

### Layer 1: Agents

#### Trend Agent
**File:** [`trend_agent.py`](trend_agent.py)

Detects rate-of-change in vitals:
- Tracks: HR, RR, SBP, SpO2, Temperature
- Calculates: slope, velocity, acceleration
- Scores: stable / slow_change / rapid_change / reversal
- Output: `TrendReport` with concern levels (0-3)

#### Conflict Agent
**File:** [`conflict_agent.py`](conflict_agent.py)

Detects cross-signal patterns:
- **Compensated Shock**: Normal SBP + rising lactate
- **Early AKI**: Rising creatinine + falling urine output
- **Pre-Respiratory Failure**: Stable SpO2 + rising RR
- Output: `ConflictReport` with severity levels (1-3)

#### Time Bomb Agent
**File:** [`timebomb_agent.py`](timebomb_agent.py)

Identifies forward-looking risks:
- Pending labs (ordered but not returned)
- Medications due in next 2 hours
- PRN gaps (not given in 18+ hours)
- Output: `TimeBombReport` with priority-sorted items

### Layer 2: Coordinator
**File:** [`coordinator.py`](coordinator.py)

Synthesizes all agent outputs:
- Runs agents concurrently via `asyncio.gather()`
- Assigns risk color: 🟢 Green / 🟡 Yellow / 🔴 Red
- Generates SBAR+ narrative via LLM
- Output: `SBARBrief` object

### API Layer
**File:** [`api_main.py`](api_main.py)

FastAPI REST endpoints:
- `GET /health` - Health check
- `GET /patients` - Ranked patient list
- `GET /patients/{patient_id}/brief` - Full SBAR brief
- `POST /patients/{patient_id}/refresh` - Re-run pipeline

---

## Data Models

### Input: PatientDataObject
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

### Output: SBARBrief
```python
@dataclass
class SBARBrief:
    patient_id: str
    stay_id: str
    timestamp: datetime
    window_covered: str
    risk_color: str              # "red" / "yellow" / "green"
    risk_emoji: str              # "🔴" / "🟡" / "🟢"
    risk_score: int              # 0-10
    situation: str               # What is changing
    background: str              # What combination is concerning
    assessment: str              # What needs attention in next 2h
    recommendation: str          # Coordinator synthesis
    trend_report: TrendReport
    conflict_report: ConflictReport
    timebomb_report: TimeBombReport
    data_quality_warnings: list[str]
```

---

## LLM Strategy

| Agent | Model | Calls per Patient | Purpose |
|-------|-------|-------------------|---------|
| Trend Agent | Claude Sonnet 4 | 1 | Generate reasoning for vital trends |
| Conflict Agent | Claude Sonnet 4 | 1 | Generate reasoning for patterns |
| Time Bomb Agent | — | 0 | Rule-based only |
| Coordinator | Claude Sonnet 4 | 1 | Generate SBAR+ narrative |
| **Total** | | **3** | |

> Note: These 3 calls can be batched into 1 call per patient to reduce latency

---

## Environment Setup

### Required Environment Variables

Create a `.env` file in the project root:

```bash
# LLM API Keys
ANTHROPIC_API_KEY=your_claude_api_key_here
WATSONX_API_KEY=your_watsonx_key_here  # Optional

# Pipeline Configuration
WINDOW_HOURS=6
SCHEDULER_INTERVAL_SECONDS=30

# Database
DATABASE_URL=sqlite:///./icu_spotter.db  # or PostgreSQL URL

# MIMIC-IV Data
MIMIC_DATA_PATH=./data/mimic-iv/
```

### Installation

```bash
# Install dependencies
pip install -r ../requirements.txt

# Or with virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r ../requirements.txt
```

---

## Running the System

### 1. Start the API Server
```bash
uvicorn api_main:app --reload --port 8000
```

### 2. Start the Scheduler (separate terminal)
```bash
python scheduler.py
```

### 3. Access API Documentation
```
http://localhost:8000/docs
```

---

## Development Workflow

### Phase 1: Foundation
1. Define all schemas in [`schemas.py`](schemas.py)
2. Set up configuration in [`config.py`](config.py)
3. Implement LLM wrapper in [`llm.py`](llm.py)

### Phase 2: Data Layer
4. Implement data loader in [`loader.py`](loader.py)
5. Set up database in [`db.py`](db.py)
6. Test with sample MIMIC-IV data

### Phase 3: Agents
7. Implement [`trend_agent.py`](trend_agent.py)
8. Implement [`conflict_agent.py`](conflict_agent.py)
9. Implement [`timebomb_agent.py`](timebomb_agent.py)
10. Test each agent independently

### Phase 4: Coordination
11. Implement [`coordinator.py`](coordinator.py)
12. Test full pipeline with `asyncio.gather()`

### Phase 5: API & Automation
13. Implement FastAPI endpoints in [`api_main.py`](api_main.py)
14. Implement scheduler in [`scheduler.py`](scheduler.py)
15. End-to-end testing

---

## Testing

### Unit Tests
```bash
pytest tests/test_agents.py
pytest tests/test_coordinator.py
pytest tests/test_api.py
```

### Integration Tests
```bash
pytest tests/test_integration.py
```

---

## Error Handling

| Failure Mode | Handling |
|--------------|----------|
| Missing vital in MIMIC data | Flag in `data_quality.missing_fields`, agent skips gracefully |
| Missing lab for conflict pattern | Pattern skipped, `data_gap=True` logged |
| Agent exception | Returns degraded report with `error` field |
| LLM API timeout | Retry once with 5s delay, fallback to template |
| Patient with < 4 vital readings | Flag `insufficient_data`, score as `unknown` |

---

## Performance Considerations

- **Concurrency**: All 3 agents run in parallel via `asyncio.gather()`
- **LLM Calls**: 3 per patient (can be batched to 1)
- **Database**: Upsert pattern for latest brief per patient
- **Caching**: Consider caching PatientDataObject for repeated queries

---

## MIMIC-IV Data Requirements

### Required Tables
- `chartevents` - Vitals (HR, RR, SBP, DBP, SpO2, Temp)
- `labevents` - Labs (Lactate, Creatinine, WBC, Hemoglobin, Troponin)
- `outputevents` - Urine output
- `inputevents` - IV fluids
- `prescriptions` - Medications
- `admissions` - Patient metadata, ICU stay IDs

### Data Access
- **Demo Dataset**: No credentialing needed (subset of MIMIC-IV)
- **Full Dataset**: Requires PhysioNet credentialing

---

## Contributing

1. Follow the implementation guide in [`IMPLEMENTATION_GUIDE.md`](IMPLEMENTATION_GUIDE.md)
2. Use type hints for all functions
3. Add docstrings to all modules and functions
4. Test each component independently before integration
5. Update this README as the system evolves

---

## Resources

- [MIMIC-IV Documentation](https://mimic.mit.edu/)
- [Anthropic Claude API](https://docs.anthropic.com/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Architecture Document](../.agent/architecture.md)
- [MVP Goals](../.agent/mvp_goals.md)

---

## License

MIT License - See LICENSE file in project root

---

## Team

ICU Silent Deterioration Spotter  
IBM Bob Challenge 2026  
Hackathon: April 30 - May 3, 2026