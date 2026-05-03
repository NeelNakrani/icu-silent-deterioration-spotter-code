import type { PatientSummary, PatientDetailData, VitalsUpdate, TrendDirection } from '../types/icu';
import type { 
  PatientListResponse, 
  PatientBriefResponse, 
  RefreshResponse,
  BackendPatientListItem 
} from '../types/backend-api.types';
import { apiService } from './api.service';
import { API_ENDPOINTS } from '../types/backend-api.types';

/**
 * Service to handle patient-related API calls.
 * Integrated with FastAPI backend at http://localhost:8000
 */

/**
 * Transform backend patient list item to frontend PatientSummary format
 */
function transformPatientListItem(item: BackendPatientListItem): PatientSummary {
  // Map risk level to lowercase for frontend consistency
  const riskLevel = item.risk_level.toLowerCase() as 'green' | 'yellow' | 'red';
  
  // Calculate time ago label
  const lastUpdated = new Date(item.last_updated);
  const now = new Date();
  const diffMinutes = Math.floor((now.getTime() - lastUpdated.getTime()) / 60000);
  const lastUpdatedLabel = diffMinutes < 1 ? 'just now' : 
                          diffMinutes < 60 ? `${diffMinutes}m ago` :
                          diffMinutes < 1440 ? `${Math.floor(diffMinutes / 60)}h ago` :
                          `${Math.floor(diffMinutes / 1440)}d ago`;

  // Shorten care unit name - handle full names like "Medical Intensive Care Unit"
  let careunitShort = item.careunit;
  
  // Map full ICU names to abbreviations
  if (/Medical\s+Intensive\s+Care\s+Unit/i.test(item.careunit)) {
    careunitShort = 'MICU';
  } else if (/Surgical\s+Intensive\s+Care\s+Unit/i.test(item.careunit)) {
    careunitShort = 'SICU';
  } else if (/Cardiac\s+(Vascular\s+)?Intensive\s+Care\s+Unit/i.test(item.careunit)) {
    careunitShort = 'CICU';
  } else if (/Neuro\s+Intermediate/i.test(item.careunit)) {
    careunitShort = 'NICU';
  } else if (/Trauma\s+SICU/i.test(item.careunit)) {
    careunitShort = 'TSICU';
  } else if (/Coronary\s+Care\s+Unit/i.test(item.careunit)) {
    careunitShort = 'CCU';
  } else {
    // Fallback: try to extract first word + ICU
    const match = item.careunit.match(/^(\w+)/);
    if (match) {
      careunitShort = match[1].substring(0, 3).toUpperCase() + 'ICU';
    }
  }

  return {
    patient_id: item.patient_id,
    stay_id: item.stay_id,
    risk_level: riskLevel,
    risk_score: item.risk_score,
    risk_delta: 0, // Not provided by backend, could be calculated
    last_updated: item.last_updated,
    last_updated_label: lastUpdatedLabel,
    careunit: item.careunit,
    careunit_short: careunitShort,
    age: item.age,
    gender: item.gender,
    primary: 'Unknown', // Not provided by backend
    los: '0d', // Not provided by backend
    flags: (item as any).flags || [], // Get flags from backend if available
    vitals: item.vitals ? {
      hr: Math.round(item.vitals.hr),
      sbp: Math.round(item.vitals.sbp),
      dbp: Math.round(item.vitals.dbp),
      map: Math.round(item.vitals.map),
      rr: Math.round(item.vitals.rr),
      spo2: Math.round(item.vitals.spo2),
      temp: Math.round(item.vitals.temp * 10) / 10, // Keep 1 decimal for temp
    } : {
      hr: 0,
      sbp: 0,
      dbp: 0,
      map: 0,
      rr: 0,
      spo2: 0,
      temp: 0,
    },
    trend: {},
    agent_counts: {
      trend: 0,
      conflict: 0,
      timebomb: 0,
    },
  };
}

/**
 * Build vitalsSpark data from trend report
 */
