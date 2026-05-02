// Shared concern/severity levels (0-3)
export type SeverityLevel = 0 | 1 | 2 | 3;

// --- Vital Trend Schema ---
export interface VitalTrend {
  vital_name: string;
  direction: 'rising' | 'falling' | 'stable' | 'volatile';
  slope: number;
  acceleration: number;
  concern_level: SeverityLevel;
  values?: number[];
  timestamps?: string[]; // ISO Date strings
  reasoning?: string;
}

export interface TrendReport {
  patient_id: string;
  timestamp: string;
  trends: VitalTrend[];
  overall_concern: SeverityLevel;
  summary: string;
  llm_reasoning?: string;
}

// --- Conflict Pattern Schema ---
export type ConflictType = 
  | 'compensated_shock' 
  | 'early_aki' 
  | 'pre_respiratory_failure' 
  | 'hidden_sepsis';

export interface ConflictPattern {
  conflict_type: ConflictType;
  severity: SeverityLevel;
  description: string;
  vitals_involved?: string[];
  labs_involved?: string[];
  evidence?: Record<string, unknown>;
  clinical_significance?: string;
}

export interface ConflictReport {
  patient_id: string;
  timestamp: string;
  conflicts: ConflictPattern[];
  overall_severity: SeverityLevel;
  summary: string;
  llm_reasoning?: string;
}

// --- Time Bomb Schema ---
export type TimeBombType = 
  | 'pending_lab' 
  | 'medication_due' 
  | 'prn_gap' 
  | 'missing_order';

export interface TimeBombItem {
  timebomb_type: TimeBombType;
  urgency: SeverityLevel;
  description: string;
  time_until_event: number | null;
  action_required?: string;
}

export interface TimeBombReport {
  patient_id: string;
  timestamp: string;
  timebombs: TimeBombItem[];
  overall_urgency: SeverityLevel;
  summary: string;
}