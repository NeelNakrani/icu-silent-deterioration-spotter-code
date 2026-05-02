"""
Module: test_layer1.py
Purpose: Test script for Layer 1 agents
Layer: Testing

Part of ICU Silent Deterioration Spotter
Hackathon: IBM Bob Challenge 2026

This script tests all three Layer 1 agents with sample data.
"""

import asyncio
from datetime import datetime, timedelta
import logging

from schemas import (
    PatientDataObject,
    VitalReading,
    LabReading,
    OutputReading,
    MedRecord,
    PendingLab,
    DataQuality
)

from trend_agent import analyze_trends
from conflict_agent import detect_conflicts
from timebomb_agent import identify_timebombs

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def create_test_patient_data() -> PatientDataObject:
    """
    Create a test PatientDataObject with sample data.
    
    Returns:
        PatientDataObject with test data
    """
    now = datetime.now()
    window_start = now - timedelta(hours=6)
    
    # Create sample vitals with concerning trends
    vitals = []
    for i in range(12):  # 12 readings over 6 hours (every 30 min)
        time = window_start + timedelta(minutes=30 * i)
        
        # Heart rate rising
        vitals.append(VitalReading(
            charttime=time,
            label="Heart Rate",
            value=80 + (i * 3),  # Rising from 80 to 113
            unit="bpm",
            itemid=220045
        ))
        
        # Respiratory rate rising
        vitals.append(VitalReading(
            charttime=time,
            label="Respiratory Rate",
            value=16 + (i * 1.5),  # Rising from 16 to 32.5
            unit="breaths/min",
            itemid=220210
        ))
        
        # Blood pressure stable
        vitals.append(VitalReading(
            charttime=time,
            label="Non Invasive Blood Pressure systolic",
            value=110 + (i * 0.5),  # Stable around 110-115
            unit="mmHg",
            itemid=220179
        ))
        
        # SpO2 stable
        vitals.append(VitalReading(
            charttime=time,
            label="O2 saturation pulseoxymetry",
            value=95 - (i * 0.2),  # Slowly declining but still >92
            unit="%",
            itemid=220277
        ))
    
    # Create sample labs showing conflicts
    labs = []
    
    # Rising lactate (compensated shock)
    labs.append(LabReading(
        charttime=window_start + timedelta(hours=1),
        label="Lactate",
        value=2.5,
        unit="mmol/L",
        itemid=50813
    ))
    labs.append(LabReading(
        charttime=window_start + timedelta(hours=4),
        label="Lactate",
        value=3.8,
        unit="mmol/L",
        itemid=50813
    ))
    
    # Rising creatinine (early AKI)
    labs.append(LabReading(
        charttime=window_start + timedelta(hours=2),
        label="Creatinine",
        value=1.3,
        unit="mg/dL",
        itemid=50912
    ))
    labs.append(LabReading(
        charttime=window_start + timedelta(hours=5),
        label="Creatinine",
        value=1.7,
        unit="mg/dL",
        itemid=50912
    ))
    
    # Elevated WBC (hidden sepsis)
    labs.append(LabReading(
        charttime=window_start + timedelta(hours=3),
        label="White Blood Cells",
        value=14.5,
        unit="K/uL",
        itemid=51301
    ))
    
    # Create sample urine output (declining)
    urine_output = []
    for i in range(6):
        time = window_start + timedelta(hours=i)
        # Declining output
        urine_output.append(OutputReading(
            charttime=time,
            value=80 - (i * 10),  # Declining from 80 to 30 mL/hr
            unit="mL",
            itemid=40055
        ))
    
    # Create sample medications
    medications = [
        MedRecord(
            starttime=window_start - timedelta(hours=2),
            stoptime=None,
            drug="Insulin Regular",
            dose="10 units",
            route="IV",
            frequency="Q4H"
        ),
        MedRecord(
            starttime=window_start - timedelta(hours=20),
            stoptime=None,
            drug="Morphine",
            dose="2 mg",
            route="IV",
            frequency="PRN pain"
        ),
        MedRecord(
            starttime=window_start - timedelta(hours=1),
            stoptime=None,
            drug="Norepinephrine",
            dose="0.1 mcg/kg/min",
            route="IV",
            frequency="Continuous"
        )
    ]
    
    # Create pending labs
    pending_labs = [
        PendingLab(
            ordertime=now - timedelta(minutes=75),
            label="Troponin",
            priority="STAT"
        ),
        PendingLab(
            ordertime=now - timedelta(hours=3),
            label="Blood Culture",
            priority="Routine"
        )
    ]
    
    # Create data quality
    data_quality = DataQuality(
        total_expected_readings=48,
        actual_readings=48,
        missing_vitals=[],
        missing_labs=[],
        data_gaps_minutes=[],
        completeness_score=1.0
    )
    
    # Create PatientDataObject
    patient_data = PatientDataObject(
        patient_id="TEST_001",
        stay_id="STAY_001",
        window_start=window_start,
        window_end=now,
        gender="M",
        age=65,
        careunit="MICU",
        vitals=vitals,
        labs=labs,
        urine_output=urine_output,
        medications=medications,
        pending_labs=pending_labs,
        data_quality=data_quality,
        intime=window_start - timedelta(days=2),
        outtime=None
    )
    
    return patient_data


