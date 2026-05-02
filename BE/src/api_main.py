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
    
    # Full detailed reports (not just summaries)
    trend_report: Optional[Dict[str, Any]] = None
    conflict_report: Optional[Dict[str, Any]] = None
    timebomb_report: Optional[Dict[str, Any]] = None


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
    Get list of all patients with their current risk levels.
    
    Returns:
        List of patients with risk information
    """
    try:
        # Get patient list from emitter
        patients = emitter.get_patient_list()
        
        # Enrich with risk information from cached briefs
        patient_list = []
        for patient in patients:
            patient_id = patient['patient_id']
            
            # Get cached brief if available
            brief = patient_briefs.get(patient_id)
            
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
            else:
                # No brief yet, show as unknown
                patient_item = PatientListItem(
                    patient_id=patient_id,
                    stay_id=patient['stay_id'],
                    risk_level=RiskLevel.GREEN,  # Default
                    risk_score=0.0,
                    last_updated=datetime.now(),
                    careunit=patient['careunit'],
                    age=patient['age'],
                    gender=patient['gender']
                )
            
            patient_list.append(patient_item.to_dict())
        
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
            trend_report=brief.trend_report.to_dict() if brief.trend_report else None,
            conflict_report=brief.conflict_report.to_dict() if brief.conflict_report else None,
            timebomb_report=brief.timebomb_report.to_dict() if brief.timebomb_report else None
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

async def refresh_patient_brief(patient_id: str) -> None:
    """
    Generate/refresh SBAR brief for a patient.
    
    Args:
        patient_id: Patient subject ID
    """
    logger.info(f"Refreshing brief for patient {patient_id}")
    
    # Get patient snapshot from emitter
    snapshot = emitter.get_snapshot(patient_id, window_hours=6)
    
    if not snapshot or not snapshot.get('records'):
        raise ValueError(f"No data available for patient {patient_id}")
    
    # Create PatientDataObject
    patient_data = create_pdo_from_emitter_data(snapshot)
    
    # Run coordinator to generate SBAR brief
    sbar_brief = await coordinate(patient_data)
    
    # Cache the brief
    patient_briefs[patient_id] = sbar_brief
    
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
    
    # Pre-generate briefs for all patients (optional, for demo)
    # Uncomment to pre-populate cache
    # logger.info("Pre-generating briefs for all patients...")
    # for patient in patients[:3]:  # Limit to first 3 for demo
    #     try:
    #         await refresh_patient_brief(patient['patient_id'])
    #     except Exception as e:
    #         logger.error(f"Error pre-generating brief for {patient['patient_id']}: {e}")
    
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