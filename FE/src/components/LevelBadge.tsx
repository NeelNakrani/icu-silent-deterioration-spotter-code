
interface LevelBadgeProps {
  level: number;
  kind?: "concern" | "severity" | "urgency";
  color: string;
}

export function LevelBadge({ level, kind = "concern", color }: LevelBadgeProps) {
  const labels = {
    concern:  ["none", "mild", "moderate", "severe"],
    severity: ["none", "mild", "moderate", "severe"],
    urgency:  ["low",  "med",  "high",     "critical"],
  };
  const txt = labels[kind][level] || "—";
  
  return (
    <span style={{
      fontFamily: "var(--mono)", fontSize: 10, fontWeight: 600,
      padding: "2px 7px", borderRadius: "var(--rounded-full)",
      color: color, border: `1px solid ${color}`, background: "transparent",
      textTransform: "uppercase", letterSpacing: ".04em",
    }}>L{level} · {txt}</span>
  );
}
