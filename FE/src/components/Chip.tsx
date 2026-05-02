
interface ChipProps {
  tone?: "neutral" | "red" | "amber" | "blue" | "orange" | "green";
  children: React.ReactNode;
  dot?: boolean;
  intense?: boolean;
}

export function Chip({ tone = "neutral", children, dot = false, intense = false }: ChipProps) {
  const tones = {
    neutral: { bg: "var(--chip-bg)",        fg: "var(--ink-2)",        brd: "var(--chip-brd)" },
    red:     { bg: "var(--risk-high-bg)",   fg: "var(--risk-high-fg)", brd: "var(--risk-high-brd)" },
    amber:   { bg: "var(--risk-med-bg)",    fg: "var(--risk-med-fg)",  brd: "var(--risk-med-brd)" },
    blue:    { bg: "var(--ag-trend-bg)",    fg: "var(--ag-trend-fg)",  brd: "var(--ag-trend-brd)" },
    orange:  { bg: "var(--ag-conf-bg)",     fg: "var(--ag-conf-fg)",   brd: "var(--ag-conf-brd)" },
    green:   { bg: "var(--risk-low-bg)",    fg: "var(--risk-low-fg)",  brd: "var(--risk-low-brd)" },
  };
  const t = tones[tone] || tones.neutral;
  
  return (
    <span style={{
      display: "inline-flex", alignItems: "center", gap: 6,
      padding: intense ? "3px 9px" : "2px 8px",
      background: t.bg, color: t.fg, border: `1px solid ${t.brd}`,
      borderRadius: 6, fontSize: 11, fontWeight: 500, lineHeight: 1.4,
      letterSpacing: ".005em", whiteSpace: "nowrap",
    }}>
      {dot && <span style={{ width: 5, height: 5, borderRadius: 99, background: t.fg, opacity: .8 }} />}
      {children}
    </span>
  );
}
