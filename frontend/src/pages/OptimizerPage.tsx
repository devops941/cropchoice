import React, { useState, useEffect } from 'react';
import { useFarm } from '../context/FarmContext';
import { optimizerApi, importExportApi } from '../api/client';
import { 
  PieChart as PieIcon, 
  Download, 
  Play, 
  CheckCircle2, 
  AlertTriangle, 
  TrendingUp, 
  Droplet, 
  DollarSign, 
  Scale, 
  ArrowRight,
  ShieldCheck,
  Activity
} from 'lucide-react';
import { 
  PieChart, 
  Pie, 
  Cell, 
  ResponsiveContainer, 
  Tooltip, 
  Legend,
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  Line
} from 'recharts';

export const OptimizerPage: React.FC = () => {
  const { selectedFarm, selectedFarmId } = useFarm();
  const [optimization, setOptimization] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [solving, setSolving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Form controls
  const [objective, setObjective] = useState('max_return');
  const [maxShare, setMaxShare] = useState(0.40);
  const [minCrops, setMinCrops] = useState(3);
  const [minArea, setMinArea] = useState(0.4);
  const [useAllLand, setUseAllLand] = useState(true);
  const [riskWeight, setRiskWeight] = useState(0.5);

  const fetchLatestOptimization = async () => {
    if (!selectedFarmId) return;
    try {
      setLoading(true);
      const list = await optimizerApi.list(selectedFarmId);
      if (list && list.length > 0) {
        setOptimization(list[0]);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLatestOptimization();
  }, [selectedFarmId]);

  const handleSolve = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFarmId) return;
    setSolving(true);
    setError(null);

    try {
      const res = await optimizerApi.run({
        farm_id: selectedFarmId,
        objective,
        max_share: maxShare,
        min_crops: minCrops,
        min_area: minArea,
        use_all_land: useAllLand,
        risk_weight: riskWeight,
      });
      setOptimization(res);
    } catch (err: any) {
      setError(err.message || 'Optimization solver failed');
    } finally {
      setSolving(false);
    }
  };

  const allocation = optimization?.allocation || [];
  const totals = optimization?.totals || {};
  const utilisation = optimization?.utilisation || {};
  const diversification = optimization?.diversification || {};
  const shadowPrices = optimization?.shadow_prices || {};
  const baselines = optimization?.baselines || {};
  const efficientFrontier = optimization?.efficient_frontier || [];

  const CROP_COLORS = ['#059669', '#D97706', '#0D9488', '#C2763F', '#E11D48', '#65A30D', '#047857', '#B45309'];
  const chartData = allocation.map((a: any) => ({
    name: a.crop_name,
    value: a.area_ha,
    share: (a.share * 100).toFixed(1),
  }));

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-3xl border border-[#DCE5DC] p-6 shadow-card flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <PieIcon className="w-5 h-5 text-[#047857]" />
            <span className="text-xs font-bold uppercase tracking-wider text-[#047857]">
              Mixed-Integer Linear Programming (MILP)
            </span>
          </div>
          <h1 className="text-2xl font-extrabold text-[#14231A]">Portfolio Land Allocation Optimizer</h1>
          <p className="text-xs text-[#4A5F52] mt-1">
            Solves optimal hectares per crop while satisfying water, budget, labour, and minimum diversification constraints.
          </p>
        </div>

        {optimization?.id && (
          <a
            href={importExportApi.exportOptimizationUrl(optimization.id)}
            download
            className="px-4 py-2.5 rounded-xl bg-[#EEF3EC] hover:bg-[#DCE5DC] text-[#14231A] text-xs font-bold flex items-center gap-2 border border-[#DCE5DC] transition-all"
          >
            <Download className="w-4 h-4 text-[#047857]" />
            Export Portfolio (.xlsx)
          </a>
        )}
      </div>

      {/* Control Form & Parameters */}
      <form onSubmit={handleSolve} className="bg-white rounded-3xl border border-[#DCE5DC] p-6 shadow-card space-y-4">
        <div className="flex items-center justify-between">
          <span className="text-xs font-bold uppercase tracking-wider text-[#7A8E80]">Optimizer Settings</span>
          <button
            type="submit"
            disabled={solving}
            className="px-5 py-2.5 rounded-xl bg-[#047857] hover:bg-[#065F46] disabled:opacity-50 text-white text-xs font-bold flex items-center gap-2 shadow-md shadow-[#047857]/20 transition-all"
          >
            <Play className="w-4 h-4" />
            {solving ? 'Solving MILP...' : 'Re-Run Optimization'}
          </button>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 pt-2">
          <div>
            <label className="block text-xs font-bold text-[#14231A] mb-1.5">Objective Goal</label>
            <select
              value={objective}
              onChange={(e) => setObjective(e.target.value)}
              className="w-full px-3 py-2 rounded-xl border border-[#DCE5DC] text-xs font-bold text-[#14231A] bg-[#F6F8F4] outline-none"
            >
              <option value="max_return">Maximize Net Profit (INR)</option>
              <option value="max_topsis">Maximize TOPSIS Closeness</option>
              <option value="balanced">Balanced Return & Risk</option>
            </select>
          </div>

          <div>
            <label className="block text-xs font-bold text-[#14231A] mb-1.5">
              Max Share per Crop: {(maxShare * 100).toFixed(0)}%
            </label>
            <input
              type="range"
              min="0.25"
              max="0.80"
              step="0.05"
              value={maxShare}
              onChange={(e) => setMaxShare(parseFloat(e.target.value))}
              className="w-full accent-[#047857]"
            />
          </div>

          <div>
            <label className="block text-xs font-bold text-[#14231A] mb-1.5">
              Minimum Crops to Plant: {minCrops}
            </label>
            <input
              type="range"
              min="1"
              max="6"
              step="1"
              value={minCrops}
              onChange={(e) => setMinCrops(parseInt(e.target.value))}
              className="w-full accent-[#047857]"
            />
          </div>

          <div className="flex items-center gap-2 pt-6">
            <label className="flex items-center gap-2 cursor-pointer text-xs font-bold text-[#14231A]">
              <input
                type="checkbox"
                checked={useAllLand}
                onChange={(e) => setUseAllLand(e.target.checked)}
                className="w-4 h-4 text-[#047857] rounded border-[#DCE5DC] focus:ring-[#047857]"
              />
              Force Cultivate 100% Land
            </label>
          </div>
        </div>
      </form>

      {error && (
        <div className="p-4 rounded-2xl bg-[#FFE4E6] border border-[#FECDD3] text-xs font-bold text-[#BE123C] flex items-center gap-3">
          <AlertTriangle className="w-5 h-5 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Results View */}
      {optimization ? (
        <div className="space-y-6">
          {/* Top Metric Strip */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div className="p-4 rounded-2xl bg-white border border-[#DCE5DC] shadow-card">
              <div className="text-[11px] font-bold text-[#7A8E80] uppercase">Allocated Land</div>
              <div className="text-2xl font-black text-[#14231A] mt-1 tabular-nums">
                {totals.total_land_ha} ha
              </div>
              <div className="text-xs text-[#047857] mt-0.5 font-semibold">
                {utilisation.land_pct}% of holding
              </div>
            </div>

            <div className="p-4 rounded-2xl bg-white border border-[#DCE5DC] shadow-card">
              <div className="text-[11px] font-bold text-[#7A8E80] uppercase">Expected Net Profit</div>
              <div className="text-2xl font-black text-[#D97706] mt-1 tabular-nums">
                ₹{totals.net_return?.toLocaleString()}
              </div>
              <div className="text-xs text-[#B45309] mt-0.5 font-semibold">
                Across {allocation.length} selected crops
              </div>
            </div>

            <div className="p-4 rounded-2xl bg-white border border-[#DCE5DC] shadow-card">
              <div className="text-[11px] font-bold text-[#7A8E80] uppercase">Water Consumption</div>
              <div className="text-2xl font-black text-[#0D9488] mt-1 tabular-nums">
                {totals.water_m3?.toLocaleString()} m³
              </div>
              <div className="text-xs text-[#0F766E] mt-0.5 font-semibold">
                {utilisation.water_pct}% utilisation
              </div>
            </div>

            <div className="p-4 rounded-2xl bg-white border border-[#DCE5DC] shadow-card">
              <div className="text-[11px] font-bold text-[#7A8E80] uppercase">Diversification (1/HHI)</div>
              <div className="text-2xl font-black text-[#047857] mt-1 tabular-nums">
                {diversification.effective_crops} Crops
              </div>
              <div className="text-xs text-[#065F46] mt-0.5 font-semibold">
                Rating: {diversification.diversification_rating}
              </div>
            </div>
          </div>

          {/* Allocation Table & Donut */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            {/* Table (7 cols) */}
            <div className="lg:col-span-7 bg-white rounded-3xl border border-[#DCE5DC] p-6 shadow-card">
              <h2 className="text-base font-extrabold text-[#14231A] mb-4">Allocated Crops Breakdown</h2>
              <div className="border border-[#DCE5DC] rounded-2xl overflow-hidden">
                <table className="w-full text-left text-xs">
                  <thead className="bg-[#EEF3EC] text-[#14231A] font-bold">
                    <tr>
                      <th className="p-3">Crop Name</th>
                      <th className="p-3">Area (ha)</th>
                      <th className="p-3">Share</th>
                      <th className="p-3">Net Profit</th>
                      <th className="p-3">Water</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[#DCE5DC]">
                    {allocation.map((a: any, i: number) => (
                      <tr key={a.crop_id || i} className="hover:bg-[#F6F8F4] transition-colors">
                        <td className="p-3 font-extrabold text-[#14231A] flex items-center gap-2">
                          <span
                            className="w-2.5 h-2.5 rounded-full"
                            style={{ backgroundColor: CROP_COLORS[i % CROP_COLORS.length] }}
                          />
                          {a.crop_name}
                        </td>
                        <td className="p-3 font-bold tabular-nums">{a.area_ha} ha</td>
                        <td className="p-3 font-semibold text-[#047857]">{((a.share || 0) * 100).toFixed(1)}%</td>
                        <td className="p-3 font-bold text-[#D97706]">₹{a.expected_return?.toLocaleString()}</td>
                        <td className="p-3 text-[#0D9488] font-semibold">{a.water_m3?.toLocaleString()} m³</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Shadow Prices / Duals */}
              <div className="mt-6 p-4 rounded-2xl bg-[#F6F8F4] border border-[#DCE5DC]">
                <div className="text-xs font-bold text-[#14231A] mb-1">Economic Shadow Prices (Dual Values)</div>
                <div className="grid grid-cols-2 gap-3 text-xs text-[#4A5F52] mt-2">
                  <div>1 extra ha land adds: <strong className="text-[#047857]">₹{shadowPrices.land_inr_per_ha} profit</strong></div>
                  <div>1 m³ extra water adds: <strong className="text-[#0D9488]">₹{shadowPrices.water_inr_per_m3} profit</strong></div>
                </div>
              </div>
            </div>

            {/* Donut Chart (5 cols) */}
            <div className="lg:col-span-5 bg-white rounded-3xl border border-[#DCE5DC] p-6 shadow-card flex flex-col justify-between">
              <div>
                <h2 className="text-base font-extrabold text-[#14231A] mb-1">Land Allocation Share</h2>
                <p className="text-xs text-[#4A5F52] mb-4">Hectares distribution</p>

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
              </div>

              {/* Baselines comparison */}
              <div className="mt-4 pt-4 border-t border-[#DCE5DC] space-y-2 text-xs">
                <div className="font-bold text-[#14231A]">Benchmark Comparisons:</div>
                <div className="flex justify-between text-[#4A5F52]">
                  <span>All-in on #{baselines.all_in_top_crop?.crop_name || '1'}:</span>
                  <strong className="text-[#14231A]">₹{baselines.all_in_top_crop?.net_return?.toLocaleString()}</strong>
                </div>
                <div className="flex justify-between text-[#4A5F52]">
                  <span>Equal Split Top 3:</span>
                  <strong className="text-[#14231A]">₹{baselines.equal_split_top?.net_return?.toLocaleString()}</strong>
                </div>
              </div>
            </div>
          </div>
        </div>
      ) : (
        <div className="bg-white rounded-3xl border border-[#DCE5DC] p-12 text-center shadow-card">
          <PieIcon className="w-12 h-12 text-[#047857] mx-auto mb-3" />
          <h3 className="text-base font-bold text-[#14231A]">No Optimization Solved Yet</h3>
          <p className="text-xs text-[#4A5F52] mt-1 mb-4">Click "Re-Run Optimization" to calculate allocation.</p>
        </div>
      )}
    </div>
  );
};
