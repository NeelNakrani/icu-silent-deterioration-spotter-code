"""
Module: db.py
Purpose: Database operations for persisting SBAR briefs
Layer: Support

Part of ICU Silent Deterioration Spotter
Hackathon: IBM Bob Challenge 2026

This module handles database operations for storing and retrieving SBAR briefs.
Supports both SQLite (for MVP/development) and PostgreSQL (for production).
"""

import json
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from pathlib import Path

from sqlalchemy import (
    create_engine,
    Column,
    String,
    Float,
    DateTime,
    Text,
    Integer
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError

from schemas import SBARBrief, RiskLevel, PatientListItem
from config import config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# SQLAlchemy base
Base = declarative_base()


# ============================================================================
# Database Models
# ============================================================================

class SBARBriefModel(Base):
    """
    SQLAlchemy model for SBAR briefs.
    """
    __tablename__ = "sbar_briefs"
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Patient identifiers
    patient_id = Column(String(50), nullable=False, index=True)
    stay_id = Column(String(50), nullable=False)
    
    # Timestamps
    timestamp = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)
    
    # Risk assessment
    risk_level = Column(String(20), nullable=False, index=True)
    risk_score = Column(Float, nullable=False)
    
    # SBAR components
    situation = Column(Text, nullable=False)
    background = Column(Text, nullable=False)
    assessment = Column(Text, nullable=False)
    recommendation = Column(Text, nullable=False)
    
    # Metadata
    data_quality_score = Column(Float, nullable=False, default=0.0)
    confidence_level = Column(Float, nullable=False, default=0.0)
    generated_by = Column(String(100), nullable=False)
    
    # Agent reports (stored as JSON)
    trend_report_json = Column(Text, nullable=True)
    conflict_report_json = Column(Text, nullable=True)
    timebomb_report_json = Column(Text, nullable=True)
    
    def __repr__(self):
        return (
            f"<SBARBrief(patient_id='{self.patient_id}', "
            f"risk_level='{self.risk_level}', "
            f"timestamp='{self.timestamp}')>"
        )


# ============================================================================
# Database Manager
# ============================================================================

class DatabaseManager:
    """
    Manages database connections and operations.
    """
    
    def __init__(self, database_url: Optional[str] = None):
        """
        Initialize database manager.
        
        Args:
            database_url: Database connection URL (defaults to config.DATABASE_URL)
        """
        self.database_url = database_url or config.DATABASE_URL
        self.engine = None
        self.SessionLocal = None
        
    def init_db(self) -> None:
        """
        Initialize database connection and create tables.
        """
        logger.info(f"Initializing database: {self.database_url}")
        
        # Create engine
        self.engine = create_engine(
            self.database_url,
            echo=config.DEBUG_MODE,
            connect_args={"check_same_thread": False} if "sqlite" in self.database_url else {}
        )
        
        # Create session factory
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )
        
        # Create tables
        Base.metadata.create_all(bind=self.engine)
        
        logger.info("Database initialized successfully")
    
    def get_session(self) -> Session:
        """
        Get a database session.
        
        Returns:
            SQLAlchemy Session object
        """
        if not self.SessionLocal:
            self.init_db()
        return self.SessionLocal()
    
    def close(self) -> None:
        """Close database connection."""
        if self.engine:
            self.engine.dispose()
            logger.info("Database connection closed")


# Global database manager instance
db_manager = DatabaseManager()


# ============================================================================
# CRUD Operations
# ============================================================================

