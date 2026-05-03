import React from 'react';
import type { PatientDetailData, TimelineItem, TrendReport, ConflictReport, TimeBombReport, VitalSpark } from '../../types/icu';
import { Sparkline, RiskPill, Chip, TrendArrow, LevelBadge } from '../../components';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '../../components/ui/dialog';
import { Switch } from '../../components/ui/switch';

// Screen 2: SBAR+ Brief detail panel — aligned to api-spec SBARBrief schema.

interface SbarCardProps {
  p: PatientDetailData;
}

function SbarCard({ p }: SbarCardProps) {
  if (!p) return null;
  
  const items = [
    { k: "S", label: "Situation",      txt: p.situation || '—' },
    { k: "B", label: "Background",     txt: p.background || '—' },
    { k: "A", label: "Assessment",     txt: p.assessment || '—' },
    { k: "R", label: "Recommendation", txt: p.recommendation || '—' },
  ];
  return (
    <div className="sbar-card" style={{
      background: "var(--surface-1)", border: "1px solid var(--rule)",
      borderRadius: 12, padding: 18,
    }}>
      <div className="sbar-card-header" style={{
        display: "flex", justifyContent: "space-between", alignItems: "flex-start",
        paddingBottom: 14, borderBottom: "1px solid var(--rule-soft)", marginBottom: 14, gap: 12,
      }}>
        <div>
          <div style={{ fontSize: 10.5, color: "var(--ink-3)", letterSpacing: ".06em", textTransform: "uppercase", marginBottom: 4 }}>SBAR+ Brief</div>
          <h2 style={{ fontSize: 18, fontWeight: 600, margin: 0, lineHeight: 1.2, fontFamily: "var(--mono)" }}>Patient ID {p.patient_id || '—'}</h2>
          <div style={{ fontSize: 11.5, color: "var(--ink-2)", marginTop: 4, fontFamily: "var(--mono)" }}>
            stay {p.stay_id || '—'} · {p.careunit_short || '—'} · {p.age || '—'}{p.gender || ''} · LOS {p.los || '—'} · {p.attending || '—'}
          </div>
        </div>
        <div style={{ textAlign: "right" }}>
          <RiskPill risk_level={p.risk_level || 'green'} score={p.risk_score ?? 0} delta={p.risk_delta ?? 0} size="lg" />
          <div style={{ fontSize: 11, color: "var(--risk-high-fg)", marginTop: 6, maxWidth: 200 }}>
            {p.risk_window || '—'}
          </div>
        </div>
      </div>

      <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
        {items.map((it) => (
          <div key={it.k} style={{ display: "grid", gridTemplateColumns: "26px 1fr", gap: 12 }}>
            <div style={{
              width: 26, height: 26, borderRadius: 6,
              background: "var(--chip-bg)", color: "var(--ink-1)",
              display: "grid", placeItems: "center",
              fontFamily: "var(--mono)", fontWeight: 600, fontSize: 12,
            }}>{it.k}</div>
            <div>
              <div style={{ fontSize: 10.5, color: "var(--ink-3)", letterSpacing: ".06em", textTransform: "uppercase", marginBottom: 2 }}>{it.label}</div>
              <div style={{ fontSize: 12.5, lineHeight: 1.5, color: "var(--ink-1)" }}>{it.txt}</div>
            </div>
          </div>
        ))}
      </div>

      {/* Data quality + confidence footer (per spec) */}
      <div className="sbar-card-footer" style={{
        display: "flex", gap: 16, marginTop: 14, paddingTop: 12,
        borderTop: "1px dashed var(--rule)",
        fontSize: 10.5, color: "var(--ink-3)", fontFamily: "var(--mono)",
      }}>
        <span>data quality <strong style={{ color: "var(--ink-1)" }}>{p.data_quality_score ? (p.data_quality_score * 100).toFixed(0) : '—'}%</strong></span>
        <span>confidence <strong style={{ color: "var(--ink-1)" }}>{p.confidence_level ? (p.confidence_level * 100).toFixed(0) : '—'}%</strong></span>
        <span style={{ marginLeft: "auto" }}>{p.generated_by || '—'}</span>
      </div>
    </div>
  );
}

