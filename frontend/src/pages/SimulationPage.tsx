import React, { useState, useEffect } from 'react';
import { useFarm } from '../context/FarmContext';
import { optimizerApi, simulationsApi } from '../api/client';
import { Activity, Play, AlertTriangle, ShieldAlert, BarChart3, TrendingDown } from 'lucide-react';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  Tooltip, 
  ResponsiveContainer, 
  ReferenceLine 
} from 'recharts';

export const SimulationPage: React.FC = () => {
  const { selectedFarmId } = useFarm();
  const [simulation, setSimulation] = useState<any>(null);
  const [optimizationId, setOptimizationId] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);

  useEffect(() => {
    if (!selectedFarmId) return;
    optimizerApi.list(selectedFarmId).then((opts) => {
      if (opts && opts.length > 0) {
        setOptimizationId(opts[0].id);
        simulationsApi.getByOpt(opts[0].id).then(setSimulation).catch(() => setSimulation(null));
      }
    }).finally(() => setLoading(false));
  }, [selectedFarmId]);

  const handleRunSimulation = async () => {
    if (!optimizationId) return;
    setRunning(true);
    try {
      const res = await simulationsApi.run({
        optimization_id: optimizationId,
        n_runs: 5000,
        seed: 42,
      });
      setSimulation(res);
    } catch (err: any) {
      alert(err.message || 'Simulation failed');
    } finally {
      setRunning(false);
    }
  };

  const stats = simulation?.stats || {};
  const histogramBins = simulation?.histogram?.bins || [];
  const riskContrib = simulation?.risk_contribution || {};

  const chartData = histogramBins.map((b: any) => ({
    name: `₹${(b.mid / 1000).toFixed(0)}k`,
    count: b.count,
    pct: b.pct,
  }));

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-3xl border border-[#DCE5DC] p-6 shadow-card flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Activity className="w-5 h-5 text-[#E11D48]" />
            <span className="text-xs font-bold uppercase tracking-wider text-[#E11D48]">
              Stochastic Risk Assessment
            </span>
          </div>
          <h1 className="text-2xl font-extrabold text-[#14231A]">Monte Carlo Portfolio Risk</h1>
          <p className="text-xs text-[#4A5F52] mt-1">
            5,000 empirical iterations evaluating downside Value-at-Risk (VaR), Expected Shortfall, and Probability of Loss.
          </p>
        </div>

        <button
          onClick={handleRunSimulation}
          disabled={running || !optimizationId}
          className="px-5 py-2.5 rounded-xl bg-[#047857] hover:bg-[#065F46] disabled:opacity-50 text-white text-xs font-bold flex items-center gap-2 shadow-md shadow-[#047857]/20 transition-all"
        >
          <Play className="w-4 h-4" />
          {running ? 'Running 5,000 Trials...' : 'Run 5,000 Simulations'}
        </button>
      </div>

      {simulation ? (
        <div className="space-y-6">
          {/* Top Metric Cards */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div className="p-4 rounded-2xl bg-white border border-[#DCE5DC] shadow-card">
              <div className="text-[11px] font-bold text-[#7A8E80] uppercase">Expected Mean Return</div>
              <div className="text-2xl font-black text-[#14231A] mt-1 tabular-nums">
                ₹{stats.mean?.toLocaleString()}
              </div>
              <div className="text-xs text-[#047857] mt-0.5">Median: ₹{stats.median?.toLocaleString()}</div>
            </div>

            <div className="p-4 rounded-2xl bg-white border border-[#DCE5DC] shadow-card">
              <div className="text-[11px] font-bold text-[#7A8E80] uppercase">Probability of Loss P(L)</div>
              <div className="text-2xl font-black text-[#E11D48] mt-1 tabular-nums">
                {stats.p_loss_pct}%
              </div>
              <div className="text-xs text-[#BE123C] mt-0.5">Chance of negative return</div>
            </div>

            <div className="p-4 rounded-2xl bg-white border border-[#DCE5DC] shadow-card">
              <div className="text-[11px] font-bold text-[#7A8E80] uppercase">5th Percentile VaR (95%)</div>
              <div className="text-2xl font-black text-[#D97706] mt-1 tabular-nums">
                ₹{stats.p5_var?.toLocaleString()}
              </div>
              <div className="text-xs text-[#B45309] mt-0.5">Value at Risk floor</div>
            </div>

            <div className="p-4 rounded-2xl bg-white border border-[#DCE5DC] shadow-card">
              <div className="text-[11px] font-bold text-[#7A8E80] uppercase">Expected Shortfall (CVaR)</div>
              <div className="text-2xl font-black text-[#C2763F] mt-1 tabular-nums">
                ₹{stats.expected_shortfall?.toLocaleString()}
              </div>
              <div className="text-xs text-[#9A5B2F] mt-0.5">Tail average loss</div>
            </div>
          </div>

          {/* Histogram & Per-Crop Risk Contribution */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            {/* Histogram (8 cols) */}
            <div className="lg:col-span-8 bg-white rounded-3xl border border-[#DCE5DC] p-6 shadow-card">
              <div className="flex items-center justify-between mb-2">
                <h2 className="text-base font-extrabold text-[#14231A]">Portfolio Return Distribution</h2>
                <span className="text-xs font-bold text-[#7A8E80]">5,000 Bootstrap Runs</span>
              </div>
              <p className="text-xs text-[#4A5F52] mb-6">
                Frequency distribution under joint price shocks and yield fluctuations.
              </p>

              <div className="h-72 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={chartData}>
                    <XAxis dataKey="name" tick={{ fontSize: 9 }} interval={2} />
                    <YAxis tick={{ fontSize: 10 }} />
                    <Tooltip
                      formatter={(val: any) => [`${val} trials`, 'Frequency']}
                      contentStyle={{ backgroundColor: '#ffffff', borderColor: '#DCE5DC', borderRadius: '12px' }}
                    />
                    <Bar dataKey="count" fill="#047857" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Risk Contribution (4 cols) */}
            <div className="lg:col-span-4 bg-white rounded-3xl border border-[#DCE5DC] p-6 shadow-card">
              <h2 className="text-base font-extrabold text-[#14231A] mb-1">Crop Risk Contribution</h2>
              <p className="text-xs text-[#4A5F52] mb-4">Percentage share of portfolio variance</p>

              <div className="space-y-3">
                {Object.entries(riskContrib).map(([cname, pct]: any) => (
                  <div key={cname} className="p-3 rounded-2xl bg-[#F6F8F4] border border-[#DCE5DC]">
                    <div className="flex justify-between text-xs font-bold mb-1">
                      <span className="text-[#14231A]">{cname}</span>
                      <span className="text-[#E11D48] tabular-nums">{pct}%</span>
                    </div>
                    <div className="w-full h-2 rounded-full bg-[#EEF3EC] overflow-hidden">
                      <div
                        className="h-full rounded-full bg-[#E11D48]"
                        style={{ width: `${Math.min(100, pct)}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      ) : (
        <div className="bg-white rounded-3xl border border-[#DCE5DC] p-12 text-center shadow-card">
          <Activity className="w-12 h-12 text-[#E11D48] mx-auto mb-3" />
          <h3 className="text-base font-bold text-[#14231A]">No Simulation Executed Yet</h3>
          <p className="text-xs text-[#4A5F52] mt-1 mb-4">Click "Run 5,000 Simulations" to evaluate portfolio risk.</p>
        </div>
      )}
    </div>
  );
};
