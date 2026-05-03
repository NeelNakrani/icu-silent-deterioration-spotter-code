"""
Module: coordinator.py
Purpose: Layer 2 - Coordinator that aggregates agent reports and synthesizes SBAR+ briefs
Layer: 2 (Coordinator)

Part of ICU Silent Deterioration Spotter
Hackathon: IBM Bob Challenge 2026

This module coordinates all Layer 1 agents, aggregates their outputs,
and synthesizes a final SBAR+ brief for clinicians.
"""

import asyncio
from datetime import datetime
from typing import Tuple, Optional
import logging

from schemas import (
    PatientDataObject,
    TrendReport,
    ConflictReport,
    TimeBombReport,
    SBARBrief,
    RiskLevel
)

from trend_agent import analyze_trends
from conflict_agent import detect_conflicts
from timebomb_agent import identify_timebombs

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def run_all_agents(
    patient_data: PatientDataObject
) -> Tuple[TrendReport, ConflictReport, TimeBombReport]:
    """
    Run all three Layer 1 agents concurrently.
    
    Args:
        patient_data: PatientDataObject containing patient data
        
    Returns:
        Tuple of (TrendReport, ConflictReport, TimeBombReport)
    """
    logger.info(f"Running all agents concurrently for patient {patient_data.patient_id}")
    
    # Run all agents concurrently using asyncio.gather
    trend_report, conflict_report, timebomb_report = await asyncio.gather(
        analyze_trends(patient_data),
        detect_conflicts(patient_data),
        identify_timebombs(patient_data)
    )
    
    logger.info(
        f"All agents completed for patient {patient_data.patient_id}: "
        f"Trend concern={trend_report.overall_concern}, "
        f"Conflict severity={conflict_report.overall_severity}, "
        f"TimeBomb urgency={timebomb_report.overall_urgency}"
    )
    
    return trend_report, conflict_report, timebomb_report


def calculate_risk_level(
    trend_report: TrendReport,
    conflict_report: ConflictReport,
    timebomb_report: TimeBombReport
) -> Tuple[RiskLevel, float]:
    """
    Calculate overall risk level and score based on agent outputs.
    
    Risk scoring logic:
    - Trend concern: 0-3 → 0-30 points
    - Conflict severity: 0-3 → 0-40 points (weighted higher)
    - TimeBomb urgency: 0-3 → 0-30 points
    
    Risk levels:
    - GREEN (🟢): 0-40 points - Stable
    - YELLOW (🟡): 41-70 points - Watch closely
    - RED (🔴): 71-100 points - Critical attention needed
    
    Args:
        trend_report: TrendReport from trend agent
        conflict_report: ConflictReport from conflict agent
        timebomb_report: TimeBombReport from timebomb agent
        
    Returns:
        Tuple of (RiskLevel, risk_score)
    """
    # Calculate weighted score
    trend_score = trend_report.overall_concern * 10  # 0-30
    conflict_score = conflict_report.overall_severity * 13.33  # 0-40 (weighted higher)
    timebomb_score = timebomb_report.overall_urgency * 10  # 0-30
    
    total_score = trend_score + conflict_score + timebomb_score
    
    # Determine risk level
    if total_score >= 71:
        risk_level = RiskLevel.RED
    elif total_score >= 41:
        risk_level = RiskLevel.YELLOW
    else:
        risk_level = RiskLevel.GREEN
    
    logger.info(
        f"Risk calculation: Trend={trend_score:.1f}, Conflict={conflict_score:.1f}, "
        f"TimeBomb={timebomb_score:.1f}, Total={total_score:.1f} → {risk_level.value}"
    )
    
    return risk_level, total_score


