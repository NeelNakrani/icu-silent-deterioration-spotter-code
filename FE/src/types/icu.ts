export type RiskLevel = 'green' | 'yellow' | 'red';
export type TrendDirection = 'rising' | 'falling' | 'stable' | 'volatile';

export interface Vitals {
  hr: number;
  sbp: number;
  dbp: number;
  map: number;
  rr: number;
  spo2: number;
  temp: number;
}

export interface AgentCounts {
  trend: number;
  conflict: number;
  timebomb: number;
}

export interface PatientSummary {
  patient_id: string;
  stay_id: string;
  risk_level: RiskLevel;
  risk_score: number;
  risk_delta: number;
  last_updated: string;
  last_updated_label: string;
  careunit: string;
  careunit_short: string;
  age: number;
  gender: string;
  primary: string;
  los: string;
  flags: string[];
  vitals: Vitals;
  trend: Record<string, TrendDirection>;
  agent_counts: AgentCounts;
}

export interface VitalSpark {
  values: number[];
  unit: string;
  current: number;
  range: string;
}

export interface Trend {
  vital_name: string;
  direction: TrendDirection;
  slope: number;
  acceleration: number;
  concern_level: number;
  values: number[];
  timestamps: string[];
  reasoning: string;
}

export interface Evidence {
  t: string;
  k: string;
  v: string | number;
}

export interface TrendReport {
  patient_id: string;
  timestamp: string;
  overall_concern: number;
  summary: string;
  llm_reasoning: string;
  last_run_label: string;
  confidence: number;
  trends: Trend[];
  evidence: Evidence[];
}

export interface Conflict {
  conflict_type: string;
  severity: number;
  description: string;
  vitals_involved: string[];
  labs_involved: string[];
  clinical_significance: string;
  evidence: Evidence[];
}

export interface ConflictReport {
  patient_id: string;
  timestamp: string;
  overall_severity: number;
  summary: string;
  llm_reasoning: string;
  last_run_label: string;
  confidence: number;
  conflicts: Conflict[];
}

export interface TimeBomb {
  timebomb_type: string;
  urgency: number;
  description: string;
  time_until_event: number;
  action_required: string;
}

export interface TimeBombReport {
  patient_id: string;
  timestamp: string;
  overall_urgency: number;
  summary: string;
  llm_reasoning: string;
  last_run_label: string;
  confidence: number;
  timebombs: TimeBomb[];
}

export interface DataQuality {
  total_expected_readings: number;
  actual_readings: number;
  missing_vitals: string[];
  missing_labs: string[];
  data_gaps_minutes: number[];
  completeness_score: number;
}

export interface TimelineItem {
  t: string;
  kind: 'agent' | 'med' | 'note' | 'lab' | 'vital' | 'order';
  text: string;
}

export interface PatientDetailData extends PatientSummary {
  timestamp: string;
  generated_by: string;
  risk_window: string;
  data_quality_score: number;
  confidence_level: number;
  weight: string;
  attending: string;
  display_name: string;
  situation: string;
  background: string;
  assessment: string;
  recommendation: string;
  vitalsSpark: Record<string, VitalSpark>;
  trend_report: TrendReport;
  conflict_report: ConflictReport;
  timebomb_report: TimeBombReport;
  data_quality: DataQuality;
  timeline: TimelineItem[];
}

export interface VitalsUpdate {
  hr: number;
  map: number;
  spo2: number;
  rr: number;
  timestamp: string;
}

export type TweakValue = string | number | boolean;
export interface TweakEdits {
  [key: string]: TweakValue;
}
