"""
Module: schemas.py
Purpose: All dataclasses and Pydantic models for the ICU Silent Deterioration Spotter
Layer: Support

Part of ICU Silent Deterioration Spotter
Hackathon: IBM Bob Challenge 2026

This module defines all data structures used throughout the backend system.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum


# ============================================================================
# Enums
# ============================================================================

class RiskLevel(str, Enum):
    """Risk level classification."""
    GREEN = "green"      # 🟢 Stable
    YELLOW = "yellow"    # 🟡 Watch
    RED = "red"          # 🔴 Critical


class VitalType(str, Enum):
    """Types of vital signs."""
    HEART_RATE = "Heart Rate"
    RESPIRATORY_RATE = "Respiratory Rate"
    SYSTOLIC_BP = "Non Invasive Blood Pressure systolic"
    DIASTOLIC_BP = "Non Invasive Blood Pressure diastolic"
    SPO2 = "O2 saturation pulseoxymetry"
    TEMPERATURE = "Temperature"
    MAP = "Mean Arterial Pressure"


class LabType(str, Enum):
    """Types of lab values."""
    CREATININE = "Creatinine"
    LACTATE = "Lactate"
    WBC = "White Blood Cells"
    HEMOGLOBIN = "Hemoglobin"
    PLATELETS = "Platelets"
    POTASSIUM = "Potassium"
    SODIUM = "Sodium"


class TrendDirection(str, Enum):
    """Direction of trend."""
    RISING = "rising"
    FALLING = "falling"
    STABLE = "stable"
    VOLATILE = "volatile"


class ConflictType(str, Enum):
    """Types of cross-signal conflicts."""
    COMPENSATED_SHOCK = "compensated_shock"
    EARLY_AKI = "early_aki"
    PRE_RESPIRATORY_FAILURE = "pre_respiratory_failure"
    HIDDEN_SEPSIS = "hidden_sepsis"


class TimeBombType(str, Enum):
    """Types of time bomb risks."""
    PENDING_LAB = "pending_lab"
    MEDICATION_DUE = "medication_due"
    PRN_GAP = "prn_gap"
    MISSING_ORDER = "missing_order"


# ============================================================================
# Layer 0 - Raw Data Components
# ============================================================================

@dataclass
class VitalReading:
    """Single vital sign reading."""
    charttime: datetime
    label: str
    value: float
    unit: str
    itemid: int
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'charttime': self.charttime.isoformat(),
            'label': self.label,
            'value': self.value,
            'unit': self.unit,
            'itemid': self.itemid
        }


@dataclass
class LabReading:
    """Single lab result."""
    charttime: datetime
    label: str
    value: float
    unit: str
    itemid: int
    flag: Optional[str] = None  # 'abnormal', 'critical', etc.
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'charttime': self.charttime.isoformat(),
            'label': self.label,
            'value': self.value,
            'unit': self.unit,
            'itemid': self.itemid,
            'flag': self.flag
        }


@dataclass
class OutputReading:
    """Urine output or other fluid output."""
    charttime: datetime
    value: float
    unit: str
    itemid: int
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'charttime': self.charttime.isoformat(),
            'value': self.value,
            'unit': self.unit,
            'itemid': self.itemid
        }


@dataclass
class MedRecord:
    """Medication record."""
    starttime: datetime
    stoptime: Optional[datetime]
    drug: str
    dose: Optional[str]
    route: Optional[str]
    frequency: Optional[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'starttime': self.starttime.isoformat(),
            'stoptime': self.stoptime.isoformat() if self.stoptime else None,
            'drug': self.drug,
            'dose': self.dose,
            'route': self.route,
            'frequency': self.frequency
        }


@dataclass
class PendingLab:
    """Lab order that hasn't been resulted yet."""
    ordertime: datetime
    label: str
    priority: str
    expected_time: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'ordertime': self.ordertime.isoformat(),
            'label': self.label,
            'priority': self.priority,
            'expected_time': self.expected_time.isoformat() if self.expected_time else None
        }


