/**
 * Type definitions matching the FastAPI backend response models
 * Based on BE/src/api_main.py
 */

// Backend API Response Types
export interface PatientListResponse {
  patients: BackendPatientListItem[];
  total_count: number;
  timestamp: string;
}

export interface BackendPatientListItem {
  patient_id: string;
  stay_id: string;
  risk_level: string; // "green" | "yellow" | "red"
  risk_score: number;
  last_updated: string;
  careunit: string;
  age: number;
  gender: string;
  vitals?: {
    hr: number;
    sbp: number;
    dbp: number;
    map: number;
    rr: number;
    spo2: number;
    temp: number;
  };
}

export interface PatientBriefResponse {
  patient_id: string;
  stay_id: string;
  timestamp: string;
  risk_level: string;
  risk_emoji: string;
  risk_score: number;
  situation: string;
  background: string;
  assessment: string;
  recommendation: string;
  data_quality_score: number;
  confidence_level: number;
  generated_by: string;
  
  // Full detailed reports (not just summaries)
  trend_report?: TrendReportAPI;
  conflict_report?: ConflictReportAPI;
  timebomb_report?: TimeBombReportAPI;
}

// Nested report types matching backend schemas
export interface TrendReportAPI {
  patient_id: string;
  timestamp: string;
  trends: VitalTrendAPI[];
  overall_concern: number;
  summary: string;
  llm_reasoning: string;
}

export interface VitalTrendAPI {
  vital_name: string;
  direction: string; // "rising" | "falling" | "stable" | "volatile"
  slope: number;
  acceleration: number;
  concern_level: number;
  values: number[];
  timestamps: string[];
  reasoning: string;
}

export interface ConflictReportAPI {
  patient_id: string;
  timestamp: string;
  conflicts: ConflictPatternAPI[];
  overall_severity: number;
  summary: string;
  llm_reasoning: string;
}

export interface ConflictPatternAPI {
  conflict_type: string;
  severity: number;
  description: string;
  vitals_involved: string[];
  labs_involved: string[];
  evidence: Record<string, any>;
  clinical_significance: string;
}

export interface TimeBombReportAPI {
  patient_id: string;
  timestamp: string;
  timebombs: TimeBombItemAPI[];
  overall_urgency: number;
  summary: string;
}

export interface TimeBombItemAPI {
  timebomb_type: string;
  urgency: number;
  description: string;
  time_until_event?: number;
  action_required: string;
}

export interface RefreshResponse {
  success: boolean;
  message: string;
  patient_id: string;
  risk_level: string;
  risk_score: number;
}

export interface HealthCheckResponse {
  status: string;
  timestamp: string;
  version: string;
}

// API Endpoints
export const API_ENDPOINTS = {
  HEALTH: '/health',
  PATIENTS: '/patients',
  PATIENT_BRIEF: (patientId: string) => `/patients/${patientId}/brief`,
  PATIENT_REFRESH: (patientId: string) => `/patients/${patientId}/refresh`,
  PATIENT_BRIEF_FORMATTED: (patientId: string) => `/patients/${patientId}/brief/formatted`,
} as const;

// Made with Bob