function buildVitalsSparkFromTrends(trendReport: any): Record<string, any> {
  const vitalsSpark: Record<string, any> = {};
  
  // Map vital names to spark keys
  const vitalMap: Record<string, string> = {
    'Heart Rate': 'hr',
    'Respiratory Rate': 'rr',
    'Non Invasive Blood Pressure systolic': 'map',
    'O2 saturation pulseoxymetry': 'spo2',
    'Temperature': 'temp',
    'Lactate': 'lact',
  };
  
  trendReport.trends?.forEach((trend: any) => {
    const key = vitalMap[trend.vital_name];
    if (key && trend.values && trend.values.length > 0) {
      vitalsSpark[key] = {
        values: trend.values,
        unit: getUnitForVital(trend.vital_name),
        current: trend.values[trend.values.length - 1],
        range: getNormalRangeForVital(trend.vital_name),
      };
    }
  });
  
  return vitalsSpark;
}

/**
 * Build trend directions from trend report
 */
function buildTrendDirections(trendReport: any): Record<string, TrendDirection> {
  const trends: Record<string, TrendDirection> = {};
  
  const vitalMap: Record<string, string> = {
    'Heart Rate': 'hr',
    'Respiratory Rate': 'rr',
    'Non Invasive Blood Pressure systolic': 'sbp',
    'O2 saturation pulseoxymetry': 'spo2',
    'Temperature': 'temp',
  };
  
  trendReport.trends?.forEach((trend: any) => {
    const key = vitalMap[trend.vital_name];
    if (key) {
      trends[key] = trend.direction as TrendDirection;
    }
  });
  
  return trends;
}

/**
 * Get unit for a vital sign
 */
function getUnitForVital(vitalName: string): string {
  const units: Record<string, string> = {
    'Heart Rate': 'bpm',
    'Respiratory Rate': '/min',
    'Non Invasive Blood Pressure systolic': 'mmHg',
    'O2 saturation pulseoxymetry': '%',
    'Temperature': '°C',
    'Lactate': 'mmol/L',
  };
  return units[vitalName] || '';
}

/**
 * Get normal range for a vital sign
 */
function getNormalRangeForVital(vitalName: string): string {
  const ranges: Record<string, string> = {
    'Heart Rate': '60-100',
    'Respiratory Rate': '12-20',
    'Non Invasive Blood Pressure systolic': '90-140',
    'O2 saturation pulseoxymetry': '95-100',
    'Temperature': '36.5-37.5',
    'Lactate': '0.5-2.2',
  };
  return ranges[vitalName] || '';
}

/**
 * Transform backend patient brief to frontend PatientDetailData format
 */
