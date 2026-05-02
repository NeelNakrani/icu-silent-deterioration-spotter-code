# Layer 0 Implementation - Data Emitter & Loader

## Overview

Layer 0 is the foundation of the ICU Silent Deterioration Spotter backend. It handles data ingestion, simulation, and transformation into structured `PatientDataObject` instances that feed into Layer 1 agents.

## Components

### 1. `emitter.py` - Data Emitter/Simulator

**Purpose:** Simulates real-time ICU data streaming from MIMIC-IV dataset.

**Key Features:**
- Loads master_multi_patient_timeline.csv
- Streams data in real-time with configurable speed multiplier
- Supports both single-patient and multi-patient emission
- Provides snapshot functionality for testing
- Respects original charttime intervals

**Main Classes:**
- `DataEmitter`: Core emitter class with async generators

**Key Methods:**
```python
# Load data
emitter = DataEmitter(speed_multiplier=1.0)
emitter.load_data()

# Get patient list
patients = emitter.get_patient_list()

# Stream single patient data
async for window in emitter.emit_patient(patient_id, window_hours=6):
    # Process window data
    pass

# Stream all patients in batches
async for batch in emitter.emit_all_patients(window_minutes=30):
    # Process batch
    pass

# Get snapshot (for testing)
snapshot = emitter.get_snapshot(patient_id, window_hours=6)
```

### 2. `loader.py` - Data Loader & Transformer

**Purpose:** Transforms raw MIMIC-IV data into structured `PatientDataObject` instances.

**Key Features:**
- Categorizes data by type (vitals, labs, outputs)
- Maps MIMIC-IV itemids to clinical labels
- Calculates data quality metrics
- Resamples to fixed intervals (e.g., 30 minutes)
- Extracts rolling windows

**Main Classes:**
- `DataLoader`: Core loader class

**Key Methods:**
```python
# Create loader
loader = DataLoader()

# Create PatientDataObject from emitter data
pdo = create_pdo_from_emitter_data(emitter_snapshot)

# Resample to fixed intervals
resampled_pdo = loader.resample_to_intervals(pdo, interval_minutes=30)

# Extract rolling window
pdo = loader.extract_rolling_window(patient_id, at_time, window_hours=6)
```

### 3. `schemas.py` - Data Models

**Purpose:** Defines all data structures used throughout the system.

**Key Data Models:**

#### Layer 0 Models
- `VitalReading`: Single vital sign reading
- `LabReading`: Single lab result
- `OutputReading`: Urine output reading
- `MedRecord`: Medication record
- `PendingLab`: Pending lab order
- `DataQuality`: Data quality metrics
- `PatientDataObject`: Complete patient data for a time window

#### Layer 1 Models (Agent Outputs)
- `VitalTrend`: Trend analysis for a vital sign
- `TrendReport`: Output from Trend Agent
- `ConflictPattern`: Cross-signal conflict pattern
- `ConflictReport`: Output from Conflict Agent
- `TimeBombItem`: Time bomb risk item
- `TimeBombReport`: Output from Time Bomb Agent

#### Layer 2 Models (Coordinator Output)
- `SBARBrief`: Final SBAR+ brief for clinicians

#### Enums
- `RiskLevel`: GREEN, YELLOW, RED
- `VitalType`: Heart Rate, Respiratory Rate, etc.
- `LabType`: Creatinine, Lactate, etc.
- `TrendDirection`: RISING, FALLING, STABLE, VOLATILE
- `ConflictType`: COMPENSATED_SHOCK, EARLY_AKI, etc.
- `TimeBombType`: PENDING_LAB, MEDICATION_DUE, etc.

## Data Flow

```
MIMIC-IV CSV
    ↓
DataEmitter (emitter.py)
    ↓ (async stream)
Raw Data Dict
    ↓
DataLoader (loader.py)
    ↓
PatientDataObject
    ↓
Layer 1 Agents (trend, conflict, timebomb)
```

## MIMIC-IV Item ID Mappings

### Vitals
- `220045`: Heart Rate
- `220210`: Respiratory Rate
- `220179`: Systolic BP (Non-Invasive)
- `220180`: Diastolic BP (Non-Invasive)
- `220277`: SpO2 (Pulse Oximetry)
- `223761/223762`: Temperature

### Labs
- `50912`: Creatinine
- `50813`: Lactate
- `51301`: White Blood Cells
- `51222`: Hemoglobin
- `51265`: Platelets
- `50971`: Potassium
- `50983`: Sodium

### Outputs
- `40055`: Urine Out Foley
- `40069`: Urine Out Void
- `226559`: Foley
- `226560`: Void

## PatientDataObject Structure

```python
@dataclass
class PatientDataObject:
    # Identifiers
    patient_id: str
    stay_id: str
    window_start: datetime
    window_end: datetime
    
    # Demographics
    gender: str
    age: int
    careunit: str
    
    # Time series data
    vitals: List[VitalReading]
    labs: List[LabReading]
    urine_output: List[OutputReading]
    medications: List[MedRecord]
    pending_labs: List[PendingLab]
    
    # Metadata
    data_quality: DataQuality
    intime: datetime
    outtime: datetime
```

