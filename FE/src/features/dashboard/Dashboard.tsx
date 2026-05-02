import React from 'react';
import type { PatientSummary, RiskLevel } from '../../types/icu';
import { RiskPill, Chip, TrendArrow, VitalCell, AgentBadge } from '../../components';

// Screen 1: Patient List Dashboard
// 3 layout variants over PatientSummary[] (api-spec).

interface HeaderProps {
  unit: string;
  setUnit: (unit: string) => void;
  refresh?: boolean;
  density?: string;
  variant: string;
  setVariant: (variant: string) => void;
  total: number;
}

function Header({ unit, setUnit, refresh, density, variant, setVariant }: HeaderProps) {
  const [tick, setTick] = React.useState(0);
  React.useEffect(() => {
    if (!refresh) return;
    const id = setInterval(() => setTick((x) => x + 1), 1000);
    return () => clearInterval(id);
  }, [refresh]);
  
  // Spec recommends 60s auto-refresh.
  const seconds = (tick % 60);
  
  return (
    <header className="dashboard-header" style={{
      display: "flex", alignItems: "center", gap: 24,
      padding: density === "dense" ? "10px 20px" : "14px 24px",
      borderBottom: "1px solid var(--rule)", background: "var(--surface-1)",
    }}>
      <div className="dashboard-brand" style={{ display: "flex", alignItems: "center", gap: 10 }}>
        <div style={{
          width: 22, height: 22, borderRadius: 5,
          background: "linear-gradient(135deg, var(--accent), var(--ink-1))",
          display: "grid", placeItems: "center", color: "var(--surface-1)",
          fontFamily: "var(--mono)", fontSize: 11, fontWeight: 700,
        }}>S</div>
        <div style={{ display: "flex", flexDirection: "column", lineHeight: 1.1 }}>
          <span style={{ fontSize: 13, fontWeight: 600, letterSpacing: ".005em" }}>Sentinel ICU</span>
          <span style={{ fontSize: 10.5, color: "var(--ink-3)" }}>Silent Deterioration Spotter · v0.1.0</span>
        </div>
      </div>

      <nav className="segmented-control unit-switcher" style={{ display: "flex", gap: 2, padding: 2, background: "var(--chip-bg)", borderRadius: 8 }}>
        {["MICU", "SICU", "All Units"].map((u) => (
          <button key={u} onClick={() => setUnit(u)}
            style={{
              padding: "5px 11px", border: 0, borderRadius: 6, cursor: "pointer",
              background: unit === u ? "var(--surface-1)" : "transparent",
              color: unit === u ? "var(--ink-1)" : "var(--ink-2)",
              fontSize: 11.5, fontWeight: unit === u ? 600 : 500,
              boxShadow: unit === u ? "0 1px 2px rgba(0,0,0,.06), 0 0 0 .5px rgba(0,0,0,.06)" : "none",
            }}>{u}</button>
        ))}
      </nav>

      <div style={{ flex: 1 }} />

      <div className="dashboard-live-status" style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 11, color: "var(--ink-3)" }}>
        <span style={{
          width: 7, height: 7, borderRadius: 99, background: "var(--ok)",
          boxShadow: "0 0 0 3px color-mix(in oklch, var(--ok) 22%, transparent)",
          animation: "pulse 1.6s ease-in-out infinite",
        }} />
        <span style={{ fontFamily: "var(--mono)" }}>GET /patients · {60 - seconds}s</span>
      </div>

      <div className="segmented-control layout-switcher" style={{ display: "flex", gap: 2, padding: 2, background: "var(--chip-bg)", borderRadius: 8 }}>
        {[
          { v: "table", l: "Table" },
          { v: "cards", l: "Cards" },
          { v: "lanes", l: "Lanes" },
        ].map((o) => (
          <button key={o.v} onClick={() => setVariant(o.v)}
            style={{
              padding: "5px 10px", border: 0, borderRadius: 6, cursor: "pointer",
              background: variant === o.v ? "var(--surface-1)" : "transparent",
              color: variant === o.v ? "var(--ink-1)" : "var(--ink-2)",
              fontSize: 11, fontWeight: variant === o.v ? 600 : 500,
              fontFamily: "var(--mono)", letterSpacing: ".02em",
              boxShadow: variant === o.v ? "0 1px 2px rgba(0,0,0,.06), 0 0 0 .5px rgba(0,0,0,.06)" : "none",
            }}>{o.l}</button>
        ))}
      </div>

      <div className="dashboard-actions" style={{ display: "flex", gap: 8 }}>
        <button style={btnGhost}>Filters</button>
      </div>
    </header>
  );
}

