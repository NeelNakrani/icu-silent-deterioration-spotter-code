# Backend Setup Instructions

This guide will help you set up the Python environment for the backend.

## Prerequisites

- Python 3.11 or higher
- pip (comes with Python)

## Quick Setup

### Windows

1. Open PowerShell in the `BE` directory
2. Run the setup script:
   ```powershell
   .\setup.ps1
   ```

**Note:** If you get an execution policy error, run this first:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Linux/macOS

1. Open a terminal in the `BE` directory
2. Make the script executable (first time only):
   ```bash
   chmod +x setup.sh
   ```
3. Run the setup script:
   ```bash
   ./setup.sh
   ```

## What the Setup Script Does

1. Checks if Python 3.11+ is installed
2. Creates a virtual environment named `venv` in the BE directory
3. Activates the virtual environment
4. Upgrades pip to the latest version
5. Installs all dependencies from `requirements.txt`

## Manual Setup (Alternative)

If you prefer to set up manually or the script doesn't work:

### Windows
```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Upgrade pip
python -m pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

### Linux/macOS
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
python -m pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

## Daily Usage

### Activating the Environment

**Windows:**
```powershell
.\venv\Scripts\Activate.ps1
```

**Linux/macOS:**
```bash
source venv/bin/activate
```

### Deactivating the Environment

When you're done working:
```bash
deactivate
```

## Verifying Installation

After setup, verify everything is installed correctly:

```bash
# Check Python version
python --version

# List installed packages
pip list

# Run tests (if available)
pytest
```

## Troubleshooting

### Python Version Issues
- Ensure Python 3.11+ is installed: `python --version` or `python3 --version`
- On some systems, you may need to use `python3` instead of `python`

### Permission Issues (Linux/macOS)
- Make sure the setup script is executable: `chmod +x setup.sh`
- You may need to use `sudo` for system-wide installations (not recommended for venv)

### Windows Execution Policy
If you get an error about execution policies:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Package Installation Failures
- Ensure you have an active internet connection
- Try upgrading pip: `python -m pip install --upgrade pip`
- Some packages may require additional system dependencies (especially on Linux)

### Virtual Environment Not Activating
- Make sure you're in the `BE` directory
- Check that the `venv` folder was created successfully
- Try recreating the environment by deleting `venv` and running setup again

## Environment Variables

Create a `.env` file in the `BE` directory for configuration:

```env
# API Keys
ANTHROPIC_API_KEY=your_key_here
IBM_WATSONX_API_KEY=your_key_here

# Database
DATABASE_URL=sqlite:///./data/icu_monitor.db

# Server
HOST=0.0.0.0
PORT=8000
```

## Next Steps

After successful setup:

1. Review the `LAYER0_README.md` for Layer 0 implementation details
2. Check `BACKEND_PLAN.md` for the overall architecture
3. Run tests: `pytest` (if tests are available)
4. Start the development server (when ready)

## Getting Help

If you encounter issues:
1. Check this troubleshooting section
2. Review the error messages carefully
3. Ensure all prerequisites are met
4. Contact the team lead for assistance