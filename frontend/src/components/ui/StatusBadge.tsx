import React from 'react';

interface StatusBadgeProps {
  status: string;
  variant?: 'emerald' | 'amber' | 'rose' | 'teal' | 'gray';
  size?: 'sm' | 'md';
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({
  status,
  variant = 'emerald',
  size = 'md',
}) => {
  const styles = {
    emerald: 'bg-[#D1FAE5] text-[#065F46] border-[#A7F3D0]',
    amber: 'bg-[#FEF3C7] text-[#B45309] border-[#FDE68A]',
    rose: 'bg-[#FFE4E6] text-[#BE123C] border-[#FECDD3]',
    teal: 'bg-[#CCFBF1] text-[#0F766E] border-[#99F6E4]',
    gray: 'bg-[#EEF3EC] text-[#4A5F52] border-[#DCE5DC]',
  };

  const sizeClasses = size === 'sm' ? 'text-[10px] px-2 py-0.5' : 'text-xs px-2.5 py-1';

  return (
    <span
      className={`inline-flex items-center font-bold rounded-full border capitalize ${styles[variant]} ${sizeClasses}`}
    >
      <span className="w-1.5 h-1.5 rounded-full mr-1.5 bg-current opacity-75" />
      {status}
    </span>
  );
};
