"""
Module: api_main.py
Purpose: Layer 2 - FastAPI REST API endpoints
Layer: 2 (API)

Part of ICU Silent Deterioration Spotter
Hackathon: IBM Bob Challenge 2026

This module provides REST API endpoints for the frontend to consume.
"""

import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from schemas import (
    PatientDataObject,
    SBARBrief,
    PatientListItem,
    HealthCheckResponse,
    RiskLevel
)
from coordinator import coordinate, format_sbar_for_display
from loader import DataLoader, create_pdo_from_emitter_data
from emitter import DataEmitter

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="ICU Silent Deterioration Spotter API",
    description="REST API for detecting silent deterioration in ICU patients",
    version="1.0.0"
)

# Configure CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state (in production, use proper database)
# This stores the latest SBAR briefs for each patient
patient_briefs: Dict[str, SBARBrief] = {}
# Store PDOs to access data_quality and other metadata
patient_data_objects: Dict[str, PatientDataObject] = {}

# Initialize data emitter and loader
emitter = DataEmitter(speed_multiplier=1.0)
loader = DataLoader()


# ============================================================================
# Pydantic Models for API Requests/Responses
# ============================================================================

class PatientBriefResponse(BaseModel):
    """Response model for patient brief endpoint."""
    patient_id: str
    stay_id: str
    timestamp: str
    risk_level: str
    risk_emoji: str
    risk_score: float
    situation: str
    background: str
    assessment: str
    recommendation: str
    data_quality_score: float
    confidence_level: float
    generated_by: str
    
    # Patient demographics
    age: Optional[int] = None
    gender: Optional[str] = None
    careunit: Optional[str] = None
    
    # Full detailed reports (not just summaries)
    trend_report: Optional[Dict[str, Any]] = None
    conflict_report: Optional[Dict[str, Any]] = None
    timebomb_report: Optional[Dict[str, Any]] = None
    
    # Timeline of recent events
    timeline: Optional[List[Dict[str, str]]] = None
    
    # Data quality metrics
    data_quality: Optional[Dict[str, Any]] = None


class PatientListResponse(BaseModel):
    """Response model for patient list endpoint."""
    patients: List[Dict[str, Any]]
    total_count: int
    timestamp: str


class RefreshResponse(BaseModel):
    """Response model for refresh endpoint."""
    success: bool
    message: str
    patient_id: str
    risk_level: str
    risk_score: float


def calculate_risk_from_data(patient_id: str) -> tuple[RiskLevel, float]:
    """
    Calculate risk level from raw patient data when no brief is available.
    
    Args:
        patient_id: Patient subject ID
        
    Returns:
        Tuple of (RiskLevel, risk_score)
    """
    try:
        # Get patient data from emitter
        if emitter.df is None:
            emitter.load_data()
        
        # Type guard: emitter.df is guaranteed to be non-None after load_data()
        if emitter.df is None:
            logger.error("Failed to load data from emitter")
            return RiskLevel.GREEN, 0.0
        
        patient_df = emitter.df[emitter.df['subject_id'] == int(patient_id)]
        
        if patient_df.empty:
            return RiskLevel.GREEN, 0.0
        
        # Count warnings in the data
        warning_count = patient_df['warning'].sum()
        total_records = len(patient_df)
        
        # Calculate warning percentage
        warning_percentage = (warning_count / total_records) * 100 if total_records > 0 else 0
        
        # Determine risk level based on warning presence and frequency
        if warning_count == 0:
            # No warnings - stable
            risk_level = RiskLevel.GREEN
            risk_score = 0.0
        elif warning_percentage < 1.0:
            # Less than 1% warnings - watch closely
            risk_level = RiskLevel.YELLOW
            risk_score = 45.0 + (warning_percentage * 10)  # 45-55 range
        else:
            # 1% or more warnings - critical attention
            risk_level = RiskLevel.RED
            risk_score = 75.0 + min(warning_percentage * 5, 25.0)  # 75-100 range
        
        logger.info(
            f"Patient {patient_id}: {warning_count}/{total_records} warnings "
            f"({warning_percentage:.2f}%) → {risk_level.value} (score: {risk_score:.1f})"
        )
        
        return risk_level, risk_score
        
    except Exception as e:
        logger.error(f"Error calculating risk for patient {patient_id}: {e}")
        return RiskLevel.GREEN, 0.0


# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/health", response_model=Dict[str, Any])
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        Health status information
    """
    health_response = HealthCheckResponse(
        status="healthy",
        timestamp=datetime.now(),
        version="1.0.0"
    )
    
    return health_response.to_dict()


@app.get("/patients", response_model=PatientListResponse)
async def get_patients():
    """
    Get list of all patients with their current risk levels and latest vitals.
    
    Returns:
        List of patients with risk information and vital signs
    """
    try:
        # Get patient list from emitter
        patients = emitter.get_patient_list()
        
        # Enrich with risk information from cached briefs, calculate from data if needed, and add latest vitals
        patient_list = []
        for patient in patients:
            patient_id = patient['patient_id']
            
            # Get latest vitals snapshot for this patient
            snapshot = emitter.get_snapshot(patient_id, window_hours=1)
            latest_vitals = extract_latest_vitals(snapshot)
            
            # Get cached brief if available
            brief = patient_briefs.get(patient_id)
            flags = []
            
            if brief:
                patient_item = PatientListItem(
                    patient_id=patient_id,
                    stay_id=patient['stay_id'],
                    risk_level=brief.risk_level,
                    risk_score=brief.risk_score,
                    last_updated=brief.timestamp,
                    careunit=patient['careunit'],
                    age=patient['age'],
                    gender=patient['gender']
                )
                # Generate flags from brief
                flags = generate_flags_from_brief(brief)
            else:
                # No brief yet, calculate risk from raw data
                risk_level, risk_score = calculate_risk_from_data(patient_id)
                patient_item = PatientListItem(
                    patient_id=patient_id,
                    stay_id=patient['stay_id'],
                    risk_level=risk_level,
                    risk_score=risk_score,
                    last_updated=datetime.now(),
                    careunit=patient['careunit'],
                    age=patient['age'],
                    gender=patient['gender']
                )
            
            # Add vitals and flags to the dict
            patient_dict = patient_item.to_dict()
            patient_dict['vitals'] = latest_vitals
            patient_dict['flags'] = flags
            patient_list.append(patient_dict)
        
        # Sort by risk score (highest first)
        patient_list.sort(key=lambda p: p['risk_score'], reverse=True)
        
        return PatientListResponse(
            patients=patient_list,
            total_count=len(patient_list),
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error getting patient list: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve patient list: {str(e)}"
        )


@app.get("/patients/{patient_id}/brief", response_model=PatientBriefResponse)
async def get_patient_brief(patient_id: str):
    """
    Get full SBAR brief for a specific patient.
    
    Args:
        patient_id: Patient subject ID
        
    Returns:
        Complete SBAR brief with all details
    """
    try:
        # Check if we have a cached brief
        if patient_id not in patient_briefs:
            # Generate new brief
            logger.info(f"No cached brief for patient {patient_id}, generating new one")
            await refresh_patient_brief(patient_id)
        
        brief = patient_briefs.get(patient_id)
        
        if not brief:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Patient {patient_id} not found or no data available"
            )
        
        # Get patient demographics from emitter
        patient_list = emitter.get_patient_list()
        patient_demo = next((p for p in patient_list if p['patient_id'] == patient_id), None)
        
        # Get data_quality from stored PDO
        pdo = patient_data_objects.get(patient_id)
        data_quality_dict = pdo.data_quality.to_dict() if pdo and pdo.data_quality else None
        
        # Convert to response model with full nested reports
        response = PatientBriefResponse(
            patient_id=brief.patient_id,
            stay_id=brief.stay_id,
            timestamp=brief.timestamp.isoformat(),
            risk_level=brief.risk_level.value,
            risk_emoji=brief.get_emoji(),
            risk_score=brief.risk_score,
            situation=brief.situation,
            background=brief.background,
            assessment=brief.assessment,
            recommendation=brief.recommendation,
            data_quality_score=brief.data_quality_score,
            confidence_level=brief.confidence_level,
            generated_by=brief.generated_by,
            age=patient_demo['age'] if patient_demo else None,
            gender=patient_demo['gender'] if patient_demo else None,
            careunit=patient_demo['careunit'] if patient_demo else None,
            trend_report=brief.trend_report.to_dict() if brief.trend_report else None,
            conflict_report=brief.conflict_report.to_dict() if brief.conflict_report else None,
            timebomb_report=brief.timebomb_report.to_dict() if brief.timebomb_report else None,
            timeline=brief.timeline if hasattr(brief, 'timeline') else [],
            data_quality=data_quality_dict
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting brief for patient {patient_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve patient brief: {str(e)}"
        )


@app.post("/patients/{patient_id}/refresh", response_model=RefreshResponse)
async def refresh_patient(patient_id: str):
    """
    Re-run the analysis pipeline for a specific patient.
    
    Args:
        patient_id: Patient subject ID
        
    Returns:
        Refresh status and updated risk information
    """
    try:
        await refresh_patient_brief(patient_id)
        
        brief = patient_briefs.get(patient_id)
        
        if not brief:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Failed to generate brief for patient {patient_id}"
            )
        
        return RefreshResponse(
            success=True,
            message=f"Successfully refreshed analysis for patient {patient_id}",
            patient_id=patient_id,
            risk_level=brief.risk_level.value,
            risk_score=brief.risk_score
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error refreshing patient {patient_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to refresh patient analysis: {str(e)}"
        )


@app.get("/patients/{patient_id}/brief/formatted")
async def get_patient_brief_formatted(patient_id: str):
    """
    Get formatted text version of SBAR brief (for console/debugging).
    
    Args:
        patient_id: Patient subject ID
        
    Returns:
        Plain text formatted SBAR brief
    """
    try:
        # Check if we have a cached brief
        if patient_id not in patient_briefs:
            await refresh_patient_brief(patient_id)
        
        brief = patient_briefs.get(patient_id)
        
        if not brief:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Patient {patient_id} not found"
            )
        
        formatted_text = format_sbar_for_display(brief)
        
        return JSONResponse(
            content={"formatted_brief": formatted_text},
            media_type="application/json"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting formatted brief for patient {patient_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve formatted brief: {str(e)}"
        )


# ============================================================================
# Helper Functions
# ============================================================================

def generate_flags_from_brief(brief: SBARBrief) -> List[str]:
    """
    Generate clinical flags from SBAR brief and agent reports.
    
    Args:
        brief: SBARBrief with agent reports
        
    Returns:
        List of flag strings
    """
    flags = []
    
    # Flags from trend report
    if brief.trend_report:
        for trend in brief.trend_report.trends:
            if trend.concern_level >= 3:
                flags.append(f"⚠️ {trend.vital_name} {trend.direction.value}")
            elif trend.concern_level >= 2:
                flags.append(f"↗️ {trend.vital_name} trending")
    
    # Flags from conflict report
    if brief.conflict_report:
        for conflict in brief.conflict_report.conflicts:
            if conflict.severity >= 3:
                flags.append(f"🔴 {conflict.conflict_type.value.replace('_', ' ').title()}")
            elif conflict.severity >= 2:
                flags.append(f"🟡 {conflict.conflict_type.value.replace('_', ' ').title()}")
    
    # Flags from timebomb report
    if brief.timebomb_report:
        for tb in brief.timebomb_report.timebombs:
            if tb.urgency >= 3:
                flags.append(f"⏰ {tb.timebomb_type.value.replace('_', ' ').title()}")
    
    # Limit to top 5 most critical flags
    return flags[:5]


def extract_latest_vitals(snapshot: Dict[str, Any]) -> Dict[str, float]:
    """
    Extract the latest vital signs from a patient snapshot.
    
    Args:
        snapshot: Patient data snapshot from emitter
        
    Returns:
        Dictionary with latest vital values (hr, sbp, dbp, map, rr, spo2, temp)
    """
    vitals = {
        'hr': 0.0,
        'sbp': 0.0,
        'dbp': 0.0,
        'map': 0.0,
        'rr': 0.0,
        'spo2': 0.0,
        'temp': 0.0,
    }
    
    if not snapshot or 'records' not in snapshot:
        return vitals
    
    records = snapshot['records']
    if not records:
        return vitals
    
    # Vital sign label mappings
    vital_mappings = {
        'Heart Rate': 'hr',
        'Respiratory Rate': 'rr',
        'Non Invasive Blood Pressure systolic': 'sbp',
        'Systolic BP': 'sbp',  # Alternative label
        'Non Invasive Blood Pressure diastolic': 'dbp',
        'Diastolic BP': 'dbp',  # Alternative label
        'Mean Arterial Pressure': 'map',
        'Arterial Blood Pressure mean': 'map',
        'O2 saturation pulseoxymetry': 'spo2',
        'SpO2': 'spo2',  # Alternative label
        'Temperature Celsius': 'temp',
        'Temperature Fahrenheit': 'temp',
        'Temperature': 'temp',  # Alternative label
    }
    
    # Track the latest timestamp for each vital
    latest_values = {}
    latest_times = {}
    
    for record in records:
        label = record.get('label', '')
        value = record.get('valuenum')
        charttime = record.get('charttime')
        
        if label in vital_mappings and value is not None:
            vital_key = vital_mappings[label]
            
            # Convert Fahrenheit to Celsius if needed
            if label == 'Temperature Fahrenheit':
                value = (value - 32) * 5/9
            
            # Keep the most recent value for each vital
            if vital_key not in latest_times or charttime > latest_times[vital_key]:
                latest_values[vital_key] = value
                latest_times[vital_key] = charttime
    
    # Update vitals dict with latest values
    for key, value in latest_values.items():
        vitals[key] = round(value, 1)
    
    # Calculate MAP if we have SBP and DBP but no direct MAP
    if vitals['map'] == 0.0 and vitals['sbp'] > 0 and vitals['dbp'] > 0:
        # MAP = DBP + (SBP - DBP) / 3
        vitals['map'] = round(vitals['dbp'] + (vitals['sbp'] - vitals['dbp']) / 3, 1)
    
    return vitals


async def refresh_patient_brief(patient_id: str) -> None:
    """
    Generate/refresh SBAR brief for a patient.
    
    Args:
        patient_id: Patient subject ID
    """
    logger.info(f"Refreshing brief for patient {patient_id}")
    
    # Get previous risk level if exists
    previous_risk_level = None
    if patient_id in patient_briefs:
        previous_risk_level = patient_briefs[patient_id].risk_level
    
    # Get patient snapshot from emitter
    snapshot = emitter.get_snapshot(patient_id, window_hours=6)
    
    if not snapshot or not snapshot.get('records'):
        raise ValueError(f"No data available for patient {patient_id}")
    
    # Create PatientDataObject
    patient_data = create_pdo_from_emitter_data(snapshot)
    
    # Run coordinator to generate SBAR brief (pass previous risk level for state tracking)
    sbar_brief = await coordinate(patient_data, previous_risk_level=previous_risk_level)
    
    # Cache the brief and PDO
    patient_briefs[patient_id] = sbar_brief
    patient_data_objects[patient_id] = patient_data
    
    logger.info(
        f"Brief refreshed for patient {patient_id}: "
        f"Risk={sbar_brief.risk_level.value}, Score={sbar_brief.risk_score:.1f}"
    )


@app.on_event("startup")
async def startup_event():
    """
    Initialize the API on startup.
    """
    logger.info("=" * 80)
    logger.info("ICU Silent Deterioration Spotter API - Starting Up")
    logger.info("=" * 80)
    
    # Load data
    logger.info("Loading patient data...")
    emitter.load_data()
    
    # Get patient list
    patients = emitter.get_patient_list()
    logger.info(f"Found {len(patients)} patients in dataset")
    
    # Pre-generate briefs for all patients to ensure consistency
    logger.info("Pre-generating briefs for all patients...")
    for patient in patients:
        try:
            await refresh_patient_brief(patient['patient_id'])
            logger.info(f"✓ Generated brief for patient {patient['patient_id']}")
        except Exception as e:
            logger.error(f"✗ Error pre-generating brief for {patient['patient_id']}: {e}")
    
    logger.info(f"Pre-generated {len(patient_briefs)} patient briefs")
    logger.info("API startup complete")
    logger.info("=" * 80)


@app.on_event("shutdown")
async def shutdown_event():
    """
    Cleanup on API shutdown.
    """
    logger.info("API shutting down...")


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    logger.info("Starting ICU Silent Deterioration Spotter API")
    logger.info("API will be available at: http://localhost:8000")
    logger.info("API documentation at: http://localhost:8000/docs")
    
    uvicorn.run(
        "api_main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Enable auto-reload during development
        log_level="info"
    )

# Made with Bob