@dataclass
class DataQuality:
    """Data quality metrics for a patient window."""
    total_expected_readings: int
    actual_readings: int
    missing_vitals: List[str] = field(default_factory=list)
    missing_labs: List[str] = field(default_factory=list)
    data_gaps_minutes: List[int] = field(default_factory=list)
    completeness_score: float = 0.0
    
    def calculate_completeness(self) -> None:
        """Calculate completeness score (0-1)."""
        if self.total_expected_readings > 0:
            self.completeness_score = self.actual_readings / self.total_expected_readings
        else:
            self.completeness_score = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'total_expected_readings': self.total_expected_readings,
            'actual_readings': self.actual_readings,
            'missing_vitals': self.missing_vitals,
            'missing_labs': self.missing_labs,
            'data_gaps_minutes': self.data_gaps_minutes,
            'completeness_score': self.completeness_score
        }


@dataclass
class PatientDataObject:
    """
    Complete patient data object for a time window.
    This is the input to all Layer 1 agents.
    """
    patient_id: str
    stay_id: str
    window_start: datetime
    window_end: datetime
    
    # Demographics
    gender: str
    age: int
    careunit: str
    
    # Time series data
    vitals: List[VitalReading] = field(default_factory=list)
    labs: List[LabReading] = field(default_factory=list)
    urine_output: List[OutputReading] = field(default_factory=list)
    medications: List[MedRecord] = field(default_factory=list)
    pending_labs: List[PendingLab] = field(default_factory=list)
    
    # Metadata
    data_quality: Optional[DataQuality] = None
    intime: Optional[datetime] = None
    outtime: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'patient_id': self.patient_id,
            'stay_id': self.stay_id,
            'window_start': self.window_start.isoformat(),
            'window_end': self.window_end.isoformat(),
            'gender': self.gender,
            'age': self.age,
            'careunit': self.careunit,
            'vitals': [v.to_dict() for v in self.vitals],
            'labs': [l.to_dict() for l in self.labs],
            'urine_output': [u.to_dict() for u in self.urine_output],
            'medications': [m.to_dict() for m in self.medications],
            'pending_labs': [p.to_dict() for p in self.pending_labs],
            'data_quality': self.data_quality.to_dict() if self.data_quality else None,
            'intime': self.intime.isoformat() if self.intime else None,
            'outtime': self.outtime.isoformat() if self.outtime else None
        }


# ============================================================================
# Layer 1 - Agent Outputs
# ============================================================================

@dataclass
class VitalTrend:
    """Trend analysis for a single vital sign."""
    vital_name: str
    direction: TrendDirection
    slope: float  # Rate of change per hour
    acceleration: float  # Change in slope (early vs late window)
    concern_level: int  # 0-3 (0=none, 1=mild, 2=moderate, 3=severe)
    values: List[float] = field(default_factory=list)
    timestamps: List[datetime] = field(default_factory=list)
    reasoning: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'vital_name': self.vital_name,
            'direction': self.direction.value,
            'slope': self.slope,
            'acceleration': self.acceleration,
            'concern_level': self.concern_level,
            'values': self.values,
            'timestamps': [t.isoformat() for t in self.timestamps],
            'reasoning': self.reasoning
        }


@dataclass
class TrendReport:
    """Output from Trend Agent."""
    patient_id: str
    timestamp: datetime
    trends: List[VitalTrend] = field(default_factory=list)
    overall_concern: int = 0  # 0-3
    summary: str = ""
    llm_reasoning: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'patient_id': self.patient_id,
            'timestamp': self.timestamp.isoformat(),
            'trends': [t.to_dict() for t in self.trends],
            'overall_concern': self.overall_concern,
            'summary': self.summary,
            'llm_reasoning': self.llm_reasoning
        }


@dataclass
class ConflictPattern:
    """A detected cross-signal conflict pattern."""
    conflict_type: ConflictType
    severity: int  # 0-3
    description: str
    vitals_involved: List[str] = field(default_factory=list)
    labs_involved: List[str] = field(default_factory=list)
    evidence: Dict[str, Any] = field(default_factory=dict)
    clinical_significance: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'conflict_type': self.conflict_type.value,
            'severity': self.severity,
            'description': self.description,
            'vitals_involved': self.vitals_involved,
            'labs_involved': self.labs_involved,
            'evidence': self.evidence,
            'clinical_significance': self.clinical_significance
        }