def upsert_brief(brief: SBARBrief) -> bool:
    """
    Insert or update an SBAR brief in the database.
    
    Args:
        brief: SBARBrief object to save
        
    Returns:
        True if successful, False otherwise
    """
    session = db_manager.get_session()
    
    try:
        # Check if brief already exists for this patient
        existing = session.query(SBARBriefModel).filter_by(
            patient_id=brief.patient_id
        ).order_by(SBARBriefModel.timestamp.desc()).first()
        
        # Convert agent reports to JSON
        trend_json = json.dumps(brief.trend_report.to_dict()) if brief.trend_report else None
        conflict_json = json.dumps(brief.conflict_report.to_dict()) if brief.conflict_report else None
        timebomb_json = json.dumps(brief.timebomb_report.to_dict()) if brief.timebomb_report else None
        
        if existing:
            # Update existing record
            existing.stay_id = brief.stay_id
            existing.timestamp = brief.timestamp
            existing.risk_level = brief.risk_level.value
            existing.risk_score = brief.risk_score
            existing.situation = brief.situation
            existing.background = brief.background
            existing.assessment = brief.assessment
            existing.recommendation = brief.recommendation
            existing.data_quality_score = brief.data_quality_score
            existing.confidence_level = brief.confidence_level
            existing.generated_by = brief.generated_by
            existing.trend_report_json = trend_json
            existing.conflict_report_json = conflict_json
            existing.timebomb_report_json = timebomb_json
            existing.updated_at = datetime.now()
            
            logger.info(f"Updated brief for patient {brief.patient_id}")
        else:
            # Insert new record
            new_brief = SBARBriefModel(
                patient_id=brief.patient_id,
                stay_id=brief.stay_id,
                timestamp=brief.timestamp,
                risk_level=brief.risk_level.value,
                risk_score=brief.risk_score,
                situation=brief.situation,
                background=brief.background,
                assessment=brief.assessment,
                recommendation=brief.recommendation,
                data_quality_score=brief.data_quality_score,
                confidence_level=brief.confidence_level,
                generated_by=brief.generated_by,
                trend_report_json=trend_json,
                conflict_report_json=conflict_json,
                timebomb_report_json=timebomb_json
            )
            session.add(new_brief)
            
            logger.info(f"Inserted new brief for patient {brief.patient_id}")
        
        session.commit()
        return True
        
    except SQLAlchemyError as e:
        logger.error(f"Database error upserting brief: {e}", exc_info=True)
        session.rollback()
        return False
    finally:
        session.close()


def get_brief(patient_id: str) -> Optional[Dict[str, Any]]:
    """
    Get the latest SBAR brief for a patient.
    
    Args:
        patient_id: Patient subject ID
        
    Returns:
        Dictionary with brief data or None if not found
    """
    session = db_manager.get_session()
    
    try:
        brief_model = session.query(SBARBriefModel).filter_by(
            patient_id=patient_id
        ).order_by(SBARBriefModel.timestamp.desc()).first()
        
        if not brief_model:
            return None
        
        # Convert to dictionary
        brief_dict = {
            "patient_id": brief_model.patient_id,
            "stay_id": brief_model.stay_id,
            "timestamp": brief_model.timestamp.isoformat(),
            "risk_level": brief_model.risk_level,
            "risk_score": brief_model.risk_score,
            "situation": brief_model.situation,
            "background": brief_model.background,
            "assessment": brief_model.assessment,
            "recommendation": brief_model.recommendation,
            "data_quality_score": brief_model.data_quality_score,
            "confidence_level": brief_model.confidence_level,
            "generated_by": brief_model.generated_by,
            "created_at": brief_model.created_at.isoformat(),
            "updated_at": brief_model.updated_at.isoformat()
        }
        
        # Parse JSON reports if available
        if brief_model.trend_report_json:
            brief_dict["trend_report"] = json.loads(brief_model.trend_report_json)
        if brief_model.conflict_report_json:
            brief_dict["conflict_report"] = json.loads(brief_model.conflict_report_json)
        if brief_model.timebomb_report_json:
            brief_dict["timebomb_report"] = json.loads(brief_model.timebomb_report_json)
        
        return brief_dict
        
    except SQLAlchemyError as e:
        logger.error(f"Database error getting brief: {e}", exc_info=True)
        return None
    finally:
        session.close()


