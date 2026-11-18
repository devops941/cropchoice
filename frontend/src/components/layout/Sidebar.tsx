import React from 'react';
import { NavLink } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import {
  LayoutDashboard,
  Compass,
  MapPin,
  Leaf,
  TrendingUp,
  Sliders,
  Award,
  PieChart,
  Layers,
  Activity,
  UploadCloud,
  FileText,
  ShieldCheck,
  HelpCircle
} from 'lucide-react';

interface NavItem {
  name: string;
  path: string;
  icon: React.ComponentType<{ className?: string }>;
  adminOnly?: boolean;
  badge?: string;
}

const NAV_ITEMS: NavItem[] = [
  { name: 'Dashboard', path: '/app', icon: LayoutDashboard },
  { name: 'Planning Wizard', path: '/app/wizard', icon: Compass, badge: 'Flow' },
  { name: 'Farms & Soil', path: '/app/farms', icon: MapPin },
  { name: 'Crop Library', path: '/app/crops', icon: Leaf },
  { name: 'Economics & Prices', path: '/app/prices', icon: TrendingUp },
  { name: 'Criteria & AHP', path: '/app/criteria', icon: Sliders },
  { name: 'TOPSIS Ranking', path: '/app/ranking', icon: Award },
  { name: 'Portfolio Optimizer', path: '/app/optimizer', icon: PieChart },
  { name: 'Scenarios', path: '/app/scenarios', icon: Layers },
  { name: 'Monte Carlo Risk', path: '/app/simulation', icon: Activity },
  { name: 'Data Upload Center', path: '/app/import', icon: UploadCloud },
  { name: 'Decision Reports', path: '/app/reports', icon: FileText },
  { name: 'Admin Console', path: '/app/admin', icon: ShieldCheck, adminOnly: true },
  { name: 'Methodology & Guide', path: '/about', icon: HelpCircle },
];

export const Sidebar: React.FC = () => {
  const { isAdmin } = useAuth();

  return (
    <aside className="w-64 bg-white border-r border-[#DCE5DC] min-h-[calc(100vh-65px)] flex flex-col justify-between p-4 shrink-0">
      <div className="space-y-1">
        <div className="text-[11px] font-bold uppercase tracking-wider text-[#7A8E80] px-3 py-2">
          Navigation
        </div>
        {NAV_ITEMS.filter((item) => !item.adminOnly || isAdmin).map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.path}
              to={item.path}
              end={item.path === '/app'}
              className={({ isActive }) =>
                `flex items-center justify-between px-3.5 py-2.5 rounded-xl text-xs font-semibold transition-all ${
                  isActive
                    ? 'bg-[#047857] text-white shadow-sm shadow-[#047857]/20 font-bold'
                    : 'text-[#4A5F52] hover:bg-[#EEF3EC] hover:text-[#14231A]'
                }`
              }
            >
              {({ isActive }) => (
                <>
                  <div className="flex items-center gap-3">
                    <Icon className={`w-4 h-4 ${isActive ? 'text-white' : 'text-[#7A8E80]'}`} />
                    <span>{item.name}</span>
                  </div>
                  {item.badge && (
                    <span
                      className={`text-[9px] uppercase px-1.5 py-0.5 rounded-full font-bold ${
                        isActive
                          ? 'bg-white/20 text-white'
                          : 'bg-[#D1FAE5] text-[#065F46]'
                      }`}
                    >
                      {item.badge}
                    </span>
                  )}
                </>
              )}
            </NavLink>
          );
        })}
      </div>

      {/* Bottom Status Card */}
      <div className="mt-6 p-3.5 rounded-2xl bg-gradient-to-br from-[#F6F8F4] to-[#EEF3EC] border border-[#DCE5DC] text-xs">
        <div className="flex items-center gap-2 mb-1.5">
          <div className="w-2 h-2 rounded-full bg-[#10B981] animate-pulse" />
          <span className="font-bold text-[#14231A]">MongoDB Atlas Active</span>
        </div>
        <p className="text-[11px] text-[#4A5F52] leading-relaxed">
          16 crop genomes · 10-yr mandi trends · Multi-criteria optimization engine.
        </p>
      </div>
    </aside>
  );
};