@dataclass
class ConflictReport:
    """Output from Lab-Vitals Conflict Agent."""
    patient_id: str
    timestamp: datetime
    conflicts: List[ConflictPattern] = field(default_factory=list)
    overall_severity: int = 0  # 0-3
    summary: str = ""
    llm_reasoning: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'patient_id': self.patient_id,
            'timestamp': self.timestamp.isoformat(),
            'conflicts': [c.to_dict() for c in self.conflicts],
            'overall_severity': self.overall_severity,
            'summary': self.summary,
            'llm_reasoning': self.llm_reasoning
        }


@dataclass
class TimeBombItem:
    """A single time bomb risk item."""
    timebomb_type: TimeBombType
    urgency: int  # 0-3 (0=low, 3=critical)
    description: str
    time_until_event: Optional[int] = None  # Minutes
    action_required: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'timebomb_type': self.timebomb_type.value,
            'urgency': self.urgency,
            'description': self.description,
            'time_until_event': self.time_until_event,
            'action_required': self.action_required
        }


@dataclass
class TimeBombReport:
    """Output from Time Bomb Observer Agent."""
    patient_id: str
    timestamp: datetime
    timebombs: List[TimeBombItem] = field(default_factory=list)
    overall_urgency: int = 0  # 0-3
    summary: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'patient_id': self.patient_id,
            'timestamp': self.timestamp.isoformat(),
            'timebombs': [t.to_dict() for t in self.timebombs],
            'overall_urgency': self.overall_urgency,
            'summary': self.summary
        }


# ============================================================================
# Layer 2 - Coordinator Output
# ============================================================================

@dataclass
class SBARBrief:
    """
    Final SBAR+ brief synthesized by the Coordinator.
    This is the output presented to clinicians.
    """
    patient_id: str
    stay_id: str
    timestamp: datetime
    
    # Risk assessment
    risk_level: RiskLevel
    risk_score: float  # 0-100
    
    # SBAR components
    situation: str  # Current state
    background: str  # Relevant history
    assessment: str  # Clinical interpretation
    recommendation: str  # Suggested actions
    
    # Agent reports (for transparency)
    trend_report: Optional[TrendReport] = None
    conflict_report: Optional[ConflictReport] = None
    timebomb_report: Optional[TimeBombReport] = None
    
    # Metadata
    data_quality_score: float = 0.0
    confidence_level: float = 0.0
    generated_by: str = "Bob Agent System"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'patient_id': self.patient_id,
            'stay_id': self.stay_id,
            'timestamp': self.timestamp.isoformat(),
            'risk_level': self.risk_level.value,
            'risk_score': self.risk_score,
            'situation': self.situation,
            'background': self.background,
            'assessment': self.assessment,
            'recommendation': self.recommendation,
            'trend_report': self.trend_report.to_dict() if self.trend_report else None,
            'conflict_report': self.conflict_report.to_dict() if self.conflict_report else None,
            'timebomb_report': self.timebomb_report.to_dict() if self.timebomb_report else None,
            'data_quality_score': self.data_quality_score,
            'confidence_level': self.confidence_level,
            'generated_by': self.generated_by
        }
    
    def get_emoji(self) -> str:
        """Get emoji representation of risk level."""
        emoji_map = {
            RiskLevel.GREEN: "🟢",
            RiskLevel.YELLOW: "🟡",
            RiskLevel.RED: "🔴"
        }
        return emoji_map.get(self.risk_level, "⚪")


# ============================================================================
# API Response Models
# ============================================================================

@dataclass
class PatientListItem:
    """Patient list item for API response."""
    patient_id: str
    stay_id: str
    risk_level: RiskLevel
    risk_score: float
    last_updated: datetime
    careunit: str
    age: int
    gender: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'patient_id': self.patient_id,
            'stay_id': self.stay_id,
            'risk_level': self.risk_level.value,
            'risk_emoji': SBARBrief(
                patient_id=self.patient_id,
                stay_id=self.stay_id,
                timestamp=self.last_updated,
                risk_level=self.risk_level,
                risk_score=self.risk_score,
                situation="", background="", assessment="", recommendation=""
            ).get_emoji(),
            'risk_score': self.risk_score,
            'last_updated': self.last_updated.isoformat(),
            'careunit': self.careunit,
            'age': self.age,
            'gender': self.gender
        }


@dataclass
class HealthCheckResponse:
    """Health check API response."""
    status: str
    timestamp: datetime
    version: str = "1.0.0"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'status': self.status,
            'timestamp': self.timestamp.isoformat(),
            'version': self.version
        }

# Made with Bob
