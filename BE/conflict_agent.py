"""
Module: conflict_agent.py
Purpose: Layer 1 - Lab-Vitals Conflict Agent
Layer: 1 (Agent)

Part of ICU Silent Deterioration Spotter
Hackathon: IBM Bob Challenge 2026

This agent detects cross-signal patterns between vitals and labs that indicate
hidden deterioration (compensated shock, early AKI, pre-respiratory failure).
Simple implementation prioritizing correctness.
"""

import asyncio
from datetime import datetime
from typing import List, Dict, Optional
import logging

from schemas import (
    PatientDataObject,
    VitalReading,
    LabReading,
    OutputReading,
    ConflictPattern,
    ConflictReport,
    ConflictType
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_latest_vital(vitals: List[VitalReading], vital_name: str) -> Optional[float]:
    """
    Get the most recent value for a specific vital sign.
    
    Args:
        vitals: List of VitalReading objects
        vital_name: Name of the vital to find
        
    Returns:
        Latest value or None if not found
    """
    matching_vitals = [v for v in vitals if v.label == vital_name]
    if not matching_vitals:
        return None
    
    # Sort by time and get latest
    latest = max(matching_vitals, key=lambda v: v.charttime)
    return latest.value


def get_latest_lab(labs: List[LabReading], lab_name: str) -> Optional[float]:
    """
    Get the most recent value for a specific lab.
    
    Args:
        labs: List of LabReading objects
        lab_name: Name of the lab to find
        
    Returns:
        Latest value or None if not found
    """
    matching_labs = [l for l in labs if l.label == lab_name]
    if not matching_labs:
        return None
    
    # Sort by time and get latest
    latest = max(matching_labs, key=lambda l: l.charttime)
    return latest.value


def calculate_lab_trend(labs: List[LabReading], lab_name: str) -> str:
    """
    Calculate simple trend for a lab value (rising/falling/stable).
    
    Args:
        labs: List of LabReading objects
        lab_name: Name of the lab
        
    Returns:
        Trend string: "rising", "falling", or "stable"
    """
    matching_labs = [l for l in labs if l.label == lab_name]
    if len(matching_labs) < 2:
        return "stable"
    
    # Sort by time
    sorted_labs = sorted(matching_labs, key=lambda l: l.charttime)
    
    # Compare first and last values
    first_value = sorted_labs[0].value
    last_value = sorted_labs[-1].value
    
    change_percent = ((last_value - first_value) / first_value) * 100 if first_value != 0 else 0
    
    if change_percent > 10:
        return "rising"
    elif change_percent < -10:
        return "falling"
    else:
        return "stable"


def calculate_urine_output_trend(outputs: List[OutputReading]) -> str:
    """
    Calculate trend for urine output.
    
    Args:
        outputs: List of OutputReading objects
        
    Returns:
        Trend string: "rising", "falling", or "stable"
    """
    if len(outputs) < 2:
        return "stable"
    
    # Sort by time
    sorted_outputs = sorted(outputs, key=lambda o: o.charttime)
    
    # Calculate total output in first half vs second half
    mid_point = len(sorted_outputs) // 2
    first_half_total = sum(o.value for o in sorted_outputs[:mid_point])
    second_half_total = sum(o.value for o in sorted_outputs[mid_point:])
    
    if second_half_total < first_half_total * 0.7:  # 30% decrease
        return "falling"
    elif second_half_total > first_half_total * 1.3:  # 30% increase
        return "rising"
    else:
        return "stable"


def check_compensated_shock(patient_data: PatientDataObject) -> Optional[ConflictPattern]:
    """
    Detect compensated shock: Normal/stable BP but rising lactate.
    
    Args:
        patient_data: PatientDataObject
        
    Returns:
        ConflictPattern if detected, None otherwise
    """
    # Get latest SBP
    sbp = get_latest_vital(patient_data.vitals, "Non Invasive Blood Pressure systolic")
    if sbp is None:
        return None
    
    # Get latest lactate
    lactate = get_latest_lab(patient_data.labs, "Lactate")
    if lactate is None:
        return None
    
    # Get lactate trend
    lactate_trend = calculate_lab_trend(patient_data.labs, "Lactate")
    
    # Check for compensated shock pattern
    # Normal BP (>90) but elevated/rising lactate (>2.0)
    if sbp >= 90 and lactate > 2.0 and lactate_trend == "rising":
        severity = 2 if lactate > 4.0 else 1
        
        return ConflictPattern(
            conflict_type=ConflictType.COMPENSATED_SHOCK,
            severity=severity,
            description="Blood pressure appears stable but lactate is elevated and rising",
            vitals_involved=["Non Invasive Blood Pressure systolic"],
            labs_involved=["Lactate"],
            evidence={
                "sbp": sbp,
                "lactate": lactate,
                "lactate_trend": lactate_trend
            },
            clinical_significance=(
                "Patient may be in compensated shock. Despite normal BP, "
                "rising lactate suggests tissue hypoperfusion and early shock state."
            )
        )
    
    return None


def check_early_aki(patient_data: PatientDataObject) -> Optional[ConflictPattern]:
    """
    Detect early acute kidney injury: Rising creatinine + falling urine output.
    
    Args:
        patient_data: PatientDataObject
        
    Returns:
        ConflictPattern if detected, None otherwise
    """
    # Get latest creatinine
    creatinine = get_latest_lab(patient_data.labs, "Creatinine")
    if creatinine is None:
        return None
    
    # Get creatinine trend
    creatinine_trend = calculate_lab_trend(patient_data.labs, "Creatinine")
    
    # Get urine output trend
    urine_trend = calculate_urine_output_trend(patient_data.urine_output)
    
    # Check for early AKI pattern
    # Rising creatinine (>1.2) and falling urine output
    if creatinine > 1.2 and creatinine_trend == "rising" and urine_trend == "falling":
        severity = 3 if creatinine > 2.0 else 2
        
        return ConflictPattern(
            conflict_type=ConflictType.EARLY_AKI,
            severity=severity,
            description="Creatinine is rising while urine output is decreasing",
            vitals_involved=[],
            labs_involved=["Creatinine"],
            evidence={
                "creatinine": creatinine,
                "creatinine_trend": creatinine_trend,
                "urine_output_trend": urine_trend
            },
            clinical_significance=(
                "Patient showing early signs of acute kidney injury. "
                "Rising creatinine with decreasing urine output suggests declining renal function."
            )
        )
    
    return None


def check_pre_respiratory_failure(patient_data: PatientDataObject) -> Optional[ConflictPattern]:
    """
    Detect pre-respiratory failure: Stable SpO2 but rising respiratory rate.
    
    Args:
        patient_data: PatientDataObject
        
    Returns:
        ConflictPattern if detected, None otherwise
    """
    # Get latest SpO2
    spo2 = get_latest_vital(patient_data.vitals, "O2 saturation pulseoxymetry")
    if spo2 is None:
        return None
    
    # Get latest respiratory rate
    rr = get_latest_vital(patient_data.vitals, "Respiratory Rate")
    if rr is None:
        return None
    
    # Calculate RR trend
    rr_readings = [v for v in patient_data.vitals if v.label == "Respiratory Rate"]
    if len(rr_readings) < 2:
        return None
    
    sorted_rr = sorted(rr_readings, key=lambda v: v.charttime)
    rr_change = sorted_rr[-1].value - sorted_rr[0].value
    
    # Check for pre-respiratory failure pattern
    # SpO2 still acceptable (>92) but RR significantly elevated (>24) and rising
    if spo2 >= 92 and rr > 24 and rr_change > 4:
        severity = 3 if rr > 30 else 2
        
        return ConflictPattern(
            conflict_type=ConflictType.PRE_RESPIRATORY_FAILURE,
            severity=severity,
            description="Oxygen saturation appears adequate but respiratory rate is elevated and rising",
            vitals_involved=["O2 saturation pulseoxymetry", "Respiratory Rate"],
            labs_involved=[],
            evidence={
                "spo2": spo2,
                "respiratory_rate": rr,
                "rr_change": rr_change
            },
            clinical_significance=(
                "Patient may be compensating for respiratory distress. "
                "Despite adequate SpO2, rising respiratory rate suggests increasing work of breathing "
                "and potential impending respiratory failure."
            )
        )
    
    return None


def check_hidden_sepsis(patient_data: PatientDataObject) -> Optional[ConflictPattern]:
    """
    Detect hidden sepsis: Normal vitals but elevated WBC and lactate.
    
    Args:
        patient_data: PatientDataObject
        
    Returns:
        ConflictPattern if detected, None otherwise
    """
    # Get latest temperature
    temp_f = get_latest_vital(patient_data.vitals, "Temperature Fahrenheit")
    temp_c = get_latest_vital(patient_data.vitals, "Temperature Celsius")
    
    # Convert to Fahrenheit if only Celsius available
    if temp_f is None and temp_c is not None:
        temp_f = (temp_c * 9/5) + 32
    
    if temp_f is None:
        return None
    
    # Get latest WBC
    wbc = get_latest_lab(patient_data.labs, "White Blood Cells")
    if wbc is None:
        return None
    
    # Get latest lactate
    lactate = get_latest_lab(patient_data.labs, "Lactate")
    if lactate is None:
        return None
    
    # Check for hidden sepsis pattern
    # Temperature relatively normal (97-100.4) but elevated WBC (>12) and lactate (>2)
    if 97.0 <= temp_f <= 100.4 and wbc > 12.0 and lactate > 2.0:
        severity = 3 if (wbc > 15.0 or lactate > 4.0) else 2
        
        return ConflictPattern(
            conflict_type=ConflictType.HIDDEN_SEPSIS,
            severity=severity,
            description="Temperature appears normal but WBC and lactate are elevated",
            vitals_involved=["Temperature"],
            labs_involved=["White Blood Cells", "Lactate"],
            evidence={
                "temperature_f": temp_f,
                "wbc": wbc,
                "lactate": lactate
            },
            clinical_significance=(
                "Patient may have early or occult sepsis. "
                "Despite normal temperature, elevated WBC and lactate suggest systemic infection."
            )
        )
    
    return None


async def detect_conflicts(patient_data: PatientDataObject) -> ConflictReport:
    """
    Main entry point for conflict detection agent.
    Detects cross-signal patterns indicating hidden deterioration.
    
    Args:
        patient_data: PatientDataObject containing patient data
        
    Returns:
        ConflictReport with detected conflict patterns
    """
    logger.info(f"Detecting conflicts for patient {patient_data.patient_id}")
    
    # Check for each conflict pattern
    conflicts = []
    
    # Compensated shock
    shock_pattern = check_compensated_shock(patient_data)
    if shock_pattern:
        conflicts.append(shock_pattern)
    
    # Early AKI
    aki_pattern = check_early_aki(patient_data)
    if aki_pattern:
        conflicts.append(aki_pattern)
    
    # Pre-respiratory failure
    resp_pattern = check_pre_respiratory_failure(patient_data)
    if resp_pattern:
        conflicts.append(resp_pattern)
    
    # Hidden sepsis
    sepsis_pattern = check_hidden_sepsis(patient_data)
    if sepsis_pattern:
        conflicts.append(sepsis_pattern)
    
    # Calculate overall severity (max of all conflicts)
    overall_severity = max([c.severity for c in conflicts], default=0)
    
    # Generate summary
    summary = generate_summary(conflicts, overall_severity)
    
    # Create report
    report = ConflictReport(
        patient_id=patient_data.patient_id,
        timestamp=datetime.now(),
        conflicts=conflicts,
        overall_severity=overall_severity,
        summary=summary,
        llm_reasoning=""  # Will be populated by LLM in future enhancement
    )
    
    logger.info(
        f"Conflict detection complete for patient {patient_data.patient_id}: "
        f"{len(conflicts)} conflict(s) detected, overall severity: {overall_severity}"
    )
    
    return report


def generate_summary(conflicts: List[ConflictPattern], overall_severity: int) -> str:
    """
    Generate a summary of detected conflicts.
    
    Args:
        conflicts: List of ConflictPattern objects
        overall_severity: Overall severity level
        
    Returns:
        Summary string
    """
    if overall_severity == 0:
        return "No cross-signal conflicts detected. Vitals and labs are concordant."
    
    conflict_descriptions = []
    for conflict in conflicts:
        conflict_descriptions.append(
            f"{conflict.conflict_type.value.replace('_', ' ').title()} (severity {conflict.severity})"
        )
    
    return f"Detected {len(conflicts)} conflict pattern(s): {', '.join(conflict_descriptions)}."


# Made with Bob