def generate_situation(
    patient_data: PatientDataObject,
    trend_report: TrendReport,
    conflict_report: ConflictReport,
    risk_level: RiskLevel
) -> str:
    """
    Generate SBAR Situation section.
    
    Args:
        patient_data: PatientDataObject
        trend_report: TrendReport
        conflict_report: ConflictReport
        risk_level: Calculated risk level
        
    Returns:
        Situation narrative string
    """
    # Build situation narrative
    situation_parts = []
    
    # Patient demographics
    situation_parts.append(
        f"{patient_data.age}yo {patient_data.gender} in {patient_data.careunit}"
    )
    
    # Risk level
    risk_emoji = {
        RiskLevel.GREEN: "🟢",
        RiskLevel.YELLOW: "🟡",
        RiskLevel.RED: "🔴"
    }[risk_level]
    
    risk_text = {
        RiskLevel.GREEN: "stable condition",
        RiskLevel.YELLOW: "requires close monitoring",
        RiskLevel.RED: "showing signs of deterioration"
    }[risk_level]
    
    situation_parts.append(f"{risk_emoji} Patient is {risk_text}.")
    
    # Add key findings
    if trend_report.overall_concern > 0:
        situation_parts.append(trend_report.summary)
    
    if conflict_report.overall_severity > 0:
        situation_parts.append(conflict_report.summary)
    
    return " ".join(situation_parts)


def generate_background(
    patient_data: PatientDataObject,
    trend_report: TrendReport
) -> str:
    """
    Generate SBAR Background section.
    
    Args:
        patient_data: PatientDataObject
        trend_report: TrendReport
        
    Returns:
        Background narrative string
    """
    background_parts = []
    
    # Time window
    window_hours = (patient_data.window_end - patient_data.window_start).total_seconds() / 3600
    background_parts.append(
        f"Analysis based on {window_hours:.1f}-hour window "
        f"({patient_data.window_start.strftime('%H:%M')} - {patient_data.window_end.strftime('%H:%M')})."
    )
    
    # Data quality
    if patient_data.data_quality:
        background_parts.append(
            f"Data completeness: {patient_data.data_quality.completeness_score:.0%} "
            f"({patient_data.data_quality.actual_readings}/{patient_data.data_quality.total_expected_readings} readings)."
        )
        
        if patient_data.data_quality.missing_vitals:
            background_parts.append(
                f"Missing vitals: {', '.join(patient_data.data_quality.missing_vitals)}."
            )
    
    # Vital trends summary
    if trend_report.trends:
        concerning_trends = [t for t in trend_report.trends if t.concern_level > 0]
        if concerning_trends:
            trend_names = [t.vital_name for t in concerning_trends]
            background_parts.append(
                f"Concerning trends in: {', '.join(trend_names)}."
            )
    
    return " ".join(background_parts)


def generate_assessment(
    conflict_report: ConflictReport,
    trend_report: TrendReport,
    risk_level: RiskLevel
) -> str:
    """
    Generate SBAR Assessment section.
    
    Args:
        conflict_report: ConflictReport
        trend_report: TrendReport
        risk_level: Calculated risk level
        
    Returns:
        Assessment narrative string
    """
    assessment_parts = []
    
    # Overall assessment based on risk level
    if risk_level == RiskLevel.RED:
        assessment_parts.append(
            "Patient shows multiple concerning patterns indicating potential silent deterioration."
        )
    elif risk_level == RiskLevel.YELLOW:
        assessment_parts.append(
            "Patient has some concerning findings that warrant close monitoring."
        )
    else:
        assessment_parts.append(
            "Patient appears stable with no immediate concerns."
        )
    
    # Conflict patterns (most important)
    if conflict_report.conflicts:
        assessment_parts.append("\nDetected cross-signal patterns:")
        for conflict in conflict_report.conflicts:
            assessment_parts.append(
                f"• {conflict.conflict_type.value.replace('_', ' ').title()}: "
                f"{conflict.clinical_significance}"
            )
    
    # Trend details
    if trend_report.trends:
        high_concern_trends = [t for t in trend_report.trends if t.concern_level >= 2]
        if high_concern_trends:
            assessment_parts.append("\nSignificant vital trends:")
            for trend in high_concern_trends:
                assessment_parts.append(f"• {trend.reasoning}")
    
    return " ".join(assessment_parts)


