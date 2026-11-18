import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useFarm } from '../context/FarmContext';
import { dashboardApi } from '../api/client';
import { KpiCard } from '../components/ui/KpiCard';
import { 
  Award, 
  TrendingUp, 
  Droplet, 
  PieChart as PieIcon, 
  AlertCircle, 
  Layers, 
  ArrowRight, 
  Sparkles,
  ShieldAlert,
  Compass,
  UploadCloud,
  CheckCircle2
} from 'lucide-react';
import { 
  PieChart, 
  Pie, 
  Cell, 
  ResponsiveContainer, 
  Tooltip, 
  Legend 
} from 'recharts';

export const DashboardPage: React.FC = () => {
  const { selectedFarmId, selectedFarm } = useFarm();
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  const fetchDashboard = async () => {
    try {
      setLoading(true);
      const res = await dashboardApi.getOverview(selectedFarmId || undefined);
      setData(res);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboard();
  }, [selectedFarmId]);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] gap-3">
        <div className="w-10 h-10 border-4 border-[#047857] border-t-transparent rounded-full animate-spin" />
        <p className="text-xs font-semibold text-[#7A8E80]">Loading agricultural dashboard...</p>
      </div>
    );
  }

  const kpis = data?.kpis || {};
  const topRanking = data?.top_ranking || [];
  const allocation = data?.allocation || [];
  const utilisation = data?.utilisation || {};
  const scenarios = data?.scenarios || [];
  const completeness = data?.data_completeness || { score_pct: 100, missing_items: [] };

  // 8-color organic palette for crops: Emerald, Amber, Teal, Clay, Rose, Lime, Moss, Mustard (NO BLUE!)
  const CROP_COLORS = ['#059669', '#D97706', '#0D9488', '#C2763F', '#E11D48', '#65A30D', '#047857', '#B45309'];

  const chartData = allocation.map((a: any) => ({
    name: a.crop_name,
    value: a.area_ha,
    share: (a.share * 100).toFixed(1),
  }));

  return (
    <div className="space-y-6">
      {/* Welcome / Header Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white rounded-3xl border border-[#DCE5DC] p-6 shadow-card">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="w-2.5 h-2.5 rounded-full bg-[#10B981]" />
            <span className="text-xs font-bold text-[#047857] uppercase tracking-wider">
              Farm Profile Active · {selectedFarm?.season?.toUpperCase() || 'KHARIF'}
            </span>
          </div>
          <h1 className="text-2xl lg:text-3xl font-extrabold text-[#14231A] tracking-tight">
            {selectedFarm?.name || 'Crop Strategy Overview'}
          </h1>
          <p className="text-xs text-[#4A5F52] mt-1">
            {selectedFarm?.land_ha || 5.0} ha total holding · Soil: {selectedFarm?.soil?.texture || 'Loam'}, pH {selectedFarm?.soil?.ph || 6.8}
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Link
            to="/app/wizard"
            className="px-4 py-2.5 rounded-xl bg-[#047857] hover:bg-[#065F46] text-white text-xs font-bold shadow-md shadow-[#047857]/20 flex items-center gap-2 transition-all"
          >
            <Compass className="w-4 h-4" />
            Run Planning Wizard
          </Link>
          <Link
            to="/app/import"
            className="px-4 py-2.5 rounded-xl bg-[#EEF3EC] hover:bg-[#DCE5DC] text-[#14231A] text-xs font-bold flex items-center gap-2 transition-all border border-[#DCE5DC]"
          >
            <UploadCloud className="w-4 h-4 text-[#047857]" />
            Upload Data
          </Link>
        </div>
      </div>

      {/* Bento Grid: Row 1 - 5 KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        <KpiCard
          title="Top Ranked Crop"
          value={kpis.top_crop || 'N/A'}
          subtitle="Highest multi-criteria suitability"
          icon={<Award className="w-5 h-5" />}
          badge="Rank #1"
          badgeColor="emerald"
        />
        <KpiCard
          title="Expected Net Return"
          value={`₹${(kpis.net_return || 0).toLocaleString()}`}
          subtitle="Optimized portfolio net profit"
          icon={<TrendingUp className="w-5 h-5 text-[#D97706]" />}
          badge="Per Season"
          badgeColor="amber"
        />
        <KpiCard
          title="Water Utilisation"
          value={`${kpis.water_pct || 0}%`}
          subtitle="Of total irrigation capacity"
          icon={<Droplet className="w-5 h-5 text-[#0D9488]" />}
          badge={kpis.water_pct > 90 ? 'High' : 'Optimal'}
          badgeColor="teal"
        />
        <KpiCard
          title="Effective Crops"
          value={kpis.effective_crops || 1.0}
          subtitle={`Diversification: ${kpis.diversification_rating || 'Good'}`}
          icon={<PieIcon className="w-5 h-5 text-[#C2763F]" />}
          badge="1 / HHI"
          badgeColor="earth"
        />
        <KpiCard
          title="Portfolio Risk"
          value={`₹${(kpis.portfolio_risk_std || 0).toLocaleString()}`}
          subtitle="Return standard deviation"
          icon={<AlertCircle className="w-5 h-5 text-[#E11D48]" />}
          badge="1-Sigma"
          badgeColor="rose"
        />
      </div>

      {/* Bento Grid: Row 2 - Leaderboard & Allocation Donut */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left: Top 5 Ranking Leaderboard (7 cols) */}
        <div className="lg:col-span-7 bg-white rounded-3xl border border-[#DCE5DC] p-6 shadow-card">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-base font-extrabold text-[#14231A]">TOPSIS Ranking Leaderboard</h2>
              <p className="text-xs text-[#4A5F52]">Ranked by geometric closeness to ideal criteria ($C_i$)</p>
            </div>
            <Link to="/app/ranking" className="text-xs font-bold text-[#047857] hover:underline flex items-center gap-1">
              View All <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          <div className="space-y-3">
            {topRanking.map((crop: any, idx: number) => {
              const rank = crop.rank || idx + 1;
              const medals = ['🥇', '🥈', '🥉'];
              return (
                <div
                  key={crop.crop_id || idx}
                  className="p-3.5 rounded-2xl bg-[#F6F8F4] border border-[#DCE5DC] hover:border-[#047857] transition-all"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <span className="text-lg font-black w-6 text-center">
                        {rank <= 3 ? medals[rank - 1] : `#${rank}`}
                      </span>
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="font-extrabold text-sm text-[#14231A]">{crop.crop_name}</span>
                          <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-white border border-[#DCE5DC] text-[#4A5F52]">
                            {crop.category || 'Crop'}
                          </span>
                        </div>
                        <p className="text-[11px] text-[#4A5F52] mt-0.5">{crop.explanation}</p>
                      </div>
                    </div>

                    <div className="text-right">
                      <div className="text-xs font-black text-[#047857] tabular-nums">
                        {(crop.closeness * 100).toFixed(1)}% Fit
                      </div>
                      <div className="text-[10px] text-[#7A8E80]">
                        ₹{crop.criteria_values?.return?.toLocaleString()}/ha
                      </div>
                    </div>
                  </div>

                  {/* Criteria mini bars */}
                  <div className="mt-2.5 pt-2 border-t border-[#DCE5DC]/60 grid grid-cols-4 gap-2 text-[10px] text-[#7A8E80]">
                    <div>Water: <strong className="text-[#14231A]">{crop.criteria_values?.water} mm</strong></div>
                    <div>Soil Fit: <strong className="text-[#14231A]">{crop.criteria_values?.soil}</strong></div>
                    <div>Price CV: <strong className="text-[#14231A]">{crop.criteria_values?.variability}</strong></div>
                    <div>WSM: <strong className="text-[#14231A]">#{crop.wsm_rank || rank}</strong></div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Right: Land Allocation Donut (5 cols) */}
        <div className="lg:col-span-5 bg-white rounded-3xl border border-[#DCE5DC] p-6 shadow-card flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-4">
              <div>
                <h2 className="text-base font-extrabold text-[#14231A]">Optimal Land Allocation</h2>
                <p className="text-xs text-[#4A5F52]">Diversified acreage under constraints</p>
              </div>
              <Link to="/app/optimizer" className="text-xs font-bold text-[#047857] hover:underline flex items-center gap-1">
                Details <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </div>

            {chartData.length > 0 ? (
              <div className="h-64 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={chartData}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={85}
                      paddingAngle={4}
                      dataKey="value"
                    >
                      {chartData.map((_: any, index: number) => (
                        <Cell key={`cell-${index}`} fill={CROP_COLORS[index % CROP_COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip
                      formatter={(val: any, name: any, item: any) => [
                        `${val} ha (${item.payload.share}%)`,
                        name,
                      ]}
                      contentStyle={{ backgroundColor: '#ffffff', borderColor: '#DCE5DC', borderRadius: '12px' }}
                    />
                    <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }} />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            ) : (
              <div className="h-64 flex items-center justify-center text-xs text-[#7A8E80]">
                No allocation calculated yet.
              </div>
            )}
          </div>

          {/* Allocation breakdown list */}
          <div className="mt-4 pt-4 border-t border-[#DCE5DC] space-y-2">
            {allocation.slice(0, 3).map((a: any, i: number) => (
              <div key={a.crop_id || i} className="flex items-center justify-between text-xs">
                <div className="flex items-center gap-2">
                  <span
                    className="w-2.5 h-2.5 rounded-full"
                    style={{ backgroundColor: CROP_COLORS[i % CROP_COLORS.length] }}
                  />
                  <span className="font-bold text-[#14231A]">{a.crop_name}</span>
                </div>
                <div className="font-semibold text-[#4A5F52] tabular-nums">
                  {a.area_ha} ha ({((a.share || 0) * 100).toFixed(0)}%)
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Bento Grid: Row 3 - Resource Utilization & Scenarios */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Resource Gauges (4 cols) */}
        <div className="lg:col-span-4 bg-white rounded-3xl border border-[#DCE5DC] p-6 shadow-card">
          <h2 className="text-base font-extrabold text-[#14231A] mb-1">Resource Utilization</h2>
          <p className="text-xs text-[#4A5F52] mb-6">Physical & financial budget consumption</p>

          <div className="space-y-5">
            <div>
              <div className="flex justify-between text-xs font-bold mb-1.5">
                <span className="text-[#14231A]">Water Consumption</span>
                <span className="text-[#0D9488] tabular-nums">{utilisation.water_pct || 0}%</span>
              </div>
              <div className="w-full h-3 rounded-full bg-[#EEF3EC] overflow-hidden">
                <div
                  className="h-full rounded-full bg-[#0D9488] transition-all duration-500"
                  style={{ width: `${Math.min(100, utilisation.water_pct || 0)}%` }}
                />
              </div>
            </div>

            <div>
              <div className="flex justify-between text-xs font-bold mb-1.5">
                <span className="text-[#14231A]">Working Capital (Budget)</span>
                <span className="text-[#D97706] tabular-nums">{utilisation.budget_pct || 0}%</span>
              </div>
              <div className="w-full h-3 rounded-full bg-[#EEF3EC] overflow-hidden">
                <div
                  className="h-full rounded-full bg-[#D97706] transition-all duration-500"
                  style={{ width: `${Math.min(100, utilisation.budget_pct || 0)}%` }}
                />
              </div>
            </div>

            <div>
              <div className="flex justify-between text-xs font-bold mb-1.5">
                <span className="text-[#14231A]">Farm Labour Allocation</span>
                <span className="text-[#047857] tabular-nums">{utilisation.labour_pct || 0}%</span>
              </div>
              <div className="w-full h-3 rounded-full bg-[#EEF3EC] overflow-hidden">
                <div
                  className="h-full rounded-full bg-[#047857] transition-all duration-500"
                  style={{ width: `${Math.min(100, utilisation.labour_pct || 0)}%` }}
                />
              </div>
            </div>
          </div>
        </div>

        {/* Climate & Market Scenarios (4 cols) */}
        <div className="lg:col-span-4 bg-white rounded-3xl border border-[#DCE5DC] p-6 shadow-card">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-base font-extrabold text-[#14231A]">Scenario Sensitivity</h2>
              <p className="text-xs text-[#4A5F52]">Stress testing against shocks</p>
            </div>
            <Link to="/app/scenarios" className="text-xs font-bold text-[#047857] hover:underline flex items-center gap-1">
              Compare <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          <div className="space-y-3">
            {scenarios.slice(0, 3).map((sc: any, idx: number) => (
              <div key={sc.id || idx} className="p-3 rounded-2xl bg-[#F6F8F4] border border-[#DCE5DC]">
                <div className="flex justify-between items-start">
                  <div className="font-bold text-xs text-[#14231A]">{sc.name}</div>
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-[#D1FAE5] text-[#065F46]">
                    Feasible
                  </span>
                </div>
                <div className="mt-2 flex items-center justify-between text-xs text-[#4A5F52]">
                  <span>Net Return: <strong className="text-[#14231A]">₹{sc.summary?.net_return?.toLocaleString()}</strong></span>
                  <span>Water: <strong className="text-[#0D9488]">{sc.summary?.water_m3?.toLocaleString()} m³</strong></span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Data Completeness & Health (4 cols) */}
        <div className="lg:col-span-4 bg-white rounded-3xl border border-[#DCE5DC] p-6 shadow-card flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-2">
              <h2 className="text-base font-extrabold text-[#14231A]">Data Health</h2>
              <span className="text-xs font-black px-2.5 py-1 rounded-full bg-[#D1FAE5] text-[#065F46] border border-[#A7F3D0]">
                {completeness.score_pct}% Ready
              </span>
            </div>
            <p className="text-xs text-[#4A5F52] mb-4">Dataset integrity in MongoDB Atlas</p>

            {completeness.missing_items && completeness.missing_items.length > 0 ? (
              <div className="space-y-2.5">
                {completeness.missing_items.slice(0, 2).map((item: any, idx: number) => (
                  <div key={idx} className="p-2.5 rounded-xl bg-[#FEF3C7] border border-[#FDE68A] text-xs">
                    <div className="font-bold text-[#B45309]">{item.crop_name}</div>
                    <div className="text-[11px] text-[#78350F]">{item.message}</div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="p-4 rounded-2xl bg-[#D1FAE5] border border-[#A7F3D0] text-xs text-[#065F46] flex items-center gap-3">
                <CheckCircle2 className="w-5 h-5 text-[#047857] shrink-0" />
                <span>All 16 crops have complete soil ranges, 10-year monthly prices, and CACP economics.</span>
              </div>
            )}
          </div>

          <Link
            to="/app/import"
            className="w-full mt-4 py-2.5 rounded-xl border border-[#DCE5DC] bg-[#F6F8F4] hover:bg-[#EEF3EC] text-xs font-bold text-[#14231A] text-center flex items-center justify-center gap-2 transition-colors"
          >
            <UploadCloud className="w-4 h-4 text-[#047857]" />
            Import Mandi & Soil CSVs
          </Link>
        </div>
      </div>
    </div>
  );
};
