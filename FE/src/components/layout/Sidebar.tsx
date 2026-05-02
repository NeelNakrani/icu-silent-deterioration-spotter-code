import { useMemo, useState } from "react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ButtonGroup } from "@/components/ui/button-group";

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
  const [selectedId, setSelectedId] = useState<string | null>("P-101");
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
    <aside className="hidden lg:flex w-80 bg-bg-panel border-r border-border-subtle flex-col h-screen shrink-0">
      <div className="p-6 pb-4">
        <div className="flex items-center justify-between mb-2">
          <h2 className="text-[11px] font-semibold tracking-[0.3em] text-text-secondary uppercase">
            Unit North
          </h2>
          <div className="flex items-center gap-2">
            <span className="h-2 w-2 rounded-full bg-success"></span>
            <span className="text-[10px] font-semibold text-success uppercase">Live</span>
          </div>
        </div>
        <h1 className="text-lg font-semibold text-text-primary tracking-tight">
          Cohort Overview
        </h1>
        <p className="text-xs text-text-muted mt-1">
          Sorted by risk, newest updates first.
        </p>
      </div>

      <div className="px-6 pb-4">
        <ButtonGroup className="bg-bg-main/40 rounded-md p-1">
          <Button size="xs" variant="secondary" className="text-[11px]">
            All ({patients.length})
          </Button>
          <Button size="xs" variant="ghost" className="text-[11px] text-text-muted hover:text-text-primary">
            Critical (2)
          </Button>
        </ButtonGroup>
      </div>

      {/* PATIENT LIST */}
      <div className="flex-1 overflow-y-auto px-4 pb-4 space-y-3 custom-scrollbar">
        {loading ? (
           /* Loading State */
           <div className="space-y-3">
              {[1, 2, 3, 4].map(i => (
                <div key={i} className="h-20 bg-bg-elevated/60 animate-pulse rounded-xl" />
              ))}
           </div>
        ) : (
          sortedPatients.map((patient) => {
            const isSelected = selectedId === patient.id;
            const riskColors = {
              RED: "border-l-critical",
              YELLOW: "border-l-warning",
              GREEN: "border-l-success",
            };
            const riskBadgeStyles = {
              RED: "bg-critical/15 text-critical",
              YELLOW: "bg-warning/15 text-warning",
              GREEN: "bg-success/15 text-success",
            };

            return (
              <button
                key={patient.id}
                onClick={() => setSelectedId(patient.id)}
                className={`w-full text-left rounded-lg border-l-4 transition-all duration-200 ring-1 ring-transparent bg-white/90
                  ${isSelected ? "bg-bg-elevated/80 ring-border-subtle" : "hover:bg-bg-elevated/50"}
                  ${riskColors[patient.risk]}
                `}
              >
                <div className="p-4 space-y-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className="text-lg font-semibold font-mono text-text-primary">
                        {patient.bed}
                      </span>
                      <span className="text-[10px] font-semibold text-text-muted px-2 py-0.5 bg-bg-main/70 rounded uppercase">
                        {patient.id}
                      </span>
                    </div>
                    <Badge className={`text-[10px] ${riskBadgeStyles[patient.risk]}`}>
                      {patient.risk}
                    </Badge>
                  </div>

                  <div>
                    <div className="text-sm font-semibold text-text-primary">
                      {patient.name}
                    </div>
                    <div className="text-[11px] text-text-muted">
                      Updated {patient.lastUpdate}
                    </div>
                  </div>

                  <div className="flex items-center justify-between">
                    <div className="text-[11px] text-text-secondary">
                      {patient.alerts.length > 0
                        ? `${patient.alerts.length} active alert${patient.alerts.length > 1 ? "s" : ""}`
                        : "Vitals stable"}
                    </div>
                    {patient.alerts.length > 0 && (
                      <Badge variant="outline" className="text-[10px] text-text-secondary border-border-subtle">
                        Review
                      </Badge>
                    )}
                  </div>
                </div>
              </button>
            );
          })
        )}
      </div>

      {/* FOOTER: System Health */}
      <div className="p-4 bg-bg-panel border-t border-border-subtle">
        <div className="rounded-lg bg-bg-main/70 p-3 flex items-center justify-between">
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