def generate_recommendation(
    conflict_report: ConflictReport,
    timebomb_report: TimeBombReport,
    risk_level: RiskLevel
) -> str:
    """
    Generate SBAR Recommendation section.
    
    Args:
        conflict_report: ConflictReport
        timebomb_report: TimeBombReport
        risk_level: Calculated risk level
        
    Returns:
        Recommendation narrative string
    """
    recommendations = []
    
    # Risk-based recommendations
    if risk_level == RiskLevel.RED:
        recommendations.append("IMMEDIATE ACTIONS RECOMMENDED:")
        recommendations.append("• Bedside assessment by physician")
        recommendations.append("• Consider ICU consult if not already in ICU")
    elif risk_level == RiskLevel.YELLOW:
        recommendations.append("RECOMMENDED ACTIONS:")
        recommendations.append("• Increase monitoring frequency")
        recommendations.append("• Notify physician of concerning trends")
    else:
        recommendations.append("ROUTINE MONITORING:")
        recommendations.append("• Continue current care plan")
    
    # Conflict-specific recommendations
    if conflict_report.conflicts:
        recommendations.append("\nPattern-specific actions:")
        for conflict in conflict_report.conflicts:
            if conflict.conflict_type.value == "compensated_shock":
                recommendations.append("• Consider fluid resuscitation")
                recommendations.append("• Repeat lactate in 2 hours")
            elif conflict.conflict_type.value == "early_aki":
                recommendations.append("• Review fluid balance")
                recommendations.append("• Consider nephrology consult")
            elif conflict.conflict_type.value == "pre_respiratory_failure":
                recommendations.append("• Assess work of breathing")
                recommendations.append("• Consider ABG and chest X-ray")
            elif conflict.conflict_type.value == "hidden_sepsis":
                recommendations.append("• Review for infection source")
                recommendations.append("• Consider blood cultures and antibiotics")
    
    # Time-sensitive items
    if timebomb_report.timebombs:
        urgent_items = [tb for tb in timebomb_report.timebombs if tb.urgency >= 2]
        if urgent_items:
            recommendations.append("\nTime-sensitive items:")
            for item in urgent_items:
                recommendations.append(f"• {item.action_required}")
    
    return "\n".join(recommendations)


def generate_timeline(patient_data: PatientDataObject, trend_report: TrendReport,
                     conflict_report: ConflictReport, timebomb_report: TimeBombReport):
    """
    Generate timeline of recent events from patient data and agent reports.
    
    Args:
        patient_data: Patient data object
        trend_report: Trend analysis report
        conflict_report: Conflict detection report
        timebomb_report: Time bomb detection report
        
    Returns:
        List of timeline items with timestamp, kind, and text
    """
    timeline = []
    
    # Add agent findings
    if trend_report and trend_report.trends:
        for trend in trend_report.trends[:3]:  # Top 3 trends
            timeline.append({
                't': trend_report.timestamp.strftime('%H:%M') if hasattr(trend_report.timestamp, 'strftime') else '00:00',
                'kind': 'agent',
                'text': f"Trend Agent: {trend.vital_name} {trend.direction.value}"
            })
    
    if conflict_report and conflict_report.conflicts:
        for conflict in conflict_report.conflicts[:2]:  # Top 2 conflicts
            timeline.append({
                't': conflict_report.timestamp.strftime('%H:%M') if hasattr(conflict_report.timestamp, 'strftime') else '00:00',
                'kind': 'agent',
                'text': f"Conflict Agent: {conflict.conflict_type.value.replace('_', ' ').title()}"
            })
    
    if timebomb_report and timebomb_report.timebombs:
        for tb in timebomb_report.timebombs[:2]:  # Top 2 timebombs
            timeline.append({
                't': timebomb_report.timestamp.strftime('%H:%M') if hasattr(timebomb_report.timestamp, 'strftime') else '00:00',
                'kind': 'agent',
                'text': f"TimeBomb Agent: {tb.timebomb_type.value.replace('_', ' ').title()}"
            })
    
    # Add recent vitals (last 5)
    if patient_data.vitals:
        recent_vitals = sorted(patient_data.vitals, key=lambda v: v.charttime, reverse=True)[:5]
        for vital in recent_vitals:
            timeline.append({
                't': vital.charttime.strftime('%H:%M'),
                'kind': 'vital',
                'text': f"{vital.label}: {vital.value:.1f} {vital.unit}"
            })
    
    # Add recent labs (last 3)
    if patient_data.labs:
        recent_labs = sorted(patient_data.labs, key=lambda l: l.charttime, reverse=True)[:3]
        for lab in recent_labs:
            flag_text = f" [{lab.flag}]" if lab.flag else ""
            timeline.append({
                't': lab.charttime.strftime('%H:%M'),
                'kind': 'lab',
                'text': f"{lab.label}: {lab.value:.1f} {lab.unit}{flag_text}"
            })
    
    # Add recent medications (last 3)
    if patient_data.medications:
        recent_meds = sorted(patient_data.medications, key=lambda m: m.starttime, reverse=True)[:3]
        for med in recent_meds:
            timeline.append({
                't': med.starttime.strftime('%H:%M'),
                'kind': 'med',
                'text': f"{med.drug} {med.dose or ''} {med.route or ''}".strip()
            })
    
    # Sort by time (most recent first) and limit to 15 items
    timeline.sort(key=lambda x: x['t'], reverse=True)
    return timeline[:15]