function transformPatientBrief(brief: PatientBriefResponse): PatientDetailData {
  const riskLevel = brief.risk_level.toLowerCase() as 'green' | 'yellow' | 'red';
  
  const lastUpdated = new Date(brief.timestamp);
  const now = new Date();
  const diffMinutes = Math.floor((now.getTime() - lastUpdated.getTime()) / 60000);
  const lastUpdatedLabel = diffMinutes < 1 ? 'just now' : 
                          diffMinutes < 60 ? `${diffMinutes}m ago` :
                          diffMinutes < 1440 ? `${Math.floor(diffMinutes / 60)}h ago` :
                          `${Math.floor(diffMinutes / 1440)}d ago`;

  return {
    patient_id: brief.patient_id,
    stay_id: brief.stay_id,
    timestamp: brief.timestamp,
    generated_by: brief.generated_by,
    risk_level: riskLevel,
    risk_score: brief.risk_score,
    risk_delta: 0,
    risk_window: '6h',
    last_updated: brief.timestamp,
    last_updated_label: lastUpdatedLabel,
    data_quality_score: brief.data_quality_score,
    confidence_level: brief.confidence_level,
    
    // SBAR sections
    situation: brief.situation,
    background: brief.background,
    assessment: brief.assessment,
    recommendation: brief.recommendation,
    
    // Patient demographics from backend
    careunit: brief.careunit || 'Unknown',
    careunit_short: brief.careunit ? (() => {
      // Map full ICU names to abbreviations
      if (/Medical\s+Intensive\s+Care\s+Unit/i.test(brief.careunit)) return 'MICU';
      if (/Surgical\s+Intensive\s+Care\s+Unit/i.test(brief.careunit)) return 'SICU';
      if (/Cardiac\s+(Vascular\s+)?Intensive\s+Care\s+Unit/i.test(brief.careunit)) return 'CICU';
      if (/Neuro\s+Intermediate/i.test(brief.careunit)) return 'NICU';
      if (/Trauma\s+SICU/i.test(brief.careunit)) return 'TSICU';
      if (/Coronary\s+Care\s+Unit/i.test(brief.careunit)) return 'CCU';
      const match = brief.careunit.match(/^(\w+)/);
      return match ? match[1].substring(0, 3).toUpperCase() + 'ICU' : 'UNK';
    })() : 'UNK',
    age: brief.age || 0,
    gender: brief.gender || 'U',
    weight: 'Unknown',
    attending: 'Unknown',
    display_name: `Patient ${brief.patient_id}`,
    primary: 'Unknown',
    los: '0d',
    flags: [],
    
    // Vitals (defaults)
    vitals: {
      hr: 0,
      sbp: 0,
      dbp: 0,
      map: 0,
      rr: 0,
      spo2: 0,
      temp: 0,
    },
    // Build vitalsSpark from trend report data
    vitalsSpark: brief.trend_report ? buildVitalsSparkFromTrends(brief.trend_report) : {},
    trend: brief.trend_report ? buildTrendDirections(brief.trend_report) : {},
    agent_counts: {
      trend: brief.trend_report?.trends?.length || 0,
      conflict: brief.conflict_report?.conflicts?.length || 0,
      timebomb: brief.timebomb_report?.timebombs?.length || 0,
    },
    
    // Agent reports (full nested objects from backend)
    trend_report: brief.trend_report ? {
      patient_id: brief.trend_report.patient_id,
      timestamp: brief.trend_report.timestamp,
      overall_concern: brief.trend_report.overall_concern,
      summary: brief.trend_report.summary,
      llm_reasoning: brief.trend_report.llm_reasoning,
      last_run_label: lastUpdatedLabel,
      confidence: brief.confidence_level,
      trends: brief.trend_report.trends.map(t => ({
        vital_name: t.vital_name,
        direction: t.direction as TrendDirection,
        slope: t.slope,
        acceleration: t.acceleration,
        concern_level: t.concern_level,
        values: t.values,
        timestamps: t.timestamps,
        reasoning: t.reasoning,
      })),
      evidence: [],
    } : {
      patient_id: brief.patient_id,
      timestamp: brief.timestamp,
      overall_concern: 0,
      summary: 'No trend analysis available',
      llm_reasoning: '',
      last_run_label: lastUpdatedLabel,
      confidence: brief.confidence_level,
      trends: [],
      evidence: [],
    },
    conflict_report: brief.conflict_report ? {
      patient_id: brief.conflict_report.patient_id,
      timestamp: brief.conflict_report.timestamp,
      overall_severity: brief.conflict_report.overall_severity,
      summary: brief.conflict_report.summary,
      llm_reasoning: brief.conflict_report.llm_reasoning,
      last_run_label: lastUpdatedLabel,
      confidence: brief.confidence_level,
      conflicts: brief.conflict_report.conflicts.map(c => ({
        conflict_type: c.conflict_type,
        severity: c.severity,
        description: c.description,
        vitals_involved: c.vitals_involved,
        labs_involved: c.labs_involved,
        evidence: Array.isArray(c.evidence) ? c.evidence : [],
        clinical_significance: c.clinical_significance,
      })),
    } : {
      patient_id: brief.patient_id,
      timestamp: brief.timestamp,
      overall_severity: 0,
      summary: 'No conflict analysis available',
      llm_reasoning: '',
      last_run_label: lastUpdatedLabel,
      confidence: brief.confidence_level,
      conflicts: [],
    },
    timebomb_report: brief.timebomb_report ? {
      patient_id: brief.timebomb_report.patient_id,
      timestamp: brief.timebomb_report.timestamp,
      overall_urgency: brief.timebomb_report.overall_urgency,
      summary: brief.timebomb_report.summary,
      llm_reasoning: '',
      last_run_label: lastUpdatedLabel,
      confidence: brief.confidence_level,
      timebombs: brief.timebomb_report.timebombs.map(tb => ({
        timebomb_type: tb.timebomb_type,
        urgency: tb.urgency,
        description: tb.description,
        time_until_event: tb.time_until_event,
        action_required: tb.action_required,
      })),
    } : {
      patient_id: brief.patient_id,
      timestamp: brief.timestamp,
      overall_urgency: 0,
      summary: 'No timebomb analysis available',
      llm_reasoning: '',
      last_run_label: lastUpdatedLabel,
      confidence: brief.confidence_level,
      timebombs: [],
    },
    
    // Data quality (defaults)
    data_quality: {
      total_expected_readings: 0,
      actual_readings: 0,
      missing_vitals: [],
      missing_labs: [],
      data_gaps_minutes: [],
      completeness_score: brief.data_quality_score,
    },
    
    // Timeline from backend - cast to proper type
    timeline: (brief.timeline || []).map(item => ({
      t: item.t,
      kind: item.kind as 'agent' | 'med' | 'note' | 'lab' | 'vital' | 'order',
      text: item.text
    })),
  };
}