## Data Quality Metrics

The `DataQuality` class tracks:
- **Total Expected Readings**: Based on window size and expected frequency
- **Actual Readings**: Number of readings received
- **Missing Vitals**: List of vital types with no data
- **Missing Labs**: List of lab types with no data
- **Data Gaps**: Time gaps larger than 1 hour (in minutes)
- **Completeness Score**: 0-1 score (actual/expected)

## Testing

Run the test suite:
```bash
cd BE
python test_layer0.py
```

Tests include:
1. Basic emitter functionality
2. Basic loader functionality
3. Emitter snapshot
4. PatientDataObject creation
5. Data resampling
6. Streaming data emission
7. Batch processing

## Usage Examples

### Example 1: Single Patient Analysis
```python
import asyncio
from emitter import DataEmitter
from loader import create_pdo_from_emitter_data

async def analyze_patient(patient_id: str):
    emitter = DataEmitter()
    
    # Get 6-hour snapshot
    snapshot = emitter.get_snapshot(patient_id, window_hours=6)
    
    # Create PatientDataObject
    pdo = create_pdo_from_emitter_data(snapshot)
    
    print(f"Patient {pdo.patient_id}")
    print(f"Vitals: {len(pdo.vitals)}")
    print(f"Data Quality: {pdo.data_quality.completeness_score:.1%}")
    
    return pdo

asyncio.run(analyze_patient("10000032"))
```

### Example 2: Real-Time Streaming
```python
import asyncio
from emitter import DataEmitter
from loader import create_pdo_from_emitter_data

async def stream_patient_data(patient_id: str):
    emitter = DataEmitter(speed_multiplier=10.0)  # 10x speed
    
    async for window in emitter.emit_patient(patient_id, window_hours=6):
        # Create PDO for this window
        pdo = create_pdo_from_emitter_data(window)
        
        # Process with agents (Layer 1)
        # trend_report = await trend_agent(pdo)
        # conflict_report = await conflict_agent(pdo)
        # timebomb_report = await timebomb_agent(pdo)
        
        print(f"Window: {pdo.window_start} - {pdo.window_end}")
        print(f"Vitals: {len(pdo.vitals)}")

asyncio.run(stream_patient_data("10000032"))
```

### Example 3: Batch Processing
```python
import asyncio
from emitter import DataEmitter
from loader import process_emitter_batch

async def process_all_patients():
    emitter = DataEmitter(speed_multiplier=100.0)
    
    async for batch in emitter.emit_all_patients(window_minutes=30):
        # Process batch into PDOs
        pdos = process_emitter_batch(batch)
        
        print(f"Batch: {batch['window_start']}")
        print(f"Patients: {len(pdos)}")
        
        # Process each patient with agents
        for pdo in pdos:
            # Run agents in parallel
            pass

asyncio.run(process_all_patients())
```

## Configuration

### Emitter Configuration
- `data_path`: Path to master CSV (default: "BE/data/raw_data/master_multi_patient_timeline.csv")
- `speed_multiplier`: Speed up/slow down time (1.0 = real-time, 10.0 = 10x speed)
- `loop_data`: Whether to loop data when reaching end

### Loader Configuration
- `data_path`: Path to master CSV
- `interval_minutes`: Resampling interval (default: 30)
- `window_hours`: Rolling window size (default: 6)

## Next Steps

With Layer 0 complete, you can now:

1. **Implement Layer 1 Agents:**
   - `trend_agent.py` - Vital sign trend analysis
   - `conflict_agent.py` - Cross-signal pattern detection
   - `timebomb_agent.py` - Forward-looking risk identification

2. **Implement Layer 2 Coordinator:**
   - `coordinator.py` - Aggregate agent reports and generate SBAR

3. **Build API Layer:**
   - `api_main.py` - FastAPI endpoints for frontend

## Dependencies

Install required packages:
```bash
pip install -r requirements.txt
```

Key dependencies:
- `pandas>=2.0.0` - Data processing
- `numpy>=1.24.0` - Numerical operations
- `python-dateutil>=2.8.0` - Date/time utilities

## File Structure

```
BE/
├── emitter.py              # Data emitter/simulator
├── loader.py               # Data loader & transformer
├── schemas.py              # All data models
├── test_layer0.py          # Integration tests
├── requirements.txt        # Python dependencies
├── LAYER0_README.md        # This file
└── data/
    └── raw_data/
        ├── master_multi_patient_timeline.csv
        └── helper.md
```

## Notes

- Type errors in IDE are expected until pandas is installed
- The emitter respects original MIMIC-IV timestamps
- Data quality is automatically calculated for each window
- All datetime objects are timezone-aware (UTC)
- The system supports both batch and streaming modes

## Support

For questions or issues with Layer 0 implementation, refer to:
- `BACKEND_PLAN.md` - Overall backend architecture
- `IMPLEMENTATION_GUIDE.md` - Detailed implementation guide
- `helper.md` - Field mappings and agent logic