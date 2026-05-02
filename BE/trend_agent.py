"""
Module: trend_agent.py
Purpose: Layer 1 - Trend Analysis Agent
Layer: 1 (Agent)

Part of ICU Silent Deterioration Spotter
Hackathon: IBM Bob Challenge 2026

This agent detects rate-of-change in vital signs (HR, RR, SBP, SpO2, Temp).
Simple implementation prioritizing correctness over complex mathematics.
"""

import asyncio
from datetime import datetime
from typing import List, Dict, Optional
import logging
from statistics import mean

from schemas import (
    PatientDataObject,
    VitalReading,
    VitalTrend,
    TrendReport,
    TrendDirection
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Vital sign normal ranges and thresholds
VITAL_THRESHOLDS = {
    "Heart Rate": {"normal_min": 60, "normal_max": 100, "critical_min": 40, "critical_max": 130},
    "Respiratory Rate": {"normal_min": 12, "normal_max": 20, "critical_min": 8, "critical_max": 30},
    "Non Invasive Blood Pressure systolic": {"normal_min": 90, "normal_max": 140, "critical_min": 70, "critical_max": 180},
    "O2 saturation pulseoxymetry": {"normal_min": 95, "normal_max": 100, "critical_min": 88, "critical_max": 100},
    "Temperature Fahrenheit": {"normal_min": 97.0, "normal_max": 99.5, "critical_min": 95.0, "critical_max": 103.0},
    "Temperature Celsius": {"normal_min": 36.1, "normal_max": 37.5, "critical_min": 35.0, "critical_max": 39.4}
}


def calculate_simple_slope(values: List[float], timestamps: List[datetime]) -> float:
    """
    Calculate simple slope using first and last values.
    
    Args:
        values: List of vital values
        timestamps: List of corresponding timestamps
        
    Returns:
        Slope (change per hour)
    """
    if len(values) < 2:
        return 0.0
    
    # Calculate time difference in hours
    time_diff_hours = (timestamps[-1] - timestamps[0]).total_seconds() / 3600
    
    if time_diff_hours == 0:
        return 0.0
    
    # Calculate value change
    value_change = values[-1] - values[0]
    
    # Return change per hour
    return value_change / time_diff_hours


def detect_trend_direction(slope: float, threshold: float = 0.5) -> TrendDirection:
    """
    Determine trend direction based on slope.
    
    Args:
        slope: Rate of change per hour
        threshold: Minimum slope to consider as rising/falling
        
    Returns:
        TrendDirection enum
    """
    if abs(slope) < threshold:
        return TrendDirection.STABLE
    elif slope > 0:
        return TrendDirection.RISING
    else:
        return TrendDirection.FALLING


def calculate_acceleration(values: List[float], timestamps: List[datetime]) -> float:
    """
    Calculate acceleration by comparing early vs late window slopes.
    
    Args:
        values: List of vital values
        timestamps: List of corresponding timestamps
        
    Returns:
        Acceleration value (positive = accelerating change)
    """
    if len(values) < 4:
        return 0.0
    
    # Split into early and late halves
    mid_point = len(values) // 2
    
    early_values = values[:mid_point]
    early_times = timestamps[:mid_point]
    
    late_values = values[mid_point:]
    late_times = timestamps[mid_point:]
    
    # Calculate slopes for each half
    early_slope = calculate_simple_slope(early_values, early_times)
    late_slope = calculate_simple_slope(late_values, late_times)
    
    # Acceleration is the difference in slopes
    return late_slope - early_slope


def score_concern_level(
    vital_name: str,
    current_value: float,
    slope: float,
    acceleration: float
) -> int:
    """
    Assign concern level (0-3) based on vital trends.
    
    Args:
        vital_name: Name of the vital sign
        current_value: Most recent value
        slope: Rate of change per hour
        acceleration: Change in slope
        
    Returns:
        Concern level (0=none, 1=mild, 2=moderate, 3=severe)
    """
    thresholds = VITAL_THRESHOLDS.get(vital_name, {})
    
    if not thresholds:
        return 0
    
    concern = 0
    
    # Check if current value is outside normal range
    if current_value < thresholds.get("normal_min", 0) or current_value > thresholds.get("normal_max", 999):
        concern += 1
    
    # Check if current value is in critical range
    if current_value < thresholds.get("critical_min", 0) or current_value > thresholds.get("critical_max", 999):
        concern += 1
    
    # Check if slope is significant (moving away from normal)
    if abs(slope) > 2.0:  # Significant change per hour
        concern += 1
    
    # Check if acceleration is significant (trend is accelerating)
    if abs(acceleration) > 1.0:
        concern += 1
    
    # Cap at 3
    return min(concern, 3)


def analyze_vital_trend(vital_name: str, readings: List[VitalReading]) -> Optional[VitalTrend]:
    """
    Analyze trend for a single vital sign.
    
    Args:
        vital_name: Name of the vital sign
        readings: List of VitalReading objects for this vital
        
    Returns:
        VitalTrend object or None if insufficient data
    """
    if len(readings) < 2:
        logger.warning(f"Insufficient data for {vital_name}: {len(readings)} readings")
        return None
    
    # Extract values and timestamps
    values = [r.value for r in readings]
    timestamps = [r.charttime for r in readings]
    
    # Calculate metrics
    slope = calculate_simple_slope(values, timestamps)
    acceleration = calculate_acceleration(values, timestamps)
    direction = detect_trend_direction(slope)
    
    # Get current value
    current_value = values[-1]
    
    # Score concern level
    concern_level = score_concern_level(vital_name, current_value, slope, acceleration)
    
    # Generate simple reasoning
    reasoning = generate_simple_reasoning(vital_name, current_value, slope, direction, concern_level)
    
    return VitalTrend(
        vital_name=vital_name,
        direction=direction,
        slope=slope,
        acceleration=acceleration,
        concern_level=concern_level,
        values=values,
        timestamps=timestamps,
        reasoning=reasoning
    )


def generate_simple_reasoning(
    vital_name: str,
    current_value: float,
    slope: float,
    direction: TrendDirection,
    concern_level: int
) -> str:
    """
    Generate simple plain-English reasoning for a trend.
    
    Args:
        vital_name: Name of the vital sign
        current_value: Most recent value
        slope: Rate of change per hour
        direction: Trend direction
        concern_level: Concern level (0-3)
        
    Returns:
        Plain-English reasoning string
    """
    if concern_level == 0:
        return f"{vital_name} is stable at {current_value:.1f}."
    
    direction_text = {
        TrendDirection.RISING: "rising",
        TrendDirection.FALLING: "falling",
        TrendDirection.STABLE: "stable",
        TrendDirection.VOLATILE: "volatile"
    }.get(direction, "changing")
    
    concern_text = {
        1: "mild concern",
        2: "moderate concern",
        3: "severe concern"
    }.get(concern_level, "concern")
    
    return (
        f"{vital_name} is {direction_text} at {abs(slope):.1f} units/hour. "
        f"Current value: {current_value:.1f}. Level of concern: {concern_text}."
    )


async def analyze_trends(patient_data: PatientDataObject) -> TrendReport:
    """
    Main entry point for trend analysis agent.
    Analyzes vital sign trends for a patient.
    
    Args:
        patient_data: PatientDataObject containing patient vitals
        
    Returns:
        TrendReport with analysis of all vital trends
    """
    logger.info(f"Analyzing trends for patient {patient_data.patient_id}")
    
    # Group vitals by type
    vitals_by_type: Dict[str, List[VitalReading]] = {}
    for vital in patient_data.vitals:
        if vital.label not in vitals_by_type:
            vitals_by_type[vital.label] = []
        vitals_by_type[vital.label].append(vital)
    
    # Analyze each vital type
    trends = []
    for vital_name, readings in vitals_by_type.items():
        trend = analyze_vital_trend(vital_name, readings)
        if trend:
            trends.append(trend)
    
    # Calculate overall concern level (max of all trends)
    overall_concern = max([t.concern_level for t in trends], default=0)
    
    # Generate summary
    summary = generate_summary(trends, overall_concern)
    
    # Create report
    report = TrendReport(
        patient_id=patient_data.patient_id,
        timestamp=datetime.now(),
        trends=trends,
        overall_concern=overall_concern,
        summary=summary,
        llm_reasoning=""  # Will be populated by LLM in future enhancement
    )
    
    logger.info(
        f"Trend analysis complete for patient {patient_data.patient_id}: "
        f"{len(trends)} vitals analyzed, overall concern: {overall_concern}"
    )
    
    return report


def generate_summary(trends: List[VitalTrend], overall_concern: int) -> str:
    """
    Generate a summary of all trends.
    
    Args:
        trends: List of VitalTrend objects
        overall_concern: Overall concern level
        
    Returns:
        Summary string
    """
    if overall_concern == 0:
        return "All vital signs are stable with no concerning trends."
    
    concerning_trends = [t for t in trends if t.concern_level > 0]
    
    if not concerning_trends:
        return "No concerning trends detected."
    
    trend_descriptions = []
    for trend in concerning_trends:
        trend_descriptions.append(
            f"{trend.vital_name} ({trend.direction.value}, concern level {trend.concern_level})"
        )
    
    return f"Detected {len(concerning_trends)} concerning trend(s): {', '.join(trend_descriptions)}."


# Made with Bob