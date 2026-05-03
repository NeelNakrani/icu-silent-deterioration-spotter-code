"""
Module: config.py
Purpose: Configuration and environment variables
Layer: Support

Part of ICU Silent Deterioration Spotter
Hackathon: IBM Bob Challenge 2026

This module manages all configuration settings and environment variables.
"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """
    Configuration class for the ICU Silent Deterioration Spotter.
    
    All configuration values can be overridden via environment variables.
    """
    
    # ========================================================================
    # Application Settings
    # ========================================================================
    
    APP_NAME: str = "ICU Silent Deterioration Spotter"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "AI-powered system for detecting silent deterioration in ICU patients"
    
    # ========================================================================
    # API Settings
    # ========================================================================
    
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    API_RELOAD: bool = os.getenv("API_RELOAD", "true").lower() == "true"
    
    # CORS settings
    CORS_ORIGINS: list = os.getenv("CORS_ORIGINS", "*").split(",")
    
    # ========================================================================
    # Data Settings
    # ========================================================================
    
    # Path to MIMIC-IV data
    BASE_DIR: Path = Path(__file__).parent
    DATA_DIR: Path = BASE_DIR / "data"
    RAW_DATA_DIR: Path = DATA_DIR / "raw_data"
    
    MIMIC_DATA_PATH: str = os.getenv(
        "MIMIC_DATA_PATH",
        str(RAW_DATA_DIR / "master_multi_patient_timeline.csv")
    )
    
    # Data window settings
    WINDOW_HOURS: int = int(os.getenv("WINDOW_HOURS", "6"))
    RESAMPLE_INTERVAL_MINUTES: int = int(os.getenv("RESAMPLE_INTERVAL_MINUTES", "30"))
    
    # ========================================================================
    # Pipeline Settings
    # ========================================================================
    
    # Scheduler settings
    SCHEDULER_ENABLED: bool = os.getenv("SCHEDULER_ENABLED", "false").lower() == "true"
    SCHEDULER_INTERVAL_SECONDS: int = int(os.getenv("SCHEDULER_INTERVAL_SECONDS", "300"))  # 5 minutes
    
    # Agent timeout settings (seconds)
    AGENT_TIMEOUT: int = int(os.getenv("AGENT_TIMEOUT", "30"))
    COORDINATOR_TIMEOUT: int = int(os.getenv("COORDINATOR_TIMEOUT", "60"))
    
    # ========================================================================
    # LLM Settings - IBM watsonx.ai
    # ========================================================================
    
    # IBM watsonx.ai
    WATSONX_API_KEY: Optional[str] = os.getenv("WATSONX_API_KEY", "")
    WATSONX_PROJECT_ID: Optional[str] = os.getenv("WATSONX_PROJECT_ID", "")
    WATSONX_URL: str = os.getenv("WATSONX_URL", "")
    WATSONX_MODEL: str = os.getenv("WATSONX_MODEL", "ibm/granite-13b-chat-v2")
    
    # LLM feature flags
    USE_LLM_FOR_TRENDS: bool = os.getenv("USE_LLM_FOR_TRENDS", "false").lower() == "true"
    USE_LLM_FOR_CONFLICTS: bool = os.getenv("USE_LLM_FOR_CONFLICTS", "false").lower() == "true"
    USE_LLM_FOR_SBAR: bool = os.getenv("USE_LLM_FOR_SBAR", "false").lower() == "true"
    USE_LLM_FOR_CRITICAL_PATIENTS: bool = os.getenv("USE_LLM_FOR_CRITICAL_PATIENTS", "true").lower() == "true"
    
    # ========================================================================
    # Database Settings
    # ========================================================================
    
    # Database type: sqlite or postgresql
    DB_TYPE: str = os.getenv("DB_TYPE", "sqlite")
    
    # SQLite settings
    SQLITE_DB_PATH: str = os.getenv("SQLITE_DB_PATH", str(DATA_DIR / "sbar_briefs.db"))
    
    # PostgreSQL settings (optional)
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT: int = int(os.getenv("POSTGRES_PORT", "5432"))
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "icu_spotter")
    
    # Database URL (constructed)
    @property
    def DATABASE_URL(self) -> str:
        """Get database URL based on DB_TYPE."""
        if self.DB_TYPE == "postgresql":
            return (
                f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
                f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
            )
        else:
            return f"sqlite:///{self.SQLITE_DB_PATH}"
    
    # ========================================================================
    # Risk Scoring Settings
    # ========================================================================
    
    # Risk level thresholds
    RISK_GREEN_MAX: float = float(os.getenv("RISK_GREEN_MAX", "40.0"))
    RISK_YELLOW_MAX: float = float(os.getenv("RISK_YELLOW_MAX", "70.0"))
    # Anything above RISK_YELLOW_MAX is RED
    
    # Agent weight settings (for risk calculation)
    TREND_WEIGHT: float = float(os.getenv("TREND_WEIGHT", "10.0"))  # 0-30 points
    CONFLICT_WEIGHT: float = float(os.getenv("CONFLICT_WEIGHT", "13.33"))  # 0-40 points
    TIMEBOMB_WEIGHT: float = float(os.getenv("TIMEBOMB_WEIGHT", "10.0"))  # 0-30 points
    
    # ========================================================================
    # Logging Settings
    # ========================================================================
    
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # ========================================================================
    # Development/Testing Settings
    # ========================================================================
    
    DEBUG_MODE: bool = os.getenv("DEBUG_MODE", "false").lower() == "true"
    TESTING_MODE: bool = os.getenv("TESTING_MODE", "false").lower() == "true"
    
    # Emitter speed multiplier for testing
    EMITTER_SPEED_MULTIPLIER: float = float(os.getenv("EMITTER_SPEED_MULTIPLIER", "1.0"))
    
    # ========================================================================
    # Helper Methods
    # ========================================================================
    
    @classmethod
    def validate(cls) -> bool:
        """
        Validate configuration settings.
        
        Returns:
            True if configuration is valid, False otherwise
        """
        errors = []
        
        # Check if data file exists
        if not Path(cls.MIMIC_DATA_PATH).exists():
            errors.append(f"MIMIC data file not found: {cls.MIMIC_DATA_PATH}")
        
        # Check LLM settings if enabled
        if cls.USE_LLM_FOR_TRENDS or cls.USE_LLM_FOR_CONFLICTS or cls.USE_LLM_FOR_SBAR or cls.USE_LLM_FOR_CRITICAL_PATIENTS:
            if not cls.WATSONX_API_KEY or not cls.WATSONX_PROJECT_ID:
                errors.append(
                    "LLM features enabled but IBM watsonx.ai credentials not provided. "
                    "Set WATSONX_API_KEY and WATSONX_PROJECT_ID"
                )
        
        # Check database settings
        if cls.DB_TYPE not in ["sqlite", "postgresql"]:
            errors.append(f"Invalid DB_TYPE: {cls.DB_TYPE}. Must be 'sqlite' or 'postgresql'")
        
        if errors:
            for error in errors:
                print(f"Configuration Error: {error}")
            return False
        
        return True
    
    @classmethod
    def print_config(cls) -> None:
        """Print current configuration (for debugging)."""
        print("=" * 80)
        print("CONFIGURATION")
        print("=" * 80)
        print(f"App Name: {cls.APP_NAME}")
        print(f"Version: {cls.APP_VERSION}")
        print(f"API: {cls.API_HOST}:{cls.API_PORT}")
        print(f"Data Path: {cls.MIMIC_DATA_PATH}")
        print(f"Window Hours: {cls.WINDOW_HOURS}")
        print(f"Database: {cls.DB_TYPE}")
        print(f"Scheduler: {'Enabled' if cls.SCHEDULER_ENABLED else 'Disabled'}")
        print(f"IBM watsonx.ai: {'Configured' if cls.WATSONX_API_KEY else 'Not configured'}")
        print(f"LLM Features: Trends={cls.USE_LLM_FOR_TRENDS}, "
              f"Conflicts={cls.USE_LLM_FOR_CONFLICTS}, SBAR={cls.USE_LLM_FOR_SBAR}, "
              f"Critical={cls.USE_LLM_FOR_CRITICAL_PATIENTS}")
        print(f"Debug Mode: {cls.DEBUG_MODE}")
        print("=" * 80)


# Create global config instance
config = Config()


# ============================================================================
# Environment File Template
# ============================================================================

ENV_TEMPLATE = """
# ICU Silent Deterioration Spotter - Environment Configuration
# Copy this file to .env and update with your settings

