type Props = {
  label: string;
  value: number;
  type?: 'default' | 'vitals' | 'training'; 
};

export default function SummaryCard({ label, value, type = 'default' }: Props) {
  return (
    <div className="
      bg-bg-panel 
      border border-border-subtle 
      border-l-4 border-l-accent 
      rounded-lg 
      p-5 
      text-left 
      transition-all 
      duration-200 
      hover:bg-bg-elevated 
      hover:-translate-y-1 
      hover:shadow-lg
    ">
      <h3 className="text-xs font-bold uppercase tracking-widest text-text-secondary mb-2">
        {label}
      </h3>
      <div className="flex items-baseline gap-2">
        <p className="text-3xl font-bold text-text-primary">
          {value.toLocaleString()}
        </p>

        <span className="text-[10px] text-text-muted font-medium">
          +0%
        </span>
      </div>
    </div>
  );
}