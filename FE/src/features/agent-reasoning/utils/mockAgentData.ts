// Mock Agent Data for Development and Demo

import type { TrendReport, ConflictReport, TimeBombReport } from '../../../types/agent-outputs.types';
import type { AgentId } from '../types/agent-stream.types';

// Mock Reasoning Chunks for Each Agent
export const MOCK_TREND_REASONING = [
  "Analyzing vital signs over 6-hour window...",
  "Heart Rate: Detected upward trend from 85 to 98 bpm",
  "Slope calculation: +2.5 bpm/hour",
  "Acceleration detected: +0.8 bpm/hour² (early vs late window)",
  "Respiratory Rate: Rising from 18 to 28 breaths/min",
  "SpO2: Declining from 96% to 91%",
  "Concern Level: MODERATE (2/3)",
  "Reasoning: Progressive respiratory fatigue pattern detected",
  "✓ Trend analysis complete"
];

export const MOCK_CONFLICT_REASONING = [
  "Cross-referencing vitals with lab values...",
  "Blood Pressure: 120/80 mmHg (NORMAL range)",
  "Heart Rate: 112 bpm (ELEVATED)",
  "Lactate: 4.5 mmol/L (RISING from 2.1)",
  "Pattern detected: Compensated Shock",
  "Evidence: Normal BP masking elevated lactate + tachycardia",
  "Clinical Significance: Early shock state requiring intervention",
  "Severity: MODERATE (2/3)",
  "✓ Conflict analysis complete"
];

export const MOCK_TIMEBOMB_REASONING = [
  "Scanning for time-sensitive risks...",
  "Pending Lab: Critical lactate result (45 minutes overdue)",
  "Medication Gap: PRN sedation not administered (2 hours)",
  "Missing Order: No respiratory therapy consult ordered",
  "Risk Assessment: High probability of intubation within 120 min",
  "Urgency Level: HIGH (2/3)",
  "Action Required: Immediate follow-up on pending lactate",
  "✓ Time bomb scan complete"
];

export const MOCK_COORDINATOR_REASONING = [
  "Synthesizing multi-agent findings...",
  "Trend Agent: Respiratory fatigue progression confirmed",
  "Conflict Agent: Compensated shock pattern identified",
  "Time Bomb Agent: Critical intervention window detected",
  "Overall Risk: RED (High priority)",
  "Recommended Actions:",
  "  1. Follow up on pending lactate immediately",
  "  2. Consider early respiratory support",
  "  3. Monitor for decompensation signs",
  "✓ Coordination complete - Alert generated"
];

// Get reasoning chunks by agent ID
export function getMockReasoningChunks(agentId: AgentId): string[] {
  switch (agentId) {
    case 'trend':
      return MOCK_TREND_REASONING;
    case 'lab-conflict':
      return MOCK_CONFLICT_REASONING;
    case 'timebomb':
      return MOCK_TIMEBOMB_REASONING;
    case 'coordinator':
      return MOCK_COORDINATOR_REASONING;
    default:
      return [];
  }
}

// Get mock result data by agent ID
export function getMockResult(agentId: AgentId, patientId: string): TrendReport | ConflictReport | TimeBombReport | null {
  const timestamp = new Date().toISOString();
  
  if (agentId === 'trend') {
    return {
      patient_id: patientId,
      timestamp,
      trends: [
        {
          vital_name: "Heart Rate",
          direction: "rising" as const,
          slope: 2.5,
          acceleration: 0.8,
          concern_level: 2,
          values: [85, 88, 92, 95, 98],
          timestamps: [
            new Date(Date.now() - 5 * 60 * 60 * 1000).toISOString(),
            new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString(),
            new Date(Date.now() - 3 * 60 * 60 * 1000).toISOString(),
            new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
            new Date(Date.now() - 1 * 60 * 60 * 1000).toISOString(),
          ],
          reasoning: "Steady upward trend suggesting physiological stress"
        },
        {
          vital_name: "Respiratory Rate",
          direction: "rising" as const,
          slope: 1.7,
          acceleration: 0.5,
          concern_level: 2,
          values: [18, 20, 23, 26, 28],
          timestamps: [
            new Date(Date.now() - 5 * 60 * 60 * 1000).toISOString(),
            new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString(),
            new Date(Date.now() - 3 * 60 * 60 * 1000).toISOString(),
            new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
            new Date(Date.now() - 1 * 60 * 60 * 1000).toISOString(),
          ],
          reasoning: "Progressive respiratory fatigue pattern"
        }
      ],
      overall_concern: 2,
      summary: "Multiple concerning upward trends in HR and RR",
      llm_reasoning: MOCK_TREND_REASONING.join('\n')
    } as TrendReport;
  }
  
  if (agentId === 'lab-conflict') {
    return {
      patient_id: patientId,
      timestamp,
      conflicts: [
        {
          conflict_type: "compensated_shock" as const,
          severity: 2,
          description: "Normal BP with elevated HR and rising lactate",
          vitals_involved: ["Heart Rate", "Blood Pressure"],
          labs_involved: ["Lactate"],
          evidence: {
            bp: "120/80",
            hr: 112,
            lactate: 4.5,
            lactate_trend: "rising"
          },
          clinical_significance: "Suggests early compensated shock requiring intervention"
        }
      ],
      overall_severity: 2,
      summary: "Detected compensated shock pattern",
      llm_reasoning: MOCK_CONFLICT_REASONING.join('\n')
    } as ConflictReport;
  }
  
  if (agentId === 'timebomb') {
    return {
      patient_id: patientId,
      timestamp,
      timebombs: [
        {
          timebomb_type: "pending_lab" as const,
          urgency: 2,
          description: "Critical lactate pending for 45 minutes",
          time_until_event: 15,
          action_required: "Follow up on pending lactate result immediately"
        },
        {
          timebomb_type: "prn_gap" as const,
          urgency: 1,
          description: "PRN sedation not administered for 2 hours",
          time_until_event: null,
          action_required: "Assess need for PRN medication"
        }
      ],
      overall_urgency: 2,
      summary: "2 pending labs requiring attention"
    } as TimeBombReport;
  }
  
  return null;
}

// Simulate streaming delay (milliseconds between chunks)
export const STREAM_DELAY_MS = 400;

// Delay utility for simulating async streaming
export const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

// Made with Bob
