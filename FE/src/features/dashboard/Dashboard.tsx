import SummaryCard from "../components/SummaryCard";
import { SBARBrief } from "../components";

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
  return (
    <div className="flex flex-col xl:flex-row gap-4 md:gap-6 animate-in fade-in duration-700 h-full">
      
      {/* LEFT COLUMN: Overview & Stats - Responsive width management */}
      <div className="flex-1 min-w-0 space-y-4 md:space-y-6 overflow-y-auto pb-4">
        
        {/* Header Panel - Responsive padding */}
        <header className="bg-bg-panel border border-border-subtle p-4 md:p-6 rounded-xl shadow-sm">
          <h2 className="text-xl md:text-2xl font-bold tracking-tight text-text-primary">
            Clinical Command Center
          </h2>
          <p className="text-text-secondary text-xs md:text-sm mt-1">
            ICU Silent Deterioration Spotter • Unit North
          </p>
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

        {/* Placeholder for Main Data / Charts - Responsive height */}
        <div className="bg-bg-panel border border-border-subtle rounded-xl p-4 md:p-6 h-64 md:h-80 xl:h-96 flex items-center justify-center border-dashed">
          <p className="text-text-muted italic text-sm md:text-base text-center px-4">
            Vitals Trend Visualization (Coming Soon)
          </p>
        </div>
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