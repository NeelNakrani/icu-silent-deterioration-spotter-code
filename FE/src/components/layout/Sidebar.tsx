import { useState, useMemo } from "react";

type RiskLevel = "RED" | "YELLOW" | "GREEN";

interface Patient {
  id: string;
  name: string;
  bed: string;
  risk: RiskLevel;
  lastUpdate: string;
  alerts: string[];
}

export default function Sidebar() {
  const [selectedId, setSelectedId] = useState<string | null>("101");
  const [loading] = useState(false);

  const [patients] = useState<Patient[]>([
    { id: "P-105", name: "Sarah Jenkins", bed: "04", risk: "YELLOW", lastUpdate: "2m ago", alerts: ["SpO2 Drop"] },
    { id: "P-101", name: "John Doe", bed: "01", risk: "RED", lastUpdate: "Just now", alerts: ["Tachycardia", "BP Labile"] },
    { id: "P-103", name: "Robert Kane", bed: "12", risk: "GREEN", lastUpdate: "15m ago", alerts: [] },
    { id: "P-102", name: "Jane Smith", bed: "02", risk: "RED", lastUpdate: "1m ago", alerts: ["Sepsis Suspected"] },
  ]);

  const sortedPatients = useMemo(() => {
    const riskOrder: Record<RiskLevel, number> = { RED: 0, YELLOW: 1, GREEN: 2 };
    return [...patients].sort((a, b) => riskOrder[a.risk] - riskOrder[b.risk]);
  }, [patients]);

  return (
    <aside className="w-80 bg-bg-panel border-r border-border-subtle flex flex-col h-screen shrink-0 shadow-2xl">
      {/* HEADER: Focus on System Integrity */}
      <div className="p-6 pb-4">
        <div className="flex items-center justify-between mb-1">
          <h2 className="font-bold text-xs tracking-[0.2em] text-text-secondary uppercase">
            Unit: ICU-North
          </h2>
          <div className="flex items-center gap-1.5">
            <span className="h-1.5 w-1.5 rounded-full bg-success"></span>
            <span className="text-[10px] font-bold text-success uppercase">Live</span>
          </div>
        </div>
        <h1 className="text-xl font-black text-text-primary tracking-tight">
          COHORT <span className="text-text-muted font-light">ANALYSIS</span>
        </h1>
      </div>

      {/* FILTER TABS: Quick triage */}
      <div className="flex px-6 gap-4 border-b border-border-subtle pb-4">
         <button className="text-[10px] font-bold text-accent border-b border-accent pb-1">ALL ({patients.length})</button>
         <button className="text-[10px] font-bold text-text-muted hover:text-critical transition-colors">CRITICAL (2)</button>
      </div>

      {/* PATIENT LIST */}
      <div className="flex-1 overflow-y-auto px-3 py-4 space-y-2 custom-scrollbar">
        {loading ? (
           /* Loading State */
           <div className="space-y-3 px-3">
              {[1, 2, 3, 4].map(i => (
                <div key={i} className="h-20 bg-bg-elevated/50 animate-pulse rounded-xl" />
              ))}
           </div>
        ) : (
          sortedPatients.map((patient) => {
            const isSelected = selectedId === patient.id;
            const riskColors = {
              RED: "border-l-critical bg-critical/5 text-critical",
              YELLOW: "border-l-warning bg-warning/5 text-warning",
              GREEN: "border-l-success bg-success/5 text-success",
            };

            return (
              <button
                key={patient.id}
                onClick={() => setSelectedId(patient.id)}
                className={`w-full text-left rounded-xl border-l-4 transition-all duration-300 relative group
                  ${isSelected ? 'bg-bg-elevated ring-1 ring-border-subtle' : 'hover:bg-bg-elevated/40'}
                  ${riskColors[patient.risk]}
                `}
              >
                <div className="p-4">
                  <div className="flex justify-between items-center mb-2">
                    <div className="flex items-center gap-2">
                      <span className="text-lg font-black font-mono">
                        {patient.bed}
                      </span>
                      <span className="text-[10px] font-bold text-text-muted px-2 py-0.5 bg-bg-main rounded uppercase">
                        {patient.id}
                      </span>
                    </div>
                    <span className="text-[10px] font-medium text-text-muted italic">
                      {patient.lastUpdate}
                    </span>
                  </div>

                  <div className="text-sm font-bold text-text-primary mb-1">
                    {patient.name}
                  </div>

                  {/* ALERTS: The "Why" behind the risk */}
                  <div className="flex flex-wrap gap-1 mt-2">
                    {patient.alerts.length > 0 ? (
                      patient.alerts.map(alert => (
                        <span key={alert} className="text-[9px] font-black uppercase px-1.5 py-0.5 rounded bg-current/10 border border-current/20">
                          {alert}
                        </span>
                      ))
                    ) : (
                      <span className="text-[9px] font-bold text-text-muted uppercase">Vitals Stable</span>
                    )}
                  </div>
                </div>

                {/* Selection Indicator */}
                {isSelected && (
                  <div className="absolute right-3 top-1/2 -translate-y-1/2">
                    <i className="bi bi-chevron-right text-text-muted"></i>
                  </div>
                )}
              </button>
            );
          })
        )}
      </div>

      {/* FOOTER: System Health */}
      <div className="p-4 bg-bg-panel border-t border-border-subtle">
        <div className="rounded-lg bg-bg-main p-3 flex items-center justify-between">
          <div className="flex items-center gap-2">
             <div className="h-2 w-2 rounded-full bg-accent animate-pulse"></div>
             <span className="text-[10px] font-black text-text-secondary uppercase">Inference Engine</span>
          </div>
          <span className="text-[10px] font-mono text-accent">98.2ms</span>
        </div>
      </div>
    </aside>
  );
}