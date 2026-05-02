import { useState } from "react";
import SummaryCard from "../components/SummaryCard";
import { SBARBrief } from "../components";
import { AgentReasoningStream } from "../agent-reasoning";

// Mock data for the "Money View"
const mockSBAR = {
  risk: "RED" as const,
  patientId: "P-101",
  stayCount: "Day 4",
  window: "Last 6h as of 08:15",
  trend: "Progressive respiratory fatigue; rate increased from 18 to 28 over 4h.",
  conflict: "Lactate is rising (4.5) despite stable Blood Pressure, suggesting occult shock.",
  timeBomb: "High risk of intubation requirement within 120 minutes.",
  reasoning: [
    "HR: 112bpm (High > 110)",
    "SpO2: 91% (Low oxygen saturation)",
    "Lactate: 4.5 mmol/L (Rising)",
    "Patient appearing restless/combative"
  ]
};

const counts = [
  { label: "Critical Patients", value: 2 },
  { label: "Active Alerts", value: 5 },
  { label: "Pending Reviews", value: 3 },
  { label: "System Uptime", value: 99 },
];

export default function Dashboard() {
  const [showAgentStream, setShowAgentStream] = useState(false);

  return (
    <div className="flex flex-col xl:flex-row gap-4 md:gap-6 animate-in fade-in duration-700 h-full">
      
      {/* LEFT COLUMN: Overview & Stats - Responsive width management */}
      <div className="flex-1 min-w-0 space-y-4 md:space-y-6 overflow-y-auto pb-4">
        
        {/* Header Panel - Responsive padding */}
        <header className="bg-bg-panel border border-border-subtle p-4 md:p-6 rounded-xl shadow-sm">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl md:text-2xl font-bold tracking-tight text-text-primary">
                Clinical Command Center
              </h2>
              <p className="text-text-secondary text-xs md:text-sm mt-1">
                ICU Silent Deterioration Spotter • Unit North
              </p>
            </div>
            <button
              onClick={() => setShowAgentStream(!showAgentStream)}
              className="px-3 md:px-4 py-2 bg-accent hover:bg-accent/80 rounded-lg text-xs md:text-sm font-semibold transition-colors flex items-center gap-2"
            >
              {showAgentStream ? (
                <>
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
                  </svg>
                  Hide Agents
                </>
              ) : (
                <>
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                  </svg>
                  Show Agents
                </>
              )}
            </button>
          </div>
        </header>

        {/* Stats Grid - Responsive columns: 1 on mobile, 2 on tablet, 4 on desktop */}
        <section className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-3 md:gap-4">
          {counts.map((item) => (
            <SummaryCard
              key={item.label}
              label={item.label}
              value={item.value}
            />
          ))}
        </section>

        {/* Agent Reasoning Stream - Collapsible */}
        {showAgentStream && (
          <section className="animate-in fade-in slide-in-from-top duration-500">
            <AgentReasoningStream patientId="10006" />
          </section>
        )}

        {/* Placeholder for Main Data / Charts - Responsive height */}
        {!showAgentStream && (
          <div className="bg-bg-panel border border-border-subtle rounded-xl p-4 md:p-6 h-64 md:h-80 xl:h-96 flex items-center justify-center border-dashed">
            <p className="text-text-muted italic text-sm md:text-base text-center px-4">
              Vitals Trend Visualization (Coming Soon)
            </p>
          </div>
        )}
      </div>

      {/* RIGHT COLUMN: SBAR Brief - Responsive width and positioning */}
      <aside className="w-full xl:w-[420px] 2xl:w-[480px] shrink-0">
        {/* Sticky positioning only on large screens, full height on mobile */}
        <div className="xl:sticky xl:top-0 h-[600px] md:h-[700px] xl:h-[calc(100vh-8rem)]">
          <SBARBrief data={mockSBAR} />
        </div>
      </aside>

    </div>
  );
}