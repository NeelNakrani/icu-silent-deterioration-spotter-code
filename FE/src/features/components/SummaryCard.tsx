import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

type Props = {
  label: string;
  value: number;
  type?: "default" | "vitals" | "training";
};

export default function SummaryCard({ label, value, type = "default" }: Props) {
  const toneByLabel: Record<string, string> = {
    "Critical Patients": "border-l-critical",
    "Active Alerts": "border-l-warning",
    "Pending Reviews": "border-l-highlight",
    "System Uptime": "border-l-success",
  };

  const tone = toneByLabel[label] ?? "border-l-accent";

  return (
    <Card
      size="sm"
      className={`bg-bg-panel border border-border-subtle/80 shadow-medical transition-colors hover:bg-bg-elevated/80 border-l-4 ${tone}`}
      data-card-type={type}
    >
      <CardHeader className="gap-1">
        <CardTitle className="text-[10px] font-semibold uppercase tracking-[0.24em] text-text-secondary">
          {label}
        </CardTitle>
      </CardHeader>
      <CardContent className="flex items-end justify-between pt-0">
        <div className="text-3xl font-semibold text-text-primary">
          {value.toLocaleString()}
        </div>
        <span className="text-[10px] text-text-muted">+0%</span>
      </CardContent>
    </Card>
  );
}