export const patientService = {
  /**
   * Fetch a list of all patients for the dashboard.
   */
  async getPatients(): Promise<PatientSummary[]> {
    try {
      const response = await apiService.get<PatientListResponse>(API_ENDPOINTS.PATIENTS);
      return response.data.patients.map(transformPatientListItem);
    } catch (error) {
      console.error('Error fetching patients:', error);
      throw error;
    }
  },

  /**
   * Fetch full SBAR+ details for a specific patient.
   */
  async getPatientDetail(patientId: string): Promise<PatientDetailData> {
    try {
      const response = await apiService.get<PatientBriefResponse>(
        API_ENDPOINTS.PATIENT_BRIEF(patientId)
      );
      return transformPatientBrief(response.data);
    } catch (error) {
      console.error(`Error fetching patient detail for ${patientId}:`, error);
      throw error;
    }
  },

  /**
   * Refresh agent analysis (coordinator synthesis).
   */
  async refreshAnalysis(patientId: string): Promise<RefreshResponse> {
    try {
      const response = await apiService.post<RefreshResponse>(
        API_ENDPOINTS.PATIENT_REFRESH(patientId)
      );
      return response.data;
    } catch (error) {
      console.error(`Error refreshing analysis for ${patientId}:`, error);
      throw error;
    }
  },

  /**
   * Simulate a WebSocket subscription for real-time vitals.
   * In a real app, this would use new WebSocket() or a library like socket.io.
   */
  subscribeToVitals(patientId: string, onUpdate: (vitals: VitalsUpdate) => void): () => void {
    console.log(`Subscribing to live vitals for ${patientId}`);
    
    // Simulate incoming data every 2 seconds
    const interval = setInterval(() => {
      const update = {
        hr: Math.floor(70 + Math.random() * 20),
        map: Math.floor(80 + Math.random() * 15),
        spo2: Math.floor(94 + Math.random() * 5),
        rr: Math.floor(14 + Math.random() * 6),
        timestamp: new Date().toISOString(),
      };
      onUpdate(update);
    }, 2000);

    // Return unsubscribe function
    return () => {
      console.log(`Unsubscribing from vitals for ${patientId}`);
      clearInterval(interval);
    };
  }
};

// Made with Bob