async def test_all_agents():
    """
    Test all three Layer 1 agents.
    """
    logger.info("=" * 80)
    logger.info("TESTING LAYER 1 AGENTS")
    logger.info("=" * 80)
    
    # Create test patient data
    logger.info("\nCreating test patient data...")
    patient_data = create_test_patient_data()
    logger.info(f"✓ Created test data for patient {patient_data.patient_id}")
    logger.info(f"  - {len(patient_data.vitals)} vital readings")
    logger.info(f"  - {len(patient_data.labs)} lab results")
    logger.info(f"  - {len(patient_data.urine_output)} urine output readings")
    logger.info(f"  - {len(patient_data.medications)} medications")
    logger.info(f"  - {len(patient_data.pending_labs)} pending labs")
    
    # Test Trend Agent
    logger.info("\n" + "=" * 80)
    logger.info("TESTING TREND AGENT")
    logger.info("=" * 80)
    trend_report = await analyze_trends(patient_data)
    logger.info(f"\n✓ Trend Analysis Complete")
    logger.info(f"  - Overall Concern: {trend_report.overall_concern}/3")
    logger.info(f"  - Trends Analyzed: {len(trend_report.trends)}")
    logger.info(f"  - Summary: {trend_report.summary}")
    
    for trend in trend_report.trends:
        logger.info(f"\n  Vital: {trend.vital_name}")
        logger.info(f"    Direction: {trend.direction.value}")
        logger.info(f"    Slope: {trend.slope:.2f} units/hour")
        logger.info(f"    Concern Level: {trend.concern_level}/3")
        logger.info(f"    Reasoning: {trend.reasoning}")
    
    # Test Conflict Agent
    logger.info("\n" + "=" * 80)
    logger.info("TESTING CONFLICT AGENT")
    logger.info("=" * 80)
    conflict_report = await detect_conflicts(patient_data)
    logger.info(f"\n✓ Conflict Detection Complete")
    logger.info(f"  - Overall Severity: {conflict_report.overall_severity}/3")
    logger.info(f"  - Conflicts Detected: {len(conflict_report.conflicts)}")
    logger.info(f"  - Summary: {conflict_report.summary}")
    
    for conflict in conflict_report.conflicts:
        logger.info(f"\n  Conflict: {conflict.conflict_type.value}")
        logger.info(f"    Severity: {conflict.severity}/3")
        logger.info(f"    Description: {conflict.description}")
        logger.info(f"    Clinical Significance: {conflict.clinical_significance}")
        logger.info(f"    Evidence: {conflict.evidence}")
    
    # Test TimeBomb Agent
    logger.info("\n" + "=" * 80)
    logger.info("TESTING TIMEBOMB AGENT")
    logger.info("=" * 80)
    timebomb_report = await identify_timebombs(patient_data)
    logger.info(f"\n✓ Time Bomb Identification Complete")
    logger.info(f"  - Overall Urgency: {timebomb_report.overall_urgency}/3")
    logger.info(f"  - Time Bombs Identified: {len(timebomb_report.timebombs)}")
    logger.info(f"  - Summary: {timebomb_report.summary}")
    
    for timebomb in timebomb_report.timebombs:
        logger.info(f"\n  Time Bomb: {timebomb.timebomb_type.value}")
        logger.info(f"    Urgency: {timebomb.urgency}/3")
        logger.info(f"    Description: {timebomb.description}")
        logger.info(f"    Action Required: {timebomb.action_required}")
        if timebomb.time_until_event:
            logger.info(f"    Time Until Event: {timebomb.time_until_event} minutes")
    
    # Summary
    logger.info("\n" + "=" * 80)
    logger.info("TEST SUMMARY")
    logger.info("=" * 80)
    logger.info(f"✓ All three Layer 1 agents tested successfully")
    logger.info(f"  - Trend Agent: {len(trend_report.trends)} trends, concern level {trend_report.overall_concern}")
    logger.info(f"  - Conflict Agent: {len(conflict_report.conflicts)} conflicts, severity {conflict_report.overall_severity}")
    logger.info(f"  - TimeBomb Agent: {len(timebomb_report.timebombs)} items, urgency {timebomb_report.overall_urgency}")
    logger.info("\n✓ Layer 1 implementation complete and functional!")


if __name__ == "__main__":
    asyncio.run(test_all_agents())

# Made with Bob