const btnGhost: React.CSSProperties = {
  padding: "5px 11px", border: "1px solid var(--rule)", background: "var(--surface-1)",
  color: "var(--ink-2)", borderRadius: 7, fontSize: 11.5, fontWeight: 500, cursor: "pointer",
};
const btnPrimary: React.CSSProperties = {
  padding: "5px 11px", border: 0, background: "var(--ink-1)",
  color: "var(--surface-1)", borderRadius: 7, fontSize: 11.5, fontWeight: 500, cursor: "pointer",
};

const flagTone = (f: string): "red" | "amber" | "neutral" =>
  /shock|arrest|anuria|vasopres|rising/i.test(f) ? "red" :
  /lactate|trop|plat|pf|gap|hgb/i.test(f)        ? "amber" : "neutral";

// risk_level (red/yellow/green) → CSS variable suffix (high/med/low)
function riskVar(level: RiskLevel) {
  return level === "red" ? "high" : level === "yellow" ? "med" : "low";
}

const th: React.CSSProperties = { padding: "10px 10px", borderBottom: "1px solid var(--rule)", fontWeight: 500 };
const td: React.CSSProperties = { padding: "10px 10px", borderBottom: "1px solid var(--rule-soft)", verticalAlign: "middle" };
const tdMono: React.CSSProperties = { ...td, fontFamily: "var(--mono)", fontVariantNumeric: "tabular-nums", color: "var(--ink-1)", width: 56 };

// ── Variant A: Dense Table with colored row borders ─────────────────────────
interface SubComponentProps {
  patients: PatientSummary[];
  onOpen: (patient: PatientSummary) => void;
}

