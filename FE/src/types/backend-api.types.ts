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
  
  // Optional detailed reports
  trend_summary?: string;
  conflict_summary?: string;
  timebomb_summary?: string;
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