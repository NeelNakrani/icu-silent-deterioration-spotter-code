
interface AgentBadgeProps {
  kind: "trend" | "conflict" | "timebomb";
  count: number;
}

export function AgentBadge({ kind, count }: AgentBadgeProps) {
  if (!count) return <span style={{ width: 18, height: 18, display: "inline-block" }} />;
  
  const tones = {
    trend:    { bg: "var(--ag-trend-bg)",  fg: "var(--ag-trend-fg)",  ch: "T" },
    conflict: { bg: "var(--ag-conf-bg)",   fg: "var(--ag-conf-fg)",   ch: "C" },
    timebomb: { bg: "var(--ag-tb-bg)",     fg: "var(--ag-tb-fg)",     ch: "B" },
  };
  const t = tones[kind];
  
  return (
    <span style={{
      display: "inline-flex", alignItems: "center", justifyContent: "center",
      width: 18, height: 18, borderRadius: "var(--rounded-xs)", background: t.bg, color: t.fg,
      fontFamily: "var(--mono)", fontSize: 10, fontWeight: 600, letterSpacing: 0,
      position: "relative",
    }} title={`${kind} flags: ${count}`}>
      {t.ch}
      {count > 1 && (
        <span style={{
          position: "absolute", top: -3, right: -4, minWidth: 11, height: 11,
          padding: "0 2px", background: t.fg, color: "var(--surface-1)",
          borderRadius: "var(--rounded-full)", fontSize: 8, fontWeight: 700, lineHeight: "11px",
        }}>{count}</span>
      )}
    </span>
  );
}
