import React from 'react';

interface KpiCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon?: React.ReactNode;
  badge?: string;
  badgeColor?: 'emerald' | 'amber' | 'teal' | 'rose' | 'earth';
  className?: string;
}

export const KpiCard: React.FC<KpiCardProps> = ({
  title,
  value,
  subtitle,
  icon,
  badge,
  badgeColor = 'emerald',
  className = '',
}) => {
  const badgeStyles = {
    emerald: 'bg-[#D1FAE5] text-[#065F46] border-[#A7F3D0]',
    amber: 'bg-[#FEF3C7] text-[#B45309] border-[#FDE68A]',
    teal: 'bg-[#CCFBF1] text-[#0F766E] border-[#99F6E4]',
    rose: 'bg-[#FFE4E6] text-[#BE123C] border-[#FECDD3]',
    earth: 'bg-[#F6E7DA] text-[#9A5B2F] border-[#E8CEB8]',
  };

  return (
    <div
      className={`bg-white rounded-2xl border border-[#DCE5DC] p-5 shadow-card hover:shadow-card-hover transition-all duration-200 ${className}`}
    >
      <div className="flex items-start justify-between">
        <p className="text-xs font-semibold text-[#7A8E80] uppercase tracking-wider">{title}</p>
        {icon && (
          <div className="p-2 rounded-xl bg-[#F6F8F4] border border-[#DCE5DC] text-[#047857]">
            {icon}
          </div>
        )}
      </div>

      <div className="mt-3 flex items-baseline gap-2">
        <span className="text-2xl lg:text-3xl font-extrabold text-[#14231A] tracking-tight tabular-nums">
          {value}
        </span>
        {badge && (
          <span
            className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${badgeStyles[badgeColor]}`}
          >
            {badge}
          </span>
        )}
      </div>

      {subtitle && (
        <p className="mt-2 text-xs font-medium text-[#4A5F52] flex items-center gap-1">
          {subtitle}
        </p>
      )}
    </div>
  );
};