async def coordinate(patient_data: PatientDataObject) -> SBARBrief:
    """
    Main coordinator function that orchestrates all agents and generates SBAR brief.
    
    This is the primary entry point for Layer 2.
    
    Args:
        patient_data: PatientDataObject containing patient data
        
    Returns:
        SBARBrief with complete clinical assessment
    """
    logger.info(f"Starting coordination for patient {patient_data.patient_id}")
    
    # Run all agents concurrently
    trend_report, conflict_report, timebomb_report = await run_all_agents(patient_data)
    
    # Calculate risk level and score
    risk_level, risk_score = calculate_risk_level(
        trend_report, conflict_report, timebomb_report
    )
    
    # Generate SBAR components
    situation = generate_situation(patient_data, trend_report, conflict_report, risk_level)
    background = generate_background(patient_data, trend_report)
    assessment = generate_assessment(conflict_report, trend_report, risk_level)
    recommendation = generate_recommendation(conflict_report, timebomb_report, risk_level)
    
    # Generate timeline
    timeline = generate_timeline(patient_data, trend_report, conflict_report, timebomb_report)
    
    # Calculate confidence level based on data quality
    confidence_level = patient_data.data_quality.completeness_score if patient_data.data_quality else 0.0
    
    # Create SBAR brief
    sbar_brief = SBARBrief(
        patient_id=patient_data.patient_id,
        stay_id=patient_data.stay_id,
        timestamp=datetime.now(),
        risk_level=risk_level,
        risk_score=risk_score,
        situation=situation,
        background=background,
        assessment=assessment,
        recommendation=recommendation,
        trend_report=trend_report,
        conflict_report=conflict_report,
        timebomb_report=timebomb_report,
        timeline=timeline,
        data_quality_score=confidence_level,
        confidence_level=confidence_level,
        generated_by="Bob Agent System v1.0"
    )
    
    logger.info(
        f"Coordination complete for patient {patient_data.patient_id}: "
        f"Risk={risk_level.value}, Score={risk_score:.1f}"
    )
    
    return sbar_brief


def format_sbar_for_display(sbar: SBARBrief) -> str:
    """
    Format SBAR brief for console/text display.
    
    Args:
        sbar: SBARBrief object
        
    Returns:
        Formatted string for display
    """
    emoji = sbar.get_emoji()
    
    output = []
    output.append("=" * 80)
    output.append(f"{emoji} SBAR BRIEF - Patient {sbar.patient_id}")
    output.append("=" * 80)
    output.append(f"Generated: {sbar.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
    output.append(f"Risk Level: {sbar.risk_level.value.upper()} (Score: {sbar.risk_score:.1f}/100)")
    output.append(f"Confidence: {sbar.confidence_level:.0%}")
    output.append("")
    
    output.append("SITUATION")
    output.append("-" * 80)
    output.append(sbar.situation)
    output.append("")
    
    output.append("BACKGROUND")
    output.append("-" * 80)
    output.append(sbar.background)
    output.append("")
    
    output.append("ASSESSMENT")
    output.append("-" * 80)
    output.append(sbar.assessment)
    output.append("")
    
    output.append("RECOMMENDATION")
    output.append("-" * 80)
    output.append(sbar.recommendation)
    output.append("")
    
    output.append("=" * 80)
    
    return "\n".join(output)


# Made with Bob