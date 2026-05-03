# Backend Structure

This directory contains the backend implementation for the ICU Silent Deterioration Spotter.

## Directory Structure

```
BE/
├── src/                    # Source code
│   ├── __init__.py
│   ├── api_main.py        # FastAPI REST API endpoints
│   ├── coordinator.py     # Layer 2 coordinator
│   ├── schemas.py         # Data models and schemas
│   ├── db.py             # Database operations
│   ├── emitter.py        # Data emitter/simulator
│   ├── loader.py         # Data loader
│   ├── trend_agent.py    # Trend analysis agent
│   ├── conflict_agent.py # Conflict detection agent
│   ├── timebomb_agent.py # Time bomb observer agent
│   └── data/                  # Data directory (created at runtime)
│       └── raw_data/          # Raw MIMIC-IV data
│
├── tests/                 # Test files
│   ├── __init__.py
│   ├── test_layer0.py    # Layer 0 tests
│   ├── test_layer1.py    # Layer 1 tests
│   └── test_layer2.py    # Layer 2 tests
│
├── scripts/               # Setup and utility scripts
│   ├── setup.ps1         # Windows setup script
│   ├── setup.sh          # Linux/macOS setup script
│   └── run_experiment.py # Experimental runner
│
├── config/                # Configuration files
│   ├── __init__.py
│   └── config.py         # Application configuration
│
├── docs/                  # Documentation
│   ├── BACKEND_PLAN.md
│   ├── BE-Guidelines.md
│   ├── IMPLEMENTATION_GUIDE.md
│   ├── LAYER0_README.md
│   ├── LAYER1_README.md
│   ├── LAYER2_README.md
│   ├── README.md
│   └── SETUP_INSTRUCTIONS.md
│
│
├── venv/                  # Virtual environment (created by setup)
│
├── requirements.txt       # Python dependencies
└── LAYER2_IMPLEMENTATION.md  # Layer 2 implementation notes
```

## Quick Start

### 1. Setup Environment

**Windows:**
```powershell
.\scripts\setup.ps1
```

**Linux/macOS:**
```bash
bash scripts/setup.sh
```

### 2. Activate Virtual Environment

**Windows:**
```powershell
.\venv\Scripts\Activate.ps1
```

**Linux/macOS:**
```bash
source venv/bin/activate
```

### 3. Run Tests

```bash
# Test Layer 0 (Data Ingestion)
python -m pytest tests/test_layer0.py -v

# Test Layer 1 (Agents)
python -m pytest tests/test_layer1.py -v

# Test Layer 2 (Coordinator + API)
python -m pytest tests/test_layer2.py -v
```

### 4. Start API Server

```bash
cd src
python api_main.py
```

The API will be available at:
- API: http://localhost:8000
- Documentation: http://localhost:8000/docs

## Running Experiments

```bash
# Test Layer 0
python scripts/run_experiment.py --layer 0

# Test Layer 1
python scripts/run_experiment.py --layer 1
```

## Architecture

### Layer 0: Data Ingestion
- **emitter.py**: Simulates real-time data streaming
- **loader.py**: Loads and processes MIMIC-IV data
- **schemas.py**: Data models and structures

### Layer 1: Agents
- **trend_agent.py**: Analyzes vital sign trends
- **conflict_agent.py**: Detects cross-signal conflicts
- **timebomb_agent.py**: Identifies time-sensitive risks

### Layer 2: Coordinator & API
- **coordinator.py**: Orchestrates agents and generates SBAR briefs
- **api_main.py**: REST API endpoints
- **db.py**: Database persistence

## Configuration

Configuration is managed through:
- `config/config.py`: Application settings
- `.env` file: Environment-specific variables (create from `.env.template`)

## Documentation

Detailed documentation is available in the `docs/` directory:
- [Setup Instructions](docs/SETUP_INSTRUCTIONS.md)
- [Implementation Guide](docs/IMPLEMENTATION_GUIDE.md)
- [Layer 0 README](docs/LAYER0_README.md)
- [Layer 1 README](docs/LAYER1_README.md)
- [Layer 2 README](docs/LAYER2_README.md)

## Made with Bob 🤖