"""
Module: timebomb_agent.py
Purpose: Layer 1 - Time Bomb Observer Agent
Layer: 1 (Agent)

Part of ICU Silent Deterioration Spotter
Hackathon: IBM Bob Challenge 2026

This agent identifies forward-looking risks: pending labs, medications due,
and PRN gaps. Pure rule-based logic, no LLM calls.
Simple implementation prioritizing correctness.
"""

import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging

from schemas import (
    PatientDataObject,
    PendingLab,
    MedRecord,
    TimeBombItem,
    TimeBombReport,
    TimeBombType
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Critical medications that should not be missed
CRITICAL_MEDICATIONS = [
    "insulin",
    "heparin",
    "warfarin",
    "antibiotic",
    "vasopressor",
    "norepinephrine",
    "epinephrine",
    "dopamine",
    "vasopressin",
    "phenylephrine"
]


def check_pending_labs(patient_data: PatientDataObject, current_time: datetime) -> List[TimeBombItem]:
    """
    Check for pending lab orders that haven't been resulted.
    
    Args:
        patient_data: PatientDataObject
        current_time: Current timestamp
        
    Returns:
        List of TimeBombItem objects for pending labs
    """
    timebombs = []
    
    for pending_lab in patient_data.pending_labs:
        # Calculate how long the lab has been pending
        time_pending_minutes = int((current_time - pending_lab.ordertime).total_seconds() / 60)
        
        # Determine urgency based on priority and time pending
        urgency = 0
        
        if pending_lab.priority.lower() in ["stat", "urgent", "critical"]:
            if time_pending_minutes > 60:  # STAT lab pending >1 hour
                urgency = 3
            elif time_pending_minutes > 30:  # STAT lab pending >30 min
                urgency = 2
            else:
                urgency = 1
        elif pending_lab.priority.lower() == "routine":
            if time_pending_minutes > 240:  # Routine lab pending >4 hours
                urgency = 2
            elif time_pending_minutes > 120:  # Routine lab pending >2 hours
                urgency = 1
        
        if urgency > 0:
            timebombs.append(TimeBombItem(
                timebomb_type=TimeBombType.PENDING_LAB,
                urgency=urgency,
                description=f"{pending_lab.label} ordered {time_pending_minutes} minutes ago, not yet resulted",
                time_until_event=None,  # Already pending
                action_required=f"Follow up on {pending_lab.label} result ({pending_lab.priority} priority)"
            ))
    
    return timebombs


def check_medications_due(patient_data: PatientDataObject, current_time: datetime) -> List[TimeBombItem]:
    """
    Check for scheduled medications due in the next 2 hours.
    
    Args:
        patient_data: PatientDataObject
        current_time: Current timestamp
        
    Returns:
        List of TimeBombItem objects for medications due
    """
    timebombs = []
    
    for med in patient_data.medications:
        # Skip if medication has already stopped
        if med.stoptime and med.stoptime < current_time:
            continue
        
        # Parse frequency to estimate next dose time
        # Simple implementation: assume common frequencies
        next_dose_time = None
        interval_hours = None
        
        if med.frequency:
            freq_lower = med.frequency.lower()
            
            if "q1h" in freq_lower or "every 1 hour" in freq_lower:
                interval_hours = 1
            elif "q2h" in freq_lower or "every 2 hour" in freq_lower:
                interval_hours = 2
            elif "q4h" in freq_lower or "every 4 hour" in freq_lower:
                interval_hours = 4
            elif "q6h" in freq_lower or "every 6 hour" in freq_lower:
                interval_hours = 6
            elif "q8h" in freq_lower or "every 8 hour" in freq_lower:
                interval_hours = 8
            elif "q12h" in freq_lower or "every 12 hour" in freq_lower or "bid" in freq_lower:
                interval_hours = 12
            elif "daily" in freq_lower or "qd" in freq_lower:
                interval_hours = 24
        
        if interval_hours:
            # Estimate next dose (simplified: assume last dose was at start time)
            next_dose_time = med.starttime + timedelta(hours=interval_hours)
            
            # Check if due within next 2 hours
            time_until_due = (next_dose_time - current_time).total_seconds() / 60
            
            if 0 <= time_until_due <= 120:  # Due within next 2 hours
                # Check if it's a critical medication
                is_critical = any(crit_med in med.drug.lower() for crit_med in CRITICAL_MEDICATIONS)
                
                urgency = 0
                if time_until_due <= 15:  # Due in next 15 minutes
                    urgency = 3 if is_critical else 2
                elif time_until_due <= 60:  # Due in next hour
                    urgency = 2 if is_critical else 1
                else:  # Due in next 2 hours
                    urgency = 1 if is_critical else 0
                
                if urgency > 0:
                    timebombs.append(TimeBombItem(
                        timebomb_type=TimeBombType.MEDICATION_DUE,
                        urgency=urgency,
                        description=f"{med.drug} ({med.dose}) due in {int(time_until_due)} minutes",
                        time_until_event=int(time_until_due),
                        action_required=f"Prepare and administer {med.drug} {med.dose} {med.route}"
                    ))
    
    return timebombs


def check_prn_gaps(patient_data: PatientDataObject, current_time: datetime) -> List[TimeBombItem]:
    """
    Check for PRN medications that haven't been given in a long time.
    
    Args:
        patient_data: PatientDataObject
        current_time: Current timestamp
        
    Returns:
        List of TimeBombItem objects for PRN gaps
    """
    timebombs = []
    
    # Common PRN medications to monitor
    prn_keywords = ["prn", "as needed", "pain", "nausea", "anxiety", "agitation"]
    
    for med in patient_data.medications:
        # Check if it's a PRN medication
        is_prn = False
        if med.frequency:
            is_prn = any(keyword in med.frequency.lower() for keyword in prn_keywords)
        
        if not is_prn:
            continue
        
        # Calculate time since last dose (using start time as proxy for last dose)
        hours_since_dose = (current_time - med.starttime).total_seconds() / 3600
        
        # Flag if PRN hasn't been given in a long time
        urgency = 0
        
        if hours_since_dose > 24:  # No PRN in 24+ hours
            urgency = 2
        elif hours_since_dose > 18:  # No PRN in 18+ hours
            urgency = 1
        
        if urgency > 0:
            timebombs.append(TimeBombItem(
                timebomb_type=TimeBombType.PRN_GAP,
                urgency=urgency,
                description=f"{med.drug} (PRN) not given in {int(hours_since_dose)} hours",
                time_until_event=None,
                action_required=f"Assess patient need for {med.drug} PRN"
            ))
    
    return timebombs


def check_missing_orders(patient_data: PatientDataObject, current_time: datetime) -> List[TimeBombItem]:
    """
    Check for potentially missing orders based on patient condition.
    
    Args:
        patient_data: PatientDataObject
        current_time: Current timestamp
        
    Returns:
        List of TimeBombItem objects for missing orders
    """
    timebombs = []
    
    # Check if patient has any medications at all
    if not patient_data.medications:
        timebombs.append(TimeBombItem(
            timebomb_type=TimeBombType.MISSING_ORDER,
            urgency=1,
            description="No active medication orders found",
            time_until_event=None,
            action_required="Review patient chart for missing medication orders"
        ))
    
    # Check if patient has recent labs
    if patient_data.labs:
        latest_lab_time = max(lab.charttime for lab in patient_data.labs)
        hours_since_lab = (current_time - latest_lab_time).total_seconds() / 3600
        
        if hours_since_lab > 24:  # No labs in 24+ hours
            timebombs.append(TimeBombItem(
                timebomb_type=TimeBombType.MISSING_ORDER,
                urgency=1,
                description=f"No lab results in {int(hours_since_lab)} hours",
                time_until_event=None,
                action_required="Consider ordering routine labs"
            ))
    
    return timebombs


async def identify_timebombs(patient_data: PatientDataObject) -> TimeBombReport:
    """
    Main entry point for time bomb observer agent.
    Identifies forward-looking risks and pending actions.
    
    Args:
        patient_data: PatientDataObject containing patient data
        
    Returns:
        TimeBombReport with identified time bomb items
    """
    logger.info(f"Identifying time bombs for patient {patient_data.patient_id}")
    
    current_time = datetime.now()
    
    # Collect all time bombs
    timebombs = []
    
    # Check pending labs
    timebombs.extend(check_pending_labs(patient_data, current_time))
    
    # Check medications due
    timebombs.extend(check_medications_due(patient_data, current_time))
    
    # Check PRN gaps
    timebombs.extend(check_prn_gaps(patient_data, current_time))
    
    # Check missing orders
    timebombs.extend(check_missing_orders(patient_data, current_time))
    
    # Sort by urgency (highest first)
    timebombs.sort(key=lambda t: t.urgency, reverse=True)
    
    # Calculate overall urgency (max of all items)
    overall_urgency = max([t.urgency for t in timebombs], default=0)
    
    # Generate summary
    summary = generate_summary(timebombs, overall_urgency)
    
    # Create report
    report = TimeBombReport(
        patient_id=patient_data.patient_id,
        timestamp=current_time,
        timebombs=timebombs,
        overall_urgency=overall_urgency,
        summary=summary
    )
    
    logger.info(
        f"Time bomb identification complete for patient {patient_data.patient_id}: "
        f"{len(timebombs)} item(s) identified, overall urgency: {overall_urgency}"
    )
    
    return report


def generate_summary(timebombs: List[TimeBombItem], overall_urgency: int) -> str:
    """
    Generate a summary of identified time bombs.
    
    Args:
        timebombs: List of TimeBombItem objects
        overall_urgency: Overall urgency level
        
    Returns:
        Summary string
    """
    if overall_urgency == 0:
        return "No pending actions or time-sensitive items identified."
    
    # Count by type
    type_counts = {}
    for tb in timebombs:
        type_name = tb.timebomb_type.value.replace('_', ' ').title()
        type_counts[type_name] = type_counts.get(type_name, 0) + 1
    
    # Build summary
    type_descriptions = [f"{count} {type_name}" for type_name, count in type_counts.items()]
    
    return f"Identified {len(timebombs)} time-sensitive item(s): {', '.join(type_descriptions)}."


# Made with Bob