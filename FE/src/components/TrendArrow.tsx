import type { TrendDirection } from '../types/icu';

interface TrendArrowProps {
  direction: TrendDirection;
}

export function TrendArrow({ direction }: TrendArrowProps) {
  const map = {
    rising:   { sym: "↑", col: "var(--trend-up)" },
    falling:  { sym: "↓", col: "var(--trend-down)" },
    stable:   { sym: "·", col: "var(--ink-3)" },
    volatile: { sym: "⇅", col: "var(--risk-med-fg)" },
  };
  const m = map[direction] || map.stable;
  
  return <span style={{ color: m.col, fontFamily: "var(--mono)", fontSize: 11 }}>{m.sym}</span>;
}
