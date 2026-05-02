export * from './RiskPill';
export * from './Chip';
export * from './TrendArrow';
export * from './VitalCell';
export * from './AgentBadge';
export * from './Sparkline';
export * from './LevelBadge';
export * from './TweaksPanel';

export function concernTone(level: number): "red" | "amber" | "neutral" {
  if (level >= 3) return "red";
  if (level === 2) return "amber";
  if (level === 1) return "neutral";
  return "neutral";
}