function VitalsSparkPanel({ vitals }: { vitals: Record<string, VitalSpark> }) {
  const rows = [
    { key: "hr",   label: "Heart rate",    tone: "amber" },
    { key: "map",  label: "MAP",           tone: "red" },
    { key: "spo2", label: "SpO₂",          tone: "red" },
    { key: "rr",   label: "Respiratory",   tone: "amber" },
    { key: "lact", label: "Lactate",       tone: "red" },
    { key: "temp", label: "Temperature",   tone: "amber" },
  ];
  
  if (!vitals) {
    return null;
  }
  
  return (
    <div style={{
      background: "var(--surface-1)", border: "1px solid var(--rule)",
      borderRadius: 12, padding: 14,
    }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", marginBottom: 10 }}>
        <div style={{ fontSize: 10.5, color: "var(--ink-3)", letterSpacing: ".06em", textTransform: "uppercase" }}>Trend · last 8h</div>
        <div style={{ fontSize: 10.5, color: "var(--ink-3)", fontFamily: "var(--mono)" }}>q1h sample</div>
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "1fr", gap: 8 }}>
        {rows.map((r) => {
          const v = vitals[r.key];
          if (!v) return null;
          const color = r.tone === "red" ? "var(--risk-high-fg)" : "var(--risk-med-fg)";
          return (
            <div className="vitals-spark-row" key={r.key} style={{
              display: "grid", gridTemplateColumns: "75px 1fr 65px",
              alignItems: "center", gap: 8,
              padding: "6px 8px", borderRadius: 8,
              background: "var(--surface-2)",
            }}>
              <div>
                <div style={{ fontSize: 11, color: "var(--ink-2)", fontWeight: 500 }}>{r.label}</div>
                <div style={{ fontSize: 9.5, color: "var(--ink-4)", fontFamily: "var(--mono)" }}>nl {v.range || '—'}</div>
              </div>
              <Sparkline values={v.values || []} color={color} fill w={140} h={26} />
              <div style={{ textAlign: "right", fontFamily: "var(--mono)" }}>
                <span style={{ fontSize: 14, color: "var(--ink-1)", fontWeight: 500 }}>{v.current ?? '—'}</span>
                <span style={{ fontSize: 9.5, color: "var(--ink-3)", marginLeft: 3 }}>{v.unit || ''}</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function Timeline({ items }: { items: TimelineItem[] }) {
  const [selectedItem, setSelectedItem] = React.useState<TimelineItem | null>(null);
  const [dialogOpen, setDialogOpen] = React.useState(false);
  
  if (!items || items.length === 0) {
    return (
      <div style={{
        background: "var(--surface-1)", border: "1px solid var(--rule)",
        borderRadius: 12, padding: 14,
      }}>
        <div style={{ fontSize: 10.5, color: "var(--ink-3)", letterSpacing: ".06em", textTransform: "uppercase", marginBottom: 10 }}>Recent timeline</div>
        <div style={{ fontSize: 11.5, color: "var(--ink-3)", textAlign: "center", padding: "20px 0" }}>No timeline data available</div>
      </div>
    );
  }
  
  const kindMeta: Record<string, { dot: string; label: string; bg: string }> = {
    agent:  { dot: "var(--ag-trend-fg)", label: "Agent", bg: "var(--ag-trend-bg)" },
    med:    { dot: "var(--ag-conf-fg)",  label: "Med", bg: "var(--ag-conf-bg)" },
    note:   { dot: "var(--ink-3)",       label: "Note", bg: "var(--surface-2)" },
    lab:    { dot: "var(--ag-tb-fg)",    label: "Lab", bg: "var(--ag-tb-bg)" },
    vital:  { dot: "var(--risk-high-fg)",label: "Vital", bg: "var(--risk-high-bg)" },
    order:  { dot: "var(--ink-2)",       label: "Order", bg: "var(--surface-2)" },
    state_change: { dot: "var(--risk-med-fg)", label: "State", bg: "var(--risk-med-bg)" },
  };
  
  // Helper to get state-specific styling
  const getStateColor = (state: string) => {
    if (state === 'red') return 'var(--risk-high-fg)';
    if (state === 'yellow') return 'var(--risk-med-fg)';
    return 'var(--ink-3)'; // green
  };
  
  const handleItemClick = (item: TimelineItem) => {
    setSelectedItem(item);
    setDialogOpen(true);
  };
  
  return (
    <>
      <div style={{
        background: "var(--surface-1)", border: "1px solid var(--rule)",
        borderRadius: 12, padding: 14,
      }}>
        <div style={{ fontSize: 10.5, color: "var(--ink-3)", letterSpacing: ".06em", textTransform: "uppercase", marginBottom: 10 }}>Recent timeline · Click to view details</div>
        <div style={{ display: "flex", flexDirection: "column", gap: 0, position: "relative" }}>
          <div style={{ position: "absolute", left: 49, top: 6, bottom: 6, width: 1, background: "var(--rule)" }} />
          {items.map((it, i) => {
            const m = kindMeta[it.kind] || kindMeta.note;
            const isStateChange = it.kind === 'state_change';
            const stateColor = isStateChange && it.to_state ? getStateColor(it.to_state) : m.dot;
            
            return (
              <button
                key={i}
                onClick={() => handleItemClick(it)}
                className="timeline-row"
                style={{
                  all: "unset",
                  display: "grid",
                  gridTemplateColumns: "44px 16px 1fr",
                  alignItems: "center",
                  padding: "5px 0",
                  position: "relative",
                  cursor: "pointer",
                  background: isStateChange ? `${stateColor}08` : "transparent",
                  borderRadius: 6,
                  marginLeft: -4,
                  paddingLeft: 4,
                  paddingRight: 4,
                  transition: "background 0.15s ease",
                  border: isStateChange ? `1px solid ${stateColor}30` : "none",
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.background = isStateChange ? `${stateColor}15` : "var(--surface-2)";
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.background = isStateChange ? `${stateColor}08` : "transparent";
                }}
              >
                <span style={{ fontFamily: "var(--mono)", fontSize: 10.5, color: "var(--ink-3)" }}>{it.t}</span>
                <span style={{
                  width: isStateChange ? 10 : 8,
                  height: isStateChange ? 10 : 8,
                  borderRadius: 99,
                  background: stateColor,
                  justifySelf: "center",
                  boxShadow: isStateChange ? `0 0 0 3px var(--surface-1), 0 0 8px ${stateColor}60` : "0 0 0 3px var(--surface-1)",
                  transition: "box-shadow 0.15s ease",
                  border: isStateChange ? `2px solid var(--surface-1)` : "none",
                }} />
                <span style={{ fontSize: 11.5, color: "var(--ink-1)", textAlign: "left" }}>
                  <span style={{
                    color: isStateChange ? stateColor : "var(--ink-3)",
                    marginRight: 8,
                    fontVariant: "all-small-caps",
                    letterSpacing: ".05em",
                    fontWeight: isStateChange ? 600 : 400
                  }}>{m.label}</span>
                  {it.text}
                </span>
              </button>
            );
          })}
        </div>
      </div>

      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent style={{
          maxWidth: 500,
          background: "var(--surface-1)",
          border: "1px solid var(--rule)",
          borderRadius: 12,
          boxShadow: "0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)",
        }}>
          <DialogHeader>
            <DialogTitle style={{
              fontSize: 16,
              fontWeight: 600,
              color: "var(--ink-1)",
              marginBottom: 8,
            }}>
              Timeline Event Details
            </DialogTitle>
          </DialogHeader>
          {selectedItem && (
            <div style={{ padding: "8px 0" }}>
              {selectedItem.kind === 'state_change' && selectedItem.to_state ? (
                // Enhanced display for state changes
                <div style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 12,
                  marginBottom: 16,
                  padding: 14,
                  background: `${getStateColor(selectedItem.to_state)}10`,
                  borderRadius: 8,
                  border: `2px solid ${getStateColor(selectedItem.to_state)}`,
                  boxShadow: `0 0 0 4px ${getStateColor(selectedItem.to_state)}15`,
                }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 8, flex: 1 }}>
                    {selectedItem.from_state && (
                      <>
                        <span style={{
                          width: 14,
                          height: 14,
                          borderRadius: 99,
                          background: getStateColor(selectedItem.from_state),
                          flexShrink: 0,
                          boxShadow: `0 0 0 3px ${getStateColor(selectedItem.to_state)}10`,
                        }} />
                        <span style={{ fontSize: 18, color: "var(--ink-3)" }}>→</span>
                      </>
                    )}
                    <span style={{
                      width: 18,
                      height: 18,
                      borderRadius: 99,
                      background: getStateColor(selectedItem.to_state),
                      flexShrink: 0,
                      boxShadow: `0 0 8px ${getStateColor(selectedItem.to_state)}60`,
                      border: `2px solid var(--surface-1)`,
                    }} />
                    <div style={{ flex: 1 }}>
                      <div style={{
                        fontSize: 10,
                        color: getStateColor(selectedItem.to_state),
                        textTransform: "uppercase",
                        letterSpacing: ".08em",
                        marginBottom: 4,
                        fontWeight: 600,
                      }}>
                        State Change
                      </div>
                      <div style={{
                        fontFamily: "var(--mono)",
                        fontSize: 14,
                        color: "var(--ink-1)",
                        fontWeight: 600,
                      }}>
                        {selectedItem.t}
                      </div>
                    </div>
                  </div>
                </div>
              ) : (
                // Standard display for other events
                <div style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 12,
                  marginBottom: 16,
                  padding: 14,
                  background: kindMeta[selectedItem.kind]?.bg || "var(--surface-2)",
                  borderRadius: 8,
                  border: `2px solid ${kindMeta[selectedItem.kind]?.dot || "var(--rule)"}`,
                  boxShadow: `0 0 0 4px ${kindMeta[selectedItem.kind]?.dot || "var(--rule)"}15`,
                }}>
                  <span style={{
                    width: 14,
                    height: 14,
                    borderRadius: 99,
                    background: kindMeta[selectedItem.kind]?.dot || "var(--ink-3)",
                    flexShrink: 0,
                    boxShadow: `0 0 0 3px ${kindMeta[selectedItem.kind]?.bg || "var(--surface-2)"}`,
                  }} />
                  <div style={{ flex: 1 }}>
                    <div style={{
                      fontSize: 10,
                      color: "var(--ink-3)",
                      textTransform: "uppercase",
                      letterSpacing: ".08em",
                      marginBottom: 4,
                      fontWeight: 600,
                    }}>
                      {kindMeta[selectedItem.kind]?.label || selectedItem.kind}
                    </div>
                    <div style={{
                      fontFamily: "var(--mono)",
                      fontSize: 14,
                      color: "var(--ink-1)",
                      fontWeight: 600,
                    }}>
                      {selectedItem.t}
                    </div>
                  </div>
                </div>
              )}
              
              <div style={{ marginBottom: 12 }}>
                <div style={{
                  fontSize: 10.5,
                  color: "var(--ink-3)",
                  textTransform: "uppercase",
                  letterSpacing: ".06em",
                  marginBottom: 8,
                  fontWeight: 600,
                }}>
                  {selectedItem.kind === 'state_change' ? 'State Transition' : 'Event Description'}
                </div>
                <div style={{
                  fontSize: 13,
                  lineHeight: 1.6,
                  color: "var(--ink-1)",
                  padding: 14,
                  background: "var(--surface-2)",
                  borderRadius: 8,
                  border: "1px solid var(--rule)",
                }}>
                  {selectedItem.text}
                </div>
              </div>
              
              <div style={{
                fontSize: 11,
                color: "var(--ink-3)",
                fontStyle: "italic",
                marginTop: 16,
                paddingTop: 12,
                borderTop: "1px dashed var(--rule)",
                background: "var(--surface-2)",
                padding: 12,
                borderRadius: 6,
              }}>
                {selectedItem.kind === 'state_change'
                  ? `⚠️ Patient state changed at ${selectedItem.t}. This indicates a significant shift in the patient's condition.`
                  : `💡 This event occurred at ${selectedItem.t} and was recorded in the patient timeline.`
                }
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </>
  );
}

function ConfidenceMeter({ value, color }: { value: number; color: string }) {
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 10.5, color: "var(--ink-3)", fontFamily: "var(--mono)" }}>
      <span>conf</span>
      <div className="confidence-meter-bar" style={{ width: 60, height: 4, background: "var(--rule)", borderRadius: 99, overflow: "hidden" }}>
        <div style={{ width: `${value * 100}%`, height: "100%", background: color }} />
      </div>
      <span>{(value * 100).toFixed(0)}%</span>
    </div>
  );
}




