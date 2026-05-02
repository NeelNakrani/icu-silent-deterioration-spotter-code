import type { TrendDirection } from '../types/icu';
import { TrendArrow } from './TrendArrow';

interface VitalCellProps {
  label: string;
  value: number | string;
  unit?: string;
  direction?: TrendDirection;
}

export function VitalCell({ label, value, unit, direction }: VitalCellProps) {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 1, minWidth: 44 }}>
      <span style={{ fontSize: 9.5, color: "var(--ink-3)", letterSpacing: ".06em", textTransform: "uppercase" }}>{label}</span>
      <span style={{ display: "flex", alignItems: "baseline", gap: 4, fontFamily: "var(--mono)", fontVariantNumeric: "tabular-nums" }}>
        <span style={{ fontSize: 13, color: "var(--ink-1)", fontWeight: 500 }}>{value}</span>
        {unit && <span style={{ fontSize: 9, color: "var(--ink-3)" }}>{unit}</span>}
        {direction && <TrendArrow direction={direction} />}
      </span>
    </div>
  );
}
