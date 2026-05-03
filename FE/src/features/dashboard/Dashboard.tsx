import React from 'react';
import type { PatientSummary, RiskLevel } from '../../types/icu';
import { RiskPill, Chip, VitalCell, AgentBadge } from '../../components';

// Screen 1: Patient List Dashboard
// 3 layout variants over PatientSummary[] (api-spec).

interface HeaderProps {
  unit: string;
  setUnit: (unit: string) => void;
  refresh?: boolean;
  density?: string;
}

function useViewport() {
  const [size, setSize] = React.useState({
    width: window.innerWidth,
    height: window.innerHeight,
  });

  React.useEffect(() => {
    const handleResize = () => {
      setSize({
        width: window.innerWidth,
        height: window.innerHeight,
      });
    };

    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  return size;
}

function Header({ unit, setUnit, refresh, density }: HeaderProps) {
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
        {["All Units","MICU", "SICU"].map((u) => (
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

const flagTone = (f: string): "red" | "amber" | "neutral" =>
  /shock|arrest|anuria|vasopres|rising/i.test(f) ? "red" :
  /lactate|trop|plat|pf|gap|hgb/i.test(f)        ? "amber" : "neutral";

// risk_level (red/yellow/green) → CSS variable suffix (high/med/low)
function riskVar(level: RiskLevel) {
  return level === "red" ? "high" : level === "yellow" ? "med" : "low";
}

// ── Patient Cards (Default View) ────────────────────────────────────────────
interface SubComponentProps {
  patients: PatientSummary[];
  onOpen: (patient: PatientSummary) => void;
}

interface PaginationControlsProps {
  onPrev?: () => void;
  onNext?: () => void;
  pageInfo?: string;
}

function PaginationControls({ onPrev, onNext, pageInfo }: PaginationControlsProps) {
  if (!pageInfo) return null;
  
  return (
    <div className="pagination-controls" style={{
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      gap: 8,
      padding: "12px 20px",
      borderBottom: "1px solid var(--rule-soft)",
      background: "var(--surface-1)",
    }}>
      <button
        onClick={onPrev}
        disabled={!onPrev}
        style={{
          ...btnGhost,
          padding: "6px 8px",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          opacity: onPrev ? 1 : 0.4,
          cursor: onPrev ? "pointer" : "not-allowed",
        }}
        aria-label="Previous page"
      >
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <polyline points="15 18 9 12 15 6"></polyline>
        </svg>
      </button>
      
      <span style={{
        fontFamily: "var(--mono)",
        fontSize: 11.5,
        color: "var(--ink-2)",
        minWidth: 60,
        textAlign: "center",
        fontWeight: 500,
      }}>
        Page {pageInfo}
      </span>
      
      <button
        onClick={onNext}
        disabled={!onNext}
        style={{
          ...btnGhost,
          padding: "6px 8px",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          opacity: onNext ? 1 : 0.4,
          cursor: onNext ? "pointer" : "not-allowed",
        }}
        aria-label="Next page"
      >
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <polyline points="9 18 15 12 9 6"></polyline>
        </svg>
      </button>
    </div>
  );
}

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

          <div className="patient-card-vitals" style={{ 
            display: "flex", 
            alignItems: "center",
            gap: 14, 
            paddingTop: 10, 
            borderTop: "1px dashed var(--rule)" 
          }}>
            {/* Vitals Section */}
            <VitalCell label="HR" value={p.vitals.hr} unit="bpm" direction={p.trend.hr} />
            <VitalCell label="MAP" value={p.vitals.map} unit="mmHg" direction={p.trend.map} />
            <VitalCell label="SpO₂" value={p.vitals.spo2} unit="%" direction={p.trend.spo2} />
            <VitalCell label="RR" value={p.vitals.rr} unit="/m" />

            {/* Spacer to push metadata to the right */}
            <div style={{ flex: 1 }} />

            {/* Metadata Group: Badges and Timestamp */}
            <div style={{ 
              display: "flex", 
              flexDirection: "column", 
              alignItems: "flex-end", 
              gap: 4 
            }}>
              {/* Agent Badges */}
              <div style={{ display: "flex", gap: 4 }}>
                <AgentBadge kind="trend" count={p.agent_counts.trend} />
                <AgentBadge kind="conflict" count={p.agent_counts.conflict} />
                <AgentBadge kind="timebomb" count={p.agent_counts.timebomb} />
              </div>

              {/* Timestamp Group */}
              <div style={{ display: "flex", gap: 4, alignItems: "baseline" }}>
                <span style={{ 
                  fontSize: 9, 
                  color: "var(--ink-4)", 
                  textTransform: "uppercase", 
                  letterSpacing: ".06em" 
                }}>
                  Updated
                </span>
                <span style={{ 
                  fontFamily: "var(--mono)", 
                  fontSize: 10, 
                  color: "var(--ink-3)" 
                }}>
                  {p.last_updated_label}
                </span>
              </div>
            </div>
          </div>
        </button>
      ))}
    </div>
  );
}

interface StatStripProps {
  patients: PatientSummary[];
  riskFilter: RiskLevel | "all";
  onRiskFilterChange: (filter: RiskLevel | "all") => void;
}

function StatStrip({ patients, riskFilter, onRiskFilterChange }: StatStripProps) {
  const red    = patients.filter((p) => p.risk_level === "red").length;
  const yellow = patients.filter((p) => p.risk_level === "yellow").length;
  const green  = patients.filter((p) => p.risk_level === "green").length;
  const flags = patients.reduce((s, p) => s + p.flags.length, 0);
  
  const stats: {
    k: string;
    v: number | string;
    sub: string;
    tone?: "red" | "amber" | "green";
    clickable?: boolean;
    filterValue?: RiskLevel | "all";
  }[] = [
    { k: "Census",    v: patients.length, sub: "active beds" },
    { k: "Red",       v: red,    sub: "critical",    tone: "red", clickable: true, filterValue: "red" },
    { k: "Yellow",    v: yellow, sub: "watch",       tone: "amber", clickable: true, filterValue: "yellow" },
    { k: "Green",     v: green,  sub: "stable",      tone: "green", clickable: true, filterValue: "green" },
    { k: "Open flags",v: flags,  sub: "across cohort" },
    { k: "Agent runs / hr", v: 142, sub: "p50 4.2s" },
  ];
  
  return (
    <div className="dashboard-stat-strip" style={{
      display: "grid", gridTemplateColumns: `repeat(${stats.length}, 1fr)`,
      borderBottom: "1px solid var(--rule)", background: "var(--surface-2)",
    }}>
      {stats.map((s, i) => {
        const isActive = s.filterValue && riskFilter === s.filterValue;
        const isClickable = s.clickable;
        
        return (
          <div
            key={i}
            onClick={() => {
              if (isClickable && s.filterValue) {
                // Toggle filter: if already active, reset to "all"
                onRiskFilterChange(isActive ? "all" : s.filterValue);
              }
            }}
            style={{
              padding: "10px 16px",
              borderRight: i < stats.length - 1 ? "1px solid var(--rule-soft)" : "none",
              display: "flex",
              flexDirection: "column",
              gap: 2,
              cursor: isClickable ? "pointer" : "default",
              background: isActive ? "var(--surface-1)" : "transparent",
              borderTop: isActive ? `2px solid var(--risk-${riskVar(s.filterValue as RiskLevel)}-fg)` : "2px solid transparent",
              transition: "all 0.2s ease",
              position: "relative",
            }}
            onMouseEnter={(e) => {
              if (isClickable && !isActive) {
                e.currentTarget.style.background = "var(--surface-1)";
              }
            }}
            onMouseLeave={(e) => {
              if (isClickable && !isActive) {
                e.currentTarget.style.background = "transparent";
              }
            }}
          >
            <span style={{ fontSize: 10, color: "var(--ink-3)", letterSpacing: ".06em", textTransform: "uppercase" }}>
              {s.k}
            </span>
            <span style={{
              fontFamily: "var(--mono)", fontSize: 18, fontWeight: 500,
              color: s.tone === "red" ? "var(--risk-high-fg)"
                   : s.tone === "amber" ? "var(--risk-med-fg)"
                   : s.tone === "green" ? "var(--risk-low-fg)"
                   : "var(--ink-1)",
            }}>
              {s.v}
            </span>
            <span style={{ fontSize: 10.5, color: "var(--ink-3)" }}>
              {s.sub}
              {isClickable && <span style={{ marginLeft: 4, opacity: 0.5 }}>↓</span>}
            </span>
          </div>
        );
      })}
    </div>
  );
}

interface DashboardProps {
  patients: PatientSummary[];
  onOpen: (patient: PatientSummary) => void;
  density?: string;
}

function Dashboard({ patients, onOpen, density }: DashboardProps) {
  const { width, height } = useViewport();

  const CARD_MIN_WIDTH = 320;
  const GRID_GAP = 12;
  const HORIZONTAL_PADDING = 40; // approx (20 left + 20 right)

  const HEADER_HEIGHT = 60;
  const STAT_HEIGHT = 60;
  const PAGINATION_HEIGHT = 60;
  const VERTICAL_PADDING = 40;

  const availableWidth = width - HORIZONTAL_PADDING;
  const columns = Math.max(1, Math.floor(availableWidth / (CARD_MIN_WIDTH + GRID_GAP)));

  const availableHeight =
    height - HEADER_HEIGHT - STAT_HEIGHT - PAGINATION_HEIGHT - VERTICAL_PADDING;

  // Approximate card height (you can tweak this)
  const CARD_HEIGHT = 180;

  const rows = Math.max(1, Math.floor(availableHeight / (CARD_HEIGHT + GRID_GAP)));

  const pageSize = columns * rows;

  const [unit, setUnit] = React.useState("All Units");
  const [currentPage, setCurrentPage] = React.useState(0);
  const [riskFilter, setRiskFilter] = React.useState<RiskLevel | "all">("all");
  
  // Settings: How many patients to show per page
  
  // Filter by unit first
  let filteredPatients = patients.filter(p => unit === "All Units" || p.careunit_short === unit);
  
  // Then filter by risk level if a filter is active
  if (riskFilter !== "all") {
    filteredPatients = filteredPatients.filter(p => p.risk_level === riskFilter);
  }
  
  // Pagination for cards view
  const pageCount = Math.ceil(filteredPatients.length / pageSize);
  
  // The specific slice of patients for the current page
  const visiblePatients = filteredPatients.slice(currentPage * pageSize, (currentPage + 1) * pageSize);

  const handleNext = () => setCurrentPage((p) => Math.min(p + 1, pageCount - 1));
  const handlePrev = () => setCurrentPage((p) => Math.max(p - 1, 0));

  // Reset page when unit or risk filter changes to avoid empty screens
  React.useEffect(() => { setCurrentPage(0); }, [unit, riskFilter]);

  // Get unfiltered patients for the current unit to show accurate stats
  const unitPatients = patients.filter(p => unit === "All Units" || p.careunit_short === unit);

  return (
    <div className="dashboard-shell" style={{ display: "flex", flexDirection: "column", height: "100vh", background: "var(--surface-0)" }}>
      <Header
        unit={unit}
        setUnit={setUnit}
        density={density}
      />
      
      <StatStrip
        patients={unitPatients}
        riskFilter={riskFilter}
        onRiskFilterChange={setRiskFilter}
      />

      <div style={{ flex: 1, overflow: "auto" }}>
        <PatientCards patients={visiblePatients} onOpen={onOpen} />
      </div>
      
      <PaginationControls
        onPrev={currentPage > 0 ? handlePrev : undefined}
        onNext={currentPage < pageCount - 1 ? handleNext : undefined}
        pageInfo={`${currentPage + 1} / ${pageCount || 1}`}
      />
    </div>
  );
}

export default Dashboard;

// Made with Bob
