import type { RiskLevel } from '../types/icu';

interface RiskPillProps {
  risk_level: RiskLevel;
  score: number | string;
  delta?: number | null;
  size?: "md" | "lg";
}

export function RiskPill({ risk_level, score, delta, size = "md" }: RiskPillProps) {
  const tones = {
    red:    { bg: "var(--risk-high-bg)", fg: "var(--risk-high-fg)", brd: "var(--risk-high-brd)" },
    yellow: { bg: "var(--risk-med-bg)",  fg: "var(--risk-med-fg)",  brd: "var(--risk-med-brd)" },
    green:  { bg: "var(--risk-low-bg)",  fg: "var(--risk-low-fg)",  brd: "var(--risk-low-brd)" },
  };
  const t = tones[risk_level] || tones.green;
  const px = size === "lg" ? "8px 12px" : "3px 8px";
  const fs = size === "lg" ? 13 : 11;
  const arrow = delta && delta > 0 ? "↑" : delta && delta < 0 ? "↓" : "·";
  const scoreStr = typeof score === "number" ? score.toFixed(1) : score;
  
  return (
    <span style={{
      display: "inline-flex", alignItems: "center", gap: 8,
      padding: px, background: t.bg, color: t.fg,
      border: `1px solid ${t.brd}`, borderRadius: "var(--rounded-full)", fontSize: fs,
      fontWeight: 600, fontVariantNumeric: "tabular-nums", letterSpacing: ".01em",
    }}>
      <span style={{ fontFamily: "var(--mono)", fontSize: fs + 1 }}>{scoreStr}</span>
      {delta !== 0 && delta != null && (
        <span style={{ opacity: 0.78, fontSize: fs - 1 }}>
          {arrow}{Math.abs(delta)}
        </span>
      )}
    </span>
  );
}