# API Settings
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=true
CORS_ORIGINS=*

# Data Settings
MIMIC_DATA_PATH=./data/raw_data/master_multi_patient_timeline.csv
WINDOW_HOURS=6
RESAMPLE_INTERVAL_MINUTES=30

# Pipeline Settings
SCHEDULER_ENABLED=false
SCHEDULER_INTERVAL_SECONDS=300
AGENT_TIMEOUT=30
COORDINATOR_TIMEOUT=60

# LLM Settings - IBM watsonx.ai
WATSONX_API_KEY=your_api_key_here
WATSONX_PROJECT_ID=your_project_id_here
WATSONX_URL=https://us-south.ml.cloud.ibm.com
WATSONX_MODEL=ibm/granite-13b-chat-v2

# LLM Feature Flags
USE_LLM_FOR_TRENDS=false
USE_LLM_FOR_CONFLICTS=false
USE_LLM_FOR_SBAR=false
USE_LLM_FOR_CRITICAL_PATIENTS=true

# Database Settings
DB_TYPE=sqlite
SQLITE_DB_PATH=./data/sbar_briefs.db

# PostgreSQL (if using)
# POSTGRES_HOST=localhost
# POSTGRES_PORT=5432
# POSTGRES_USER=postgres
# POSTGRES_PASSWORD=your_password
# POSTGRES_DB=icu_spotter

# Risk Scoring
RISK_GREEN_MAX=40.0
RISK_YELLOW_MAX=70.0
TREND_WEIGHT=10.0
CONFLICT_WEIGHT=13.33
TIMEBOMB_WEIGHT=10.0

# Logging
LOG_LEVEL=INFO

# Development
DEBUG_MODE=false
TESTING_MODE=false
EMITTER_SPEED_MULTIPLIER=1.0
"""


def create_env_template(output_path: str = ".env.template") -> None:
    """
    Create a template .env file.
    
    Args:
        output_path: Path to write the template file
    """
    with open(output_path, "w") as f:
        f.write(ENV_TEMPLATE.strip())
    print(f"Created environment template: {output_path}")


if __name__ == "__main__":
    # Validate and print configuration
    print("\nValidating configuration...")
    if config.validate():
        print("✓ Configuration is valid\n")
        config.print_config()
    else:
        print("✗ Configuration validation failed\n")
    
    # Optionally create .env template
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--create-template":
        create_env_template()

# Made with Bob
