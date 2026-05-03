/**
 * SBAR Brief Types
 * Structured data for the "Money View" Right Panel
 */

export type RiskLevel = 'RED' | 'YELLOW' | 'GREEN';

export interface SBARBrief {
  risk: RiskLevel;
  patientId: string;
  stayCount: string;
  window: string;
  trend: string;
  conflict: string;
  timeBomb: string;
  reasoning: string[];
  aiInsight?: string;  // AI-generated clinical insight from IBM watsonx.ai
}

export interface SBARBriefProps {
  data: SBARBrief;
  onGenerateAIInsight?: () => void;
  isGeneratingAI?: boolean;
}

// Made with Bob