def get_all_patients() -> List[Dict[str, Any]]:
    """
    Get list of all patients with their latest brief information.
    
    Returns:
        List of dictionaries with patient information
    """
    session = db_manager.get_session()
    
    try:
        # Get latest brief for each patient
        # This is a simplified query; in production, use a proper subquery
        briefs = session.query(SBARBriefModel).order_by(
            SBARBriefModel.patient_id,
            SBARBriefModel.timestamp.desc()
        ).all()
        
        # Group by patient and take latest
        patient_map = {}
        for brief in briefs:
            if brief.patient_id not in patient_map:
                patient_map[brief.patient_id] = {
                    "patient_id": brief.patient_id,
                    "stay_id": brief.stay_id,
                    "risk_level": brief.risk_level,
                    "risk_score": brief.risk_score,
                    "last_updated": brief.timestamp.isoformat(),
                    "confidence_level": brief.confidence_level
                }
        
        return list(patient_map.values())
        
    except SQLAlchemyError as e:
        logger.error(f"Database error getting all patients: {e}", exc_info=True)
        return []
    finally:
        session.close()


def get_patient_history(patient_id: str, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Get historical briefs for a patient.
    
    Args:
        patient_id: Patient subject ID
        limit: Maximum number of records to return
        
    Returns:
        List of brief dictionaries, ordered by timestamp (newest first)
    """
    session = db_manager.get_session()
    
    try:
        briefs = session.query(SBARBriefModel).filter_by(
            patient_id=patient_id
        ).order_by(SBARBriefModel.timestamp.desc()).limit(limit).all()
        
        history = []
        for brief in briefs:
            history.append({
                "timestamp": brief.timestamp.isoformat(),
                "risk_level": brief.risk_level,
                "risk_score": brief.risk_score,
                "situation": brief.situation[:100] + "..." if len(brief.situation) > 100 else brief.situation
            })
        
        return history
        
    except SQLAlchemyError as e:
        logger.error(f"Database error getting patient history: {e}", exc_info=True)
        return []
    finally:
        session.close()


def delete_brief(patient_id: str) -> bool:
    """
    Delete all briefs for a patient.
    
    Args:
        patient_id: Patient subject ID
        
    Returns:
        True if successful, False otherwise
    """
    session = db_manager.get_session()
    
    try:
        deleted_count = session.query(SBARBriefModel).filter_by(
            patient_id=patient_id
        ).delete()
        
        session.commit()
        logger.info(f"Deleted {deleted_count} brief(s) for patient {patient_id}")
        return True
        
    except SQLAlchemyError as e:
        logger.error(f"Database error deleting brief: {e}", exc_info=True)
        session.rollback()
        return False
    finally:
        session.close()


def get_high_risk_patients(threshold: float = 70.0) -> List[Dict[str, Any]]:
    """
    Get all patients with risk score above threshold.
    
    Args:
        threshold: Risk score threshold (default: 70.0 for RED level)
        
    Returns:
        List of high-risk patient dictionaries
    """
    session = db_manager.get_session()
    
    try:
        briefs = session.query(SBARBriefModel).filter(
            SBARBriefModel.risk_score >= threshold
        ).order_by(SBARBriefModel.risk_score.desc()).all()
        
        high_risk = []
        for brief in briefs:
            high_risk.append({
                "patient_id": brief.patient_id,
                "stay_id": brief.stay_id,
                "risk_level": brief.risk_level,
                "risk_score": brief.risk_score,
                "timestamp": brief.timestamp.isoformat(),
                "situation": brief.situation
            })
        
        return high_risk
        
    except SQLAlchemyError as e:
        logger.error(f"Database error getting high-risk patients: {e}", exc_info=True)
        return []
    finally:
        session.close()


# ============================================================================
# Initialization
# ============================================================================

def init_database() -> None:
    """
    Initialize the database (create tables if they don't exist).
    """
    db_manager.init_db()


if __name__ == "__main__":
    # Initialize database and run some tests
    logger.info("Initializing database...")
    init_database()
    logger.info("Database initialized successfully")
    
    # Print database info
    print(f"\nDatabase URL: {config.DATABASE_URL}")
    print(f"Database Type: {config.DB_TYPE}")
    
    if config.DB_TYPE == "sqlite":
        db_path = Path(config.SQLITE_DB_PATH)
        if db_path.exists():
            print(f"Database file exists: {db_path}")
            print(f"File size: {db_path.stat().st_size} bytes")
        else:
            print(f"Database file will be created at: {db_path}")

# Made with Bob