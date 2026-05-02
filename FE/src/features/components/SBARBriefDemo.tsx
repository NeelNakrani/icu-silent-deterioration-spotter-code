/**
 * SBARBriefDemo - Demo component showing the SBARBrief in action
 * This can be integrated into the Dashboard for testing
 */

import SBARBrief from './SBARBrief';
import type { SBARBrief as SBARBriefType } from '../../types/sbar.types';

const mockData: SBARBriefType = {
  risk: "RED",
  patientId: "P-101",
  stayCount: "Day 4",
  window: "Last 6h as of 08:15",
  trend: "Progressive respiratory fatigue noted; respiratory rate increased from 18 to 28 over 4 hours.",
  conflict: "Lactate is rising (2.1 → 4.5 mmol/L) despite normalized Blood Pressure, suggesting occult shock.",
  timeBomb: "High risk of intubation requirement within 120 minutes if current trend persists.",
  reasoning: [
    "HR: 112 bpm (High Heart Rate > 110)",
    "SpO2: 91% on 4L O2 (Low oxygen saturation)",
    "Lactate: 4.5 mmol/L (Elevated, normal < 2.0)",
    "Respiratory Rate: 28 breaths/min (Tachypnea, normal 12-20)",
    "Patient appearing restless and anxious",
    "Blood Pressure: 118/76 mmHg (Normalized but misleading)"
  ]
};

export default function SBARBriefDemo() {
  return (
    <div className="h-screen p-6 bg-bg-main">
      <div className="max-w-2xl mx-auto h-full">
        <div className="mb-4">
          <h1 className="text-2xl font-bold text-text-primary mb-2">
            ICU Silent Deterioration Spotter
          </h1>
          <p className="text-text-secondary text-sm">
            Right Panel: "The Money View" — Patient Health Police Report
          </p>
        </div>
        <div className="h-[calc(100%-5rem)]">
          <SBARBrief data={mockData} />
        </div>
      </div>
    </div>
  );
}

// Made with Bob