// Trend agent body
function TrendBody({ report }: { report: TrendReport }) {
  if (!report) return null;
  
  return (
    <>
      <div className="responsive-table-block" style={{ marginBottom: 12 }}>
        <div style={{ fontSize: 10.5, color: "var(--ink-3)", letterSpacing: ".06em", textTransform: "uppercase", marginBottom: 6 }}>Vital trends</div>
        <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 11.5 }}>
          <thead>
            <tr style={{ color: "var(--ink-3)", textAlign: "left", fontSize: 10, letterSpacing: ".05em", textTransform: "uppercase" }}>
              <th style={{ padding: "4px 6px 4px 0", fontWeight: 500 }}>Vital</th>
              <th style={{ padding: "4px 6px", fontWeight: 500 }}>Direction</th>
              <th style={{ padding: "4px 6px", fontWeight: 500, textAlign: "right" }}>Slope/h</th>
              <th style={{ padding: "4px 6px", fontWeight: 500, textAlign: "right" }}>Accel</th>
              <th style={{ padding: "4px 0 4px 6px", fontWeight: 500 }}>Concern</th>
            </tr>
          </thead>
          <tbody>
            {report.trends?.map((tr, i) => (
              <tr key={i} style={{ borderTop: "1px solid var(--rule-soft)" }}>
                <td style={{ padding: "6px 6px 6px 0", color: "var(--ink-1)", fontWeight: 500 }}>{tr.vital_name}</td>
                <td style={{ padding: "6px 6px", color: "var(--ink-2)" }}>
                  <TrendArrow direction={tr.direction} /> <span style={{ fontVariant: "all-small-caps", letterSpacing: ".04em", marginLeft: 4 }}>{tr.direction}</span>
                </td>
                <td style={{ padding: "6px 6px", fontFamily: "var(--mono)", textAlign: "right", color: "var(--ink-2)" }}>
                  {tr.slope > 0 ? "+" : ""}{tr.slope.toFixed(2)}
                </td>
                <td style={{ padding: "6px 6px", fontFamily: "var(--mono)", textAlign: "right", color: "var(--ink-3)" }}>
                  {tr.acceleration > 0 ? "+" : ""}{tr.acceleration.toFixed(2)}
                </td>
                <td style={{ padding: "6px 0 6px 6px" }}>
                  <LevelBadge level={tr.concern_level} kind="concern" color={tr.concern_level >= 3 ? "var(--risk-high-fg)" : tr.concern_level === 2 ? "var(--risk-med-fg)" : "var(--ink-3)"} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div style={{ marginBottom: 12 }}>
        <div style={{ fontSize: 10.5, color: "var(--ink-3)", letterSpacing: ".06em", textTransform: "uppercase", marginBottom: 6 }}>LLM reasoning</div>
        <div style={{ fontSize: 12, lineHeight: 1.5, color: "var(--ink-1)" }}>{report.llm_reasoning || '—'}</div>
      </div>

      {report.evidence && report.evidence.length > 0 && (
        <div className="responsive-table-block">
          <div style={{ fontSize: 10.5, color: "var(--ink-3)", letterSpacing: ".06em", textTransform: "uppercase", marginBottom: 6 }}>Evidence</div>
          <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 11.5 }}>
            <tbody>
              {report.evidence.map((e, i) => (
              <tr key={i} style={{ borderTop: i ? "1px solid var(--rule-soft)" : "none" }}>
                <td style={{ padding: "6px 0", fontFamily: "var(--mono)", color: "var(--ink-3)", width: 80 }}>{e.t}</td>
                <td style={{ padding: "6px 0", color: "var(--ink-2)", width: 130 }}>{e.k}</td>
                <td style={{ padding: "6px 0", color: "var(--ink-1)", fontFamily: "var(--mono)" }}>{e.v}</td>
              </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </>
  );
}

function ConflictBody({ report, color }: { report: ConflictReport; color: string }) {
  if (!report) return null;
  
  return (
    <>
      <div style={{ marginBottom: 12 }}>
        <div style={{ fontSize: 10.5, color: "var(--ink-3)", letterSpacing: ".06em", textTransform: "uppercase", marginBottom: 6 }}>LLM reasoning</div>
        <div style={{ fontSize: 12, lineHeight: 1.5, color: "var(--ink-1)" }}>{report.llm_reasoning || '—'}</div>
      </div>

      {report.conflicts?.map((c, i) => (
        <div key={i} style={{
          marginTop: 10, padding: "10px 12px", borderRadius: 8,
          background: "var(--surface-1)", border: "1px solid var(--rule)",
          borderLeft: `3px solid ${color}`,
        }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", gap: 10, marginBottom: 4 }}>
            <span style={{ fontFamily: "var(--mono)", fontSize: 11.5, fontWeight: 600, color: color }}>
              {c.conflict_type}
            </span>
            <LevelBadge level={c.severity} kind="severity" color={c.severity >= 3 ? "var(--risk-high-fg)" : color} />
          </div>
          <div style={{ fontSize: 12, color: "var(--ink-1)", marginBottom: 6 }}>{c.description}</div>
          <div style={{ display: "flex", flexWrap: "wrap", gap: 4, marginBottom: 6 }}>
            {c.vitals_involved && c.vitals_involved.map((v, j) => (
              <Chip key={"v"+j} tone="neutral">vital · {v}</Chip>
            ))}
            {c.labs_involved && c.labs_involved.map((l, j) => (
              <Chip key={"l"+j} tone="amber">lab · {l}</Chip>
            ))}
          </div>
          <div style={{ fontSize: 11.5, color: "var(--ink-2)", fontStyle: "italic" }}>{c.clinical_significance}</div>

          {c.evidence && Array.isArray(c.evidence) && (
            <div style={{ marginTop: 10 }}>
              <div style={{ fontSize: 10.5, color: "var(--ink-3)", letterSpacing: ".06em", textTransform: "uppercase", marginBottom: 4 }}>Evidence</div>
              <table className="agent-evidence-table" style={{ width: "100%", borderCollapse: "collapse", fontSize: 11.5 }}>
                <tbody>
                  {c.evidence.map((e, j) => (
                    <tr key={j} style={{ borderTop: j ? "1px solid var(--rule-soft)" : "none" }}>
                      <td style={{ padding: "5px 0", fontFamily: "var(--mono)", color: "var(--ink-3)", width: 70 }}>{e.t}</td>
                      <td style={{ padding: "5px 0", color: "var(--ink-2)", width: 90 }}>{e.k}</td>
                      <td style={{ padding: "5px 0", color: "var(--ink-1)", fontFamily: "var(--mono)" }}>{e.v}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      ))}
    </>
  );
}

function TimeBombBody({ report }: { report: TimeBombReport }) {
  if (!report) return null;
  
  const fmtTime = (mins: number) => {
    if (mins == null) return "—";
    const sign = mins < 0 ? "+" : "−";
    const abs = Math.abs(mins);
    const h = Math.floor(abs / 60);
    const m = abs % 60;
    return `${sign}${h ? h + "h " : ""}${m}m`;
  };
  return (
    <>
      <div style={{ marginBottom: 12 }}>
        <div style={{ fontSize: 10.5, color: "var(--ink-3)", letterSpacing: ".06em", textTransform: "uppercase", marginBottom: 6 }}>LLM reasoning</div>
        <div style={{ fontSize: 12, lineHeight: 1.5, color: "var(--ink-1)" }}>{report.llm_reasoning || '—'}</div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: 8 }}>
        {report.timebombs?.map((tb, i) => {
          const overdue = tb.time_until_event != null && tb.time_until_event < 0;
          const tone = tb.urgency >= 3 ? "var(--risk-high-fg)" : tb.urgency === 2 ? "var(--risk-med-fg)" : "var(--ink-3)";
          return (
        <div className="timebomb-card" key={i} style={{
              padding: "10px 12px", borderRadius: 8,
              background: "var(--surface-1)", border: "1px solid var(--rule)",
              borderLeft: `3px solid ${tone}`,
            }}>
              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 4 }}>
                <span style={{ fontFamily: "var(--mono)", fontSize: 11, color: tone, fontWeight: 600 }}>{tb.timebomb_type}</span>
                <LevelBadge level={tb.urgency} kind="urgency" color={tone} />
              </div>
              <div style={{
                fontFamily: "var(--mono)", fontSize: 16, fontWeight: 600,
                color: overdue ? "var(--risk-high-fg)" : "var(--ink-1)",
                marginBottom: 4,
              }}>
                {fmtTime(tb.time_until_event)}
                {overdue && <span style={{ fontSize: 9.5, marginLeft: 6, color: "var(--risk-high-fg)" }}>OVERDUE</span>}
              </div>
              <div style={{ fontSize: 11.5, color: "var(--ink-1)", marginBottom: 4, lineHeight: 1.4 }}>{tb.description}</div>
              <div style={{ fontSize: 10.5, color: "var(--ink-3)", fontStyle: "italic" }}>→ {tb.action_required}</div>
            </div>
          );
        })}
      </div>
    </>
  );
}

interface AgentCardProps {
  kind: "trend" | "conflict" | "timebomb";
  title: string;
  desc: string;
  glyph: string;
  summary: string;
  body: React.ReactNode;
  confidence: number;
  lastRun: string;
  level: number;
  levelKind: "concern" | "severity" | "urgency";
  agentVisual: string;
  defaultOpen?: boolean;
}

function AgentCard({ kind, title, desc, glyph, summary, body, confidence, lastRun, level, levelKind, agentVisual, defaultOpen }: AgentCardProps) {
  const [open, setOpen] = React.useState(defaultOpen);
  const META = {
    trend:    { color: "var(--ag-trend-fg)", bg: "var(--ag-trend-bg)",  brd: "var(--ag-trend-brd)" },
    conflict: { color: "var(--ag-conf-fg)",  bg: "var(--ag-conf-bg)",   brd: "var(--ag-conf-brd)" },
    timebomb: { color: "var(--ag-tb-fg)",    bg: "var(--ag-tb-bg)",     brd: "var(--ag-tb-brd)" },
  };
  const m = META[kind];

  return (
    <div style={{
      background: agentVisual === "tinted" ? m.bg : "var(--surface-1)",
      border: `1px solid ${agentVisual === "tinted" ? m.brd : "var(--rule)"}`,
      borderLeft: `4px solid ${m.color}`,
      borderRadius: 10, overflow: "hidden",
    }}>
      <button className="agent-card-toggle" onClick={() => setOpen(!open)} style={{
        all: "unset", cursor: "pointer", display: "flex", alignItems: "center",
        gap: 12, padding: "12px 14px", width: "100%", boxSizing: "border-box",
      }}>
        <span style={{
          width: 28, height: 28, borderRadius: 6, flexShrink: 0,
          background: m.color, color: agentVisual === "tinted" ? m.bg : "var(--surface-1)",
          display: "grid", placeItems: "center",
          fontFamily: "var(--mono)", fontWeight: 700, fontSize: 13,
        }}>{glyph}</span>
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ display: "flex", alignItems: "baseline", gap: 8, flexWrap: "wrap" }}>
            <span style={{ fontSize: 13, fontWeight: 600, color: m.color }}>{title}</span>
            <span style={{ fontSize: 10.5, color: "var(--ink-3)" }}>{desc}</span>
            <LevelBadge level={level} kind={levelKind} color={m.color} />
          </div>
          <div style={{ fontSize: 11.5, color: "var(--ink-1)", marginTop: 2, lineHeight: 1.4 }}>{summary}</div>
        </div>
        <div className="agent-card-meta" style={{ display: "flex", flexDirection: "column", alignItems: "flex-end", gap: 4 }}>
          <ConfidenceMeter value={confidence} color={m.color} />
          <span style={{ fontSize: 10, color: "var(--ink-3)", fontFamily: "var(--mono)" }}>{lastRun}</span>
        </div>
        <span style={{
          marginLeft: 6, color: m.color, fontFamily: "var(--mono)", fontSize: 11,
          transform: open ? "rotate(90deg)" : "rotate(0)", transition: "transform .15s",
        }}>▸</span>
      </button>

      {open && (
        <div style={{
          padding: "12px 14px 14px 14px",
          borderTop: `1px dashed ${agentVisual === "tinted" ? m.brd : "var(--rule)"}`,
        }}>
          {body}

          {/* Removed Acknowledge/Snooze/Trace buttons per request */}
        </div>
      )}
    </div>
  );
}

const btnTiny: React.CSSProperties = {
  padding: "5px 10px", border: "1px solid var(--rule)", background: "var(--surface-1)",
  color: "var(--ink-2)", borderRadius: 6, fontSize: 11, fontWeight: 500, cursor: "pointer",
};

interface DetailHeaderProps {
  p: PatientDetailData;
  onBack: () => void;
  refresh?: boolean;
}

function DetailHeader({ p, onBack, refresh }: DetailHeaderProps) {
  const [tick, setTick] = React.useState(0);
  const [isDark, setIsDark] = React.useState(true);
  
  React.useEffect(() => {
    if (!refresh) return;
    const id = setInterval(() => setTick((x) => x + 1), 1000);
    return () => clearInterval(id);
  }, [refresh]);
  
  React.useEffect(() => {
    // Initialize from HTML data-theme attribute
    const htmlElement = document.documentElement;
    const theme = htmlElement.getAttribute('data-theme');
    setIsDark(theme === 'dark');
  }, []);
  
  const toggleDarkMode = (checked: boolean) => {
    const htmlElement = document.documentElement;
    if (checked) {
      // Switch is ON = Dark mode
      htmlElement.setAttribute('data-theme', 'dark');
      setIsDark(true);
    } else {
      // Switch is OFF = Light mode
      htmlElement.setAttribute('data-theme', 'light');
      setIsDark(false);
    }
  };
  
  // Spec recommends 60s auto-refresh.
  const seconds = (tick % 60);
  
  if (!p) return null;
  
  return (
    <header className="detail-header" style={{
      display: "flex", alignItems: "center", gap: 14,
      padding: "10px 20px",
      borderBottom: "1px solid var(--rule)", background: "var(--surface-1)",
    }}>
      <button onClick={onBack} style={{
        all: "unset", cursor: "pointer", display: "flex", alignItems: "center", gap: 6,
        padding: "6px 10px", borderRadius: 7, background: "var(--chip-bg)",
        color: "var(--ink-2)", fontSize: 11.5, fontWeight: 500,
      }}>
        <span style={{ fontFamily: "var(--mono)" }}>←</span> All patients
      </button>

      <div className="detail-patient-meta" style={{ display: "flex", alignItems: "baseline", gap: 10 }}>
        <span style={{ fontFamily: "var(--mono)", fontSize: 11.5, color: "var(--ink-3)" }}>{p.careunit_short || '—'}</span>
        <span style={{ fontSize: 13, fontWeight: 600, fontFamily: "var(--mono)" }}>Patient ID {p.patient_id || '—'}</span>
        <span style={{ fontFamily: "var(--mono)", fontSize: 11, color: "var(--ink-3)" }}>stay {p.stay_id || '—'} · {p.age || '—'}{p.gender || ''}</span>
      </div>

      <div style={{ flex: 1 }} />

      <div style={{
        display: "flex",
        alignItems: "center",
        gap: 8,
        padding: "6px 12px",
        background: "var(--chip-bg)",
        borderRadius: 8,
        border: "1px solid var(--rule)",
      }}>
        <svg
          width="14"
          height="14"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
          style={{
            color: isDark ? "var(--ink-3)" : "var(--ink-1)",
            transition: "color 0.2s ease"
          }}
        >
          <circle cx="12" cy="12" r="5"></circle>
          <line x1="12" y1="1" x2="12" y2="3"></line>
          <line x1="12" y1="21" x2="12" y2="23"></line>
          <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line>
          <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line>
          <line x1="1" y1="12" x2="3" y2="12"></line>
          <line x1="21" y1="12" x2="23" y2="12"></line>
          <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line>
          <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>
        </svg>
        
        <Switch
          checked={isDark}
          onCheckedChange={toggleDarkMode}
          size="sm"
          aria-label="Toggle dark mode"
        />
        
        <svg
          width="14"
          height="14"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
          style={{
            color: isDark ? "var(--ink-1)" : "var(--ink-3)",
            transition: "color 0.2s ease"
          }}
        >
          <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>
        </svg>
      </div>

      <div className="detail-live-status" style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 11, color: "var(--ink-3)" }}>
        <span style={{
          width: 7, height: 7, borderRadius: 99, background: "var(--ok)",
          boxShadow: "0 0 0 3px color-mix(in oklch, var(--ok) 22%, transparent)",
          animation: "pulse 1.6s ease-in-out infinite",
        }} />
        <span style={{ fontFamily: "var(--mono)" }}>GET /patient/{p.patient_id} · {60 - seconds}s</span>
      </div>
    </header>
  );
}

interface PatientDetailProps {
  patient: PatientDetailData;
  onBack: () => void;
  agentVisual: string;
}

function PatientDetail({ patient: p, onBack, agentVisual }: PatientDetailProps) {
  // Guard against undefined patient data
  if (!p) {
    return (
      <div className="detail-shell" style={{ display: "flex", flexDirection: "column", height: "100vh", background: "var(--surface-0)", alignItems: "center", justifyContent: "center" }}>
        <div style={{ fontSize: 14, color: "var(--ink-3)" }}>Loading patient data...</div>
      </div>
    );
  }
  
  return (
    <div className="detail-shell" style={{ display: "flex", flexDirection: "column", height: "100vh", background: "var(--surface-0)" }}>
      <DetailHeader p={p} onBack={onBack} refresh={true} />
      <div className="detail-layout" style={{
        flex: 1, display: "grid", gridTemplateColumns: "minmax(380px, 460px) 1fr",
        gap: 0, overflow: "hidden",
      }}>
        {/* LEFT: SBAR + vitals + timeline */}
        <div className="detail-summary-pane" style={{
          padding: 16, overflow: "auto",
          borderRight: "1px solid var(--rule)", background: "var(--surface-2)",
          display: "flex", flexDirection: "column", gap: 14,
        }}>
          <SbarCard p={p} />
          {p.vitalsSpark && <VitalsSparkPanel vitals={p.vitalsSpark} />}
          {p.timeline && <Timeline items={p.timeline} />}
        </div>

        {/* RIGHT: agent reasoning panels */}
        <div className="detail-agent-pane" style={{ overflow: "auto", padding: 18 }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-end", gap: 12, marginBottom: 14, flexWrap: "wrap" }}>
            <div style={{ minWidth: 0 }}>
              <div style={{ fontSize: 10, color: "var(--ink-3)", letterSpacing: ".06em", textTransform: "uppercase" }}>Coordinator synthesis</div>
              <h3 style={{ fontSize: 15, fontWeight: 600, margin: "2px 0 0" }}>Agent reasoning</h3>
              <div style={{ fontSize: 10.5, color: "var(--ink-3)", marginTop: 2 }}>3 layer-1 agents</div>
            </div>
            <div style={{ fontSize: 11, color: "var(--ink-3)", fontFamily: "var(--mono)", whiteSpace: "nowrap" }}>
              risk <span style={{ color: "var(--risk-high-fg)", fontWeight: 600 }}>{p.risk_score?.toFixed(1) ?? '—'}</span>
              <span style={{ margin: "0 8px", color: "var(--ink-4)" }}>·</span>
              conf <span style={{ color: "var(--ink-1)", fontWeight: 600 }}>{p.confidence_level ? (p.confidence_level * 100).toFixed(0) : '—'}%</span>
            </div>
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
            {p.trend_report && (
              <AgentCard
                kind="trend"
                title="Trend Agent"
                desc="Vital-sign trajectories"
                glyph="T"
                summary={p.trend_report.summary || 'No data available'}
                confidence={p.trend_report.confidence ?? 0}
                lastRun={p.trend_report.last_run_label || '—'}
                level={p.trend_report.overall_concern ?? 0}
                levelKind="concern"
                agentVisual={agentVisual}
                defaultOpen={true}
                body={<TrendBody report={p.trend_report} />}
              />
            )}
            {p.conflict_report && (
              <AgentCard
                kind="conflict"
                title="Lab-Vitals Conflict Agent"
                desc="Cross-signal divergence"
                glyph="C"
                summary={p.conflict_report.summary || 'No data available'}
                confidence={p.conflict_report.confidence ?? 0}
                lastRun={p.conflict_report.last_run_label || '—'}
                level={p.conflict_report.overall_severity ?? 0}
                levelKind="severity"
                agentVisual={agentVisual}
                defaultOpen={false}
                body={<ConflictBody report={p.conflict_report} color="var(--ag-conf-fg)" />}
              />
            )}
            {p.timebomb_report && (
              <AgentCard
                kind="timebomb"
                title="Time Bomb Agent"
                desc="Forward-looking risks"
                glyph="B"
                summary={p.timebomb_report.summary || 'No data available'}
                confidence={p.timebomb_report.confidence ?? 0}
                lastRun={p.timebomb_report.last_run_label || '—'}
                level={p.timebomb_report.overall_urgency ?? 0}
                levelKind="urgency"
                agentVisual={agentVisual}
                defaultOpen={false}
                body={<TimeBombBody report={p.timebomb_report} />}
              />
            )}
          </div>

          {/* Data-quality footer */}
          <div className="data-quality-grid" style={{
            marginTop: 16, padding: 12, borderRadius: 10,
            border: "1px solid var(--rule)", background: "var(--surface-1)",
            display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 12,
          }}>
            {p.data_quality && (
              <>
                <div>
                  <div style={{ fontSize: 10, color: "var(--ink-3)", letterSpacing: ".06em", textTransform: "uppercase" }}>Completeness</div>
                  <div style={{ fontFamily: "var(--mono)", fontSize: 14, fontWeight: 600 }}>
                    {p.data_quality.completeness_score ? (p.data_quality.completeness_score * 100).toFixed(1) : '—'}%
                  </div>
                  <div style={{ fontSize: 10.5, color: "var(--ink-3)" }}>
                    {p.data_quality.actual_readings ?? '—'}/{p.data_quality.total_expected_readings ?? '—'} readings
                  </div>
                </div>
                <div>
                  <div style={{ fontSize: 10, color: "var(--ink-3)", letterSpacing: ".06em", textTransform: "uppercase" }}>Missing vitals</div>
                  <div style={{ fontFamily: "var(--mono)", fontSize: 12, color: "var(--ink-1)" }}>
                    {p.data_quality.missing_vitals?.length ? p.data_quality.missing_vitals.join(", ") : "—"}
                  </div>
                </div>
                <div>
                  <div style={{ fontSize: 10, color: "var(--ink-3)", letterSpacing: ".06em", textTransform: "uppercase" }}>Missing labs</div>
                  <div style={{ fontFamily: "var(--mono)", fontSize: 12, color: "var(--ink-1)" }}>
                    {p.data_quality.missing_labs?.length ? p.data_quality.missing_labs.join(", ") : "—"}
                  </div>
                </div>
                <div>
                  <div style={{ fontSize: 10, color: "var(--ink-3)", letterSpacing: ".06em", textTransform: "uppercase" }}>Data gaps</div>
                  <div style={{ fontFamily: "var(--mono)", fontSize: 12, color: "var(--ink-1)" }}>
                    {p.data_quality.data_gaps_minutes?.length ? p.data_quality.data_gaps_minutes.map(m => m + "m").join(", ") : "—"}
                  </div>
                </div>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default PatientDetail;
