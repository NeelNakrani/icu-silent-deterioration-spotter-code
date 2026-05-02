import type { PatientSummary, PatientDetailData, VitalsUpdate } from '../types/icu';
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

  // Shorten care unit name
  const careunitShort = item.careunit.replace(/^(Medical|Surgical|Cardiac|Neuro|Trauma)\s+ICU$/i, (_, type) => 
    type.substring(0, 3).toUpperCase()
  );

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
    flags: [], // Not provided by backend
    vitals: {
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
    
    // Patient demographics (defaults, not provided by backend)
    careunit: 'Unknown',
    careunit_short: 'UNK',
    age: 0,
    gender: 'U',
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
    vitalsSpark: {},
    trend: {},
    agent_counts: {
      trend: 0,
      conflict: 0,
      timebomb: 0,
    },
    
    // Agent reports (parsed from summaries if available)
    trend_report: {
      patient_id: brief.patient_id,
      timestamp: brief.timestamp,
      overall_concern: 0,
      summary: brief.trend_summary || 'No trend analysis available',
      llm_reasoning: brief.trend_summary || '',
      last_run_label: lastUpdatedLabel,
      confidence: brief.confidence_level,
      trends: [],
      evidence: [],
    },
    conflict_report: {
      patient_id: brief.patient_id,
      timestamp: brief.timestamp,
      overall_severity: 0,
      summary: brief.conflict_summary || 'No conflict analysis available',
      llm_reasoning: brief.conflict_summary || '',
      last_run_label: lastUpdatedLabel,
      confidence: brief.confidence_level,
      conflicts: [],
    },
    timebomb_report: {
      patient_id: brief.patient_id,
      timestamp: brief.timestamp,
      overall_urgency: 0,
      summary: brief.timebomb_summary || 'No timebomb analysis available',
      llm_reasoning: brief.timebomb_summary || '',
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
    
    // Timeline (empty for now)
    timeline: [],
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
