import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { useFarm } from '../../context/FarmContext';
import { 
  Sprout, 
  MapPin, 
  LogOut, 
  User, 
  Shield, 
  Compass,
  UploadCloud,
  ChevronDown
} from 'lucide-react';

export const Navbar: React.FC = () => {
  const { user, logout, isAdmin } = useAuth();
  const { farms, selectedFarmId, setSelectedFarmId, selectedFarm } = useFarm();
  const navigate = useNavigate();

  return (
    <header className="sticky top-0 z-40 w-full bg-white/90 backdrop-blur-md border-b border-[#DCE5DC] px-4 lg:px-8 py-3">
      <div className="flex items-center justify-between">
        {/* Left: Brand & Farm Selector */}
        <div className="flex items-center gap-6">
          <Link to="/app" className="flex items-center gap-2.5 group">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-[#047857] to-[#059669] flex items-center justify-center text-white shadow-md shadow-[#047857]/20 group-hover:scale-105 transition-transform">
              <Sprout className="w-5 h-5" />
            </div>
            <div>
              <span className="font-extrabold text-lg text-[#14231A] tracking-tight flex items-center gap-1.5">
                CropChoice
                <span className="text-[10px] font-semibold uppercase px-1.5 py-0.5 rounded-full bg-[#D1FAE5] text-[#065F46] border border-[#A7F3D0]">
                  2026
                </span>
              </span>
              <p className="text-[11px] text-[#4A5F52] hidden sm:block">Intelligent Portfolio Optimizer</p>
            </div>
          </Link>

          {/* Farm Switcher Dropdown */}
          {farms.length > 0 && (
            <div className="relative flex items-center bg-[#F6F8F4] border border-[#DCE5DC] rounded-xl px-3 py-1.5 hover:border-[#047857] transition-colors">
              <MapPin className="w-4 h-4 text-[#047857] mr-2 shrink-0" />
              <select
                aria-label="Select Farm"
                value={selectedFarmId || ''}
                onChange={(e) => setSelectedFarmId(e.target.value)}
                className="bg-transparent text-sm font-semibold text-[#14231A] focus:outline-none cursor-pointer pr-5"
              >
                {farms.map((f) => (
                  <option key={f.id} value={f.id} className="text-sm">
                    {f.name} ({f.land_ha} ha · {f.season})
                  </option>
                ))}
              </select>
              <ChevronDown className="w-3.5 h-3.5 text-[#7A8E80] absolute right-2.5 pointer-events-none" />
            </div>
          )}
        </div>

        {/* Right: Quick actions & User menu */}
        <div className="flex items-center gap-3">
          <Link
            to="/app/wizard"
            className="hidden md:flex items-center gap-2 px-3.5 py-2 text-xs font-bold text-white bg-[#047857] hover:bg-[#065F46] rounded-xl shadow-sm hover:shadow transition-all"
          >
            <Compass className="w-4 h-4" />
            Planning Wizard
          </Link>

          <Link
            to="/app/import"
            className="flex items-center gap-1.5 px-3 py-2 text-xs font-semibold text-[#047857] bg-[#D1FAE5] hover:bg-[#A7F3D0] rounded-xl transition-all"
          >
            <UploadCloud className="w-4 h-4" />
            <span className="hidden sm:inline">Upload Data</span>
          </Link>

          {/* User Badge */}
          <div className="flex items-center gap-2 pl-2 border-l border-[#DCE5DC]">
            <Link to="/app/profile" className="flex items-center gap-2 py-1 px-2 rounded-lg hover:bg-[#F6F8F4] transition-colors">
              <div className="w-8 h-8 rounded-full bg-[#EEF3EC] border border-[#DCE5DC] flex items-center justify-center text-[#047857] font-bold text-xs">
                {user?.name ? user.name.charAt(0).toUpperCase() : 'U'}
              </div>
              <div className="hidden lg:block text-left">
                <div className="text-xs font-bold text-[#14231A] flex items-center gap-1">
                  {user?.name || 'Planner'}
                  {isAdmin && (
                    <Shield className="w-3 h-3 text-[#D97706]" />
                  )}
                </div>
                <div className="text-[10px] text-[#7A8E80] capitalize">{user?.role || 'planner'}</div>
              </div>
            </Link>

            <button
              onClick={() => {
                logout();
                navigate('/login');
              }}
              title="Log out"
              className="p-2 text-[#7A8E80] hover:text-[#E11D48] hover:bg-[#FFE4E6] rounded-lg transition-colors"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </header>
  );
};