function PatientTable({ patients, onOpen }: SubComponentProps) {
  return (
    <div className="patient-table-wrap" style={{ padding: "16px 20px", overflow: "auto" }}>
      <table style={{
        width: "100%", borderCollapse: "separate", borderSpacing: 0,
        fontSize: 12, color: "var(--ink-1)",
      }}>
        <thead>
          <tr style={{ textAlign: "left", color: "var(--ink-3)", fontSize: 10.5, letterSpacing: ".06em", textTransform: "uppercase" }}>
            <th style={th}>Risk</th>
            <th style={th}>Bed</th>
            <th style={th}>Patient</th>
            <th style={th}>Primary</th>
            <th style={th}>Active flags</th>
            <th style={th}>HR</th>
            <th style={th}>MAP</th>
            <th style={th}>SpO₂</th>
            <th style={th}>RR</th>
            <th style={th}>Agents</th>
            <th style={{ ...th, textAlign: "right" }}>Updated</th>
          </tr>
        </thead>
        <tbody>
          {patients.map((p, i) => (
            <tr key={p.patient_id} onClick={() => onOpen(p)}
              style={{
                cursor: "pointer",
                background: i % 2 === 0 ? "var(--surface-1)" : "var(--surface-2)",
              }}
              onMouseOver={(e) => e.currentTarget.style.background = "var(--surface-hover)"}
              onMouseOut={(e) => e.currentTarget.style.background = i % 2 === 0 ? "var(--surface-1)" : "var(--surface-2)"}>
              <td style={{ ...td, borderLeft: `4px solid var(--risk-${riskVar(p.risk_level)}-fg)`, paddingLeft: 12, width: 92 }}>
                <RiskPill risk_level={p.risk_level} score={p.risk_score} delta={p.risk_delta} />
              </td>
              <td style={{ ...td, fontFamily: "var(--mono)", color: "var(--ink-2)", width: 76 }}>{p.careunit_short}</td>
              <td style={td}>
                <div style={{ display: "flex", flexDirection: "column", lineHeight: 1.25 }}>
                  <span style={{ fontWeight: 500, fontFamily: "var(--mono)" }}>#{p.patient_id}</span>
                  <span style={{ fontSize: 10.5, color: "var(--ink-3)", fontFamily: "var(--mono)" }}>
                    stay {p.stay_id} · {p.age}{p.gender} · {p.los}
                  </span>
                </div>
              </td>
              <td style={{ ...td, color: "var(--ink-2)" }}>{p.primary}</td>
              <td style={td}>
                <div style={{ display: "flex", gap: 4, flexWrap: "wrap" }}>
                  {p.flags.length === 0
                    ? <span style={{ color: "var(--ink-4)", fontSize: 11 }}>—</span>
                    : p.flags.map((f, i) => (
                        <Chip key={i} tone={flagTone(f)} dot={flagTone(f) !== "neutral"}>{f}</Chip>
                      ))}
                </div>
              </td>
              <td style={tdMono}>{p.vitals.hr} <TrendArrow direction={p.trend.hr} /></td>
              <td style={tdMono}>{p.vitals.map} <TrendArrow direction={p.trend.map} /></td>
              <td style={tdMono}>{p.vitals.spo2}<span style={{ color: "var(--ink-4)" }}>%</span></td>
              <td style={tdMono}>{p.vitals.rr}</td>
              <td style={td}>
                <div style={{ display: "flex", gap: 4 }}>
                  <AgentBadge kind="trend" count={p.agent_counts.trend} />
                  <AgentBadge kind="conflict" count={p.agent_counts.conflict} />
                  <AgentBadge kind="timebomb" count={p.agent_counts.timebomb} />
                </div>
              </td>
              <td style={{ ...td, textAlign: "right", color: "var(--ink-3)", fontFamily: "var(--mono)", fontSize: 10.5 }}>{p.last_updated_label}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

// ── Variant B: Card Grid ────────────────────────────────────────────────────
function PatientCards({ patients, onOpen }: SubComponentProps) {
  return (
    <div className="patient-card-grid" style={{
      padding: 20, display: "grid", gap: 12,
      gridTemplateColumns: "repeat(auto-fill, minmax(320px, 1fr))",
    }}>
      {patients.map((p) => (
        <button className="patient-card" key={p.patient_id} onClick={() => onOpen(p)} style={{
          all: "unset", cursor: "pointer", display: "block",
          background: "var(--surface-1)",
          border: "1px solid var(--rule)",
          borderLeft: `3px solid var(--risk-${riskVar(p.risk_level)}-fg)`,
          borderRadius: 10, padding: 14,
          boxShadow: p.risk_level === "red"
            ? "0 1px 0 rgba(0,0,0,.02), 0 0 0 1px color-mix(in oklch, var(--risk-high-fg) 16%, transparent)"
            : "0 1px 0 rgba(0,0,0,.02)",
        }}>
          <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", gap: 10, marginBottom: 10 }}>
            <div>
              <div style={{ fontFamily: "var(--mono)", fontSize: 10.5, color: "var(--ink-3)" }}>{p.careunit_short} · {p.age}{p.gender}</div>
              <div style={{ fontSize: 13, fontWeight: 600, marginTop: 2, fontFamily: "var(--mono)" }}>subject_id {p.patient_id}</div>
              <div style={{ fontSize: 11, color: "var(--ink-2)", marginTop: 1 }}>{p.primary}</div>
            </div>
            <RiskPill risk_level={p.risk_level} score={p.risk_score} delta={p.risk_delta} />
          </div>

          <div style={{ display: "flex", gap: 4, flexWrap: "wrap", marginBottom: 12, minHeight: 22 }}>
            {p.flags.length === 0
              ? <span style={{ color: "var(--ink-4)", fontSize: 11 }}>No active flags</span>
              : p.flags.map((f, i) => (
                  <Chip key={i} tone={flagTone(f)} dot={flagTone(f) !== "neutral"}>{f}</Chip>
                ))}
          </div>

          <div className="patient-card-vitals" style={{ display: "flex", gap: 14, paddingTop: 10, borderTop: "1px dashed var(--rule)" }}>
            <VitalCell label="HR" value={p.vitals.hr} unit="bpm" direction={p.trend.hr} />
            <VitalCell label="MAP" value={p.vitals.map} unit="mmHg" direction={p.trend.map} />
            <VitalCell label="SpO₂" value={p.vitals.spo2} unit="%" direction={p.trend.spo2} />
            <VitalCell label="RR" value={p.vitals.rr} unit="/m" />
            <div style={{ flex: 1 }} />
            <div style={{ display: "flex", gap: 4, alignSelf: "flex-end" }}>
              <AgentBadge kind="trend" count={p.agent_counts.trend} />
              <AgentBadge kind="conflict" count={p.agent_counts.conflict} />
              <AgentBadge kind="timebomb" count={p.agent_counts.timebomb} />
            </div>
          </div>
        </button>
      ))}
    </div>
  );
}

// ── Variant C: Risk lanes (kanban-ish) ──────────────────────────────────────
function PatientLanes({ patients, onOpen }: SubComponentProps) {
  const lanes: { key: RiskLevel; label: string; sub: string }[] = [
    { key: "red",    label: "Critical (red)",   sub: "Active escalation" },
    { key: "yellow", label: "Watch (yellow)",   sub: "Trending or unsettled" },
    { key: "green",  label: "Stable (green)",   sub: "Routine surveillance" },
  ];
  return (
    <div className="patient-lanes" style={{ padding: 16, display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 14, alignItems: "start" }}>
      {lanes.map((lane) => {
        const list = patients.filter((p) => p.risk_level === lane.key);
        const v = riskVar(lane.key);
        return (
          <div key={lane.key} style={{
            background: `color-mix(in oklch, var(--risk-${v}-fg) 5%, var(--surface-2))`,
            border: `1px solid color-mix(in oklch, var(--risk-${v}-fg) 18%, var(--rule))`,
            borderRadius: 12, padding: 12,
          }}>
            <div style={{
              display: "flex", alignItems: "baseline", justifyContent: "space-between",
              padding: "2px 4px 10px", borderBottom: `1px dashed color-mix(in oklch, var(--risk-${v}-fg) 25%, transparent)`,
              marginBottom: 10,
            }}>
              <div>
                <div style={{ fontSize: 12, fontWeight: 600, color: `var(--risk-${v}-fg)` }}>{lane.label}</div>
                <div style={{ fontSize: 10.5, color: "var(--ink-3)", marginTop: 1 }}>{lane.sub}</div>
              </div>
              <div style={{ fontFamily: "var(--mono)", fontSize: 11, color: "var(--ink-2)" }}>{list.length}</div>
            </div>

            <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
              {list.map((p) => (
                <button key={p.patient_id} onClick={() => onOpen(p)} style={{
                  all: "unset", cursor: "pointer", display: "block",
                  background: "var(--surface-1)", border: "1px solid var(--rule)",
                  borderRadius: 8, padding: "10px 12px",
                }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline" }}>
                    <div style={{ fontSize: 12, fontWeight: 600, fontFamily: "var(--mono)" }}>#{p.patient_id}</div>
                    <RiskPill risk_level={p.risk_level} score={p.risk_score} delta={p.risk_delta} />
                  </div>
                  <div style={{ fontSize: 10.5, color: "var(--ink-3)", fontFamily: "var(--mono)", margin: "2px 0 6px" }}>
                    {p.careunit_short} · {p.age}{p.gender} · {p.los}
                  </div>
                  <div style={{ fontSize: 11, color: "var(--ink-2)", marginBottom: 8 }}>{p.primary}</div>
                  <div style={{ display: "flex", flexWrap: "wrap", gap: 4, marginBottom: 8 }}>
                    {p.flags.slice(0, 3).map((f, i) => (
                      <Chip key={i} tone={flagTone(f)} dot={flagTone(f) !== "neutral"}>{f}</Chip>
                    ))}
                  </div>
                  <div style={{ display: "flex", gap: 12, alignItems: "center" }}>
                    <span style={{ fontFamily: "var(--mono)", fontSize: 10.5, color: "var(--ink-3)" }}>
                      HR {p.vitals.hr} · MAP {p.vitals.map} · SpO₂ {p.vitals.spo2}%
                    </span>
                    <div style={{ flex: 1 }} />
                    <div style={{ display: "flex", gap: 3 }}>
                      <AgentBadge kind="trend" count={p.agent_counts.trend} />
                      <AgentBadge kind="conflict" count={p.agent_counts.conflict} />
                      <AgentBadge kind="timebomb" count={p.agent_counts.timebomb} />
                    </div>
                  </div>
                </button>
              ))}
              {list.length === 0 && (
                <div style={{ fontSize: 11, color: "var(--ink-4)", padding: "12px 6px", textAlign: "center" }}>—</div>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}

function StatStrip({ patients }: { patients: PatientSummary[] }) {
  const red    = patients.filter((p) => p.risk_level === "red").length;
  const yellow = patients.filter((p) => p.risk_level === "yellow").length;
  const green  = patients.filter((p) => p.risk_level === "green").length;
  const flags = patients.reduce((s, p) => s + p.flags.length, 0);
  const stats: { k: string; v: number | string; sub: string; tone?: "red" | "amber" | "green" }[] = [
    { k: "Census",    v: patients.length, sub: "active beds" },
    { k: "Red",       v: red,    sub: "critical",    tone: "red" },
    { k: "Yellow",    v: yellow, sub: "watch",       tone: "amber" },
    { k: "Green",     v: green,  sub: "stable",      tone: "green" },
    { k: "Open flags",v: flags,  sub: "across cohort" },
    { k: "Agent runs / hr", v: 142, sub: "p50 4.2s" },
  ];
  return (
    <div className="dashboard-stat-strip" style={{
      display: "grid", gridTemplateColumns: `repeat(${stats.length}, 1fr)`,
      borderBottom: "1px solid var(--rule)", background: "var(--surface-2)",
    }}>
      {stats.map((s, i) => (
        <div key={i} style={{
          padding: "10px 16px", borderRight: i < stats.length - 1 ? "1px solid var(--rule-soft)" : "none",
          display: "flex", flexDirection: "column", gap: 2,
        }}>
          <span style={{ fontSize: 10, color: "var(--ink-3)", letterSpacing: ".06em", textTransform: "uppercase" }}>{s.k}</span>
          <span style={{
            fontFamily: "var(--mono)", fontSize: 18, fontWeight: 500,
            color: s.tone === "red" ? "var(--risk-high-fg)"
                 : s.tone === "amber" ? "var(--risk-med-fg)"
                 : s.tone === "green" ? "var(--risk-low-fg)"
                 : "var(--ink-1)",
          }}>{s.v}</span>
          <span style={{ fontSize: 10.5, color: "var(--ink-3)" }}>{s.sub}</span>
        </div>
      ))}
    </div>
  );
}

interface DashboardProps {
  patients: PatientSummary[];
  onOpen: (patient: PatientSummary) => void;
  variant: string;
  setVariant: (variant: string) => void;
  density?: string;
}

function Dashboard({ patients, onOpen, variant, setVariant, density }: DashboardProps) {
  const [unit, setUnit] = React.useState("MICU");
  return (
    <div className="dashboard-shell" style={{ display: "flex", flexDirection: "column", height: "100vh", background: "var(--surface-0)" }}>
      <Header unit={unit} setUnit={setUnit} refresh={true} density={density} variant={variant} setVariant={setVariant} total={patients.length} />
      <StatStrip patients={patients} />
      <div style={{ flex: 1, overflow: "auto" }}>
        {variant === "table" && <PatientTable patients={patients} onOpen={onOpen} />}
        {variant === "cards" && <PatientCards patients={patients} onOpen={onOpen} />}
        {variant === "lanes" && <PatientLanes patients={patients} onOpen={onOpen} />}
      </div>
    </div>
  );
}

export default Dashboard;
