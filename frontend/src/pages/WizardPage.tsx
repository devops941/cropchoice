import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useFarm } from '../context/FarmContext';
import { criteriaApi, rankingsApi, optimizerApi, simulationsApi } from '../api/client';
import { 
  Compass, 
  MapPin, 
  Sliders, 
  Award, 
  PieChart, 
  Layers, 
  FileText, 
  Check, 
  ArrowRight, 
  ArrowLeft,
  Sparkles,
  Droplet,
  TrendingUp,
  ShieldAlert
} from 'lucide-react';

const STEPS = [
  { id: 1, name: 'Farm & Soil', icon: MapPin },
  { id: 2, name: 'Criteria Weights', icon: Sliders },
  { id: 3, name: 'TOPSIS Ranking', icon: Award },
  { id: 4, name: 'Portfolio Optimizer', icon: PieChart },
  { id: 5, name: 'Scenario Test', icon: Layers },
  { id: 6, name: 'Decision Report', icon: FileText },
];

export const WizardPage: React.FC = () => {
  const { selectedFarm, farms, setSelectedFarmId } = useFarm();
  const navigate = useNavigate();

  const [currentStep, setCurrentStep] = useState(1);
  const [weights, setWeights] = useState({ water: 0.25, soil: 0.25, return: 0.25, variability: 0.25 });
  const [useWsr, setUseWsr] = useState(false);
  const [rankingResult, setRankingResult] = useState<any>(null);
  const [optimizationResult, setOptimizationResult] = useState<any>(null);
  const [simulationResult, setSimulationResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Optimizer parameters
  const [objective, setObjective] = useState('max_return');
  const [maxShare, setMaxShare] = useState(0.40);
  const [minCrops, setMinCrops] = useState(3);
  const [useAllLand, setUseAllLand] = useState(true);

  // Step 2 preset setter
  const applyPreset = (presetWeights: any) => {
    setWeights(presetWeights);
  };

  // Step 3: Run ranking
  const runRanking = async () => {
    if (!selectedFarm) return;
    try {
      setLoading(true);
      setError(null);
      const res = await rankingsApi.run({
        farm_id: selectedFarm.id,
        weights,
        use_wsr: useWsr,
      });
      setRankingResult(res);
      setCurrentStep(3);
    } catch (err: any) {
      setError(err.message || 'Failed to calculate rankings');
    } finally {
      setLoading(false);
    }
  };

  // Step 4: Run optimization
  const runOptimization = async () => {
    if (!selectedFarm) return;
    try {
      setLoading(true);
      setError(null);
      const res = await optimizerApi.run({
        farm_id: selectedFarm.id,
        ranking_id: rankingResult?.id,
        objective,
        max_share: maxShare,
        min_crops: minCrops,
        use_all_land: useAllLand,
      });
      setOptimizationResult(res);
      setCurrentStep(4);
    } catch (err: any) {
      setError(err.message || 'Optimization failed');
    } finally {
      setLoading(false);
    }
  };

  // Step 5: Run Monte Carlo Simulation
  const runSimulation = async () => {
    if (!optimizationResult) return;
    try {
      setLoading(true);
      setError(null);
      const res = await simulationsApi.run({
        optimization_id: optimizationResult.id,
        n_runs: 2500,
        seed: 42,
      });
      setSimulationResult(res);
      setCurrentStep(5);
    } catch (err: any) {
      setError(err.message || 'Simulation failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      {/* Wizard Header Banner */}
      <div className="bg-white rounded-3xl border border-[#DCE5DC] p-6 shadow-card">
        <div className="flex items-center gap-2 mb-2">
          <Compass className="w-5 h-5 text-[#047857]" />
          <span className="text-xs font-bold uppercase tracking-wider text-[#047857]">
            Guided Crop Planning Walkthrough
          </span>
        </div>
        <h1 className="text-2xl lg:text-3xl font-extrabold text-[#14231A]">
          Step-by-Step Strategic Portfolio Planner
        </h1>
        <p className="text-xs text-[#4A5F52] mt-1">
          Follow this 6-step guided pipeline to evaluate soil constraints, establish weights, rank alternatives, and solve land allocation.
        </p>

        {/* Stepper Bar */}
        <div className="mt-8 grid grid-cols-2 sm:grid-cols-6 gap-2">
          {STEPS.map((s) => {
            const Icon = s.icon;
            const isCompleted = currentStep > s.id;
            const isCurrent = currentStep === s.id;
            return (
              <button
                key={s.id}
                type="button"
                onClick={() => {
                  if (s.id < currentStep) setCurrentStep(s.id);
                }}
                disabled={s.id > currentStep}
                className={`p-3 rounded-2xl border text-left transition-all ${
                  isCurrent
                    ? 'bg-[#047857] text-white border-[#047857] shadow-sm'
                    : isCompleted
                    ? 'bg-[#D1FAE5] text-[#065F46] border-[#A7F3D0]'
                    : 'bg-[#F6F8F4] text-[#7A8E80] border-[#DCE5DC] opacity-60'
                }`}
              >
                <div className="flex items-center justify-between mb-1">
                  <span className="text-[10px] font-black uppercase">Step {s.id}</span>
                  {isCompleted ? (
                    <Check className="w-3.5 h-3.5 text-[#047857]" />
                  ) : (
                    <Icon className="w-3.5 h-3.5" />
                  )}
                </div>
                <div className="text-xs font-bold truncate">{s.name}</div>
              </button>
            );
          })}
        </div>
      </div>

      {error && (
        <div className="p-4 rounded-2xl bg-[#FFE4E6] border border-[#FECDD3] text-xs font-bold text-[#BE123C]">
          {error}
        </div>
      )}

      {/* Step 1: Farm & Soil */}
      {currentStep === 1 && (
        <div className="bg-white rounded-3xl border border-[#DCE5DC] p-8 shadow-card space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-extrabold text-[#14231A]">Step 1: Select Farm & Soil Test Baseline</h2>
              <p className="text-xs text-[#4A5F52] mt-1">
                Choose the land holding to analyze. Soil pH, EC, texture, and irrigation metrics will be checked against each crop.
              </p>
            </div>
            <button
              onClick={() => setCurrentStep(2)}
              className="px-5 py-2.5 rounded-xl bg-[#047857] hover:bg-[#065F46] text-white text-xs font-bold flex items-center gap-2 shadow-md transition-all"
            >
              Continue to Weights <ArrowRight className="w-4 h-4" />
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {farms.map((f) => {
              const isSelected = selectedFarm?.id === f.id;
              return (
                <div
                  key={f.id}
                  onClick={() => setSelectedFarmId(f.id)}
                  className={`p-5 rounded-2xl border cursor-pointer transition-all ${
                    isSelected
                      ? 'bg-[#ECF6EF] border-[#047857] shadow-sm'
                      : 'bg-[#F6F8F4] border-[#DCE5DC] hover:border-[#7A8E80]'
                  }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-extrabold text-sm text-[#14231A]">{f.name}</span>
                    {isSelected && (
                      <span className="w-2.5 h-2.5 rounded-full bg-[#047857]" />
                    )}
                  </div>
                  <div className="space-y-1 text-xs text-[#4A5F52]">
                    <div>Total Land: <strong className="text-[#14231A]">{f.land_ha} ha</strong></div>
                    <div>Season: <strong className="text-[#14231A] capitalize">{f.season}</strong></div>
                    <div>Soil Texture: <strong className="text-[#14231A] capitalize">{f.soil.texture}</strong></div>
                    <div>Soil pH: <strong className="text-[#14231A]">{f.soil.ph}</strong> (EC: {f.soil.ec} dS/m)</div>
                    <div>Water Available: <strong className="text-[#0D9488]">{f.water.irrigation_m3?.toLocaleString()} m³</strong></div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Step 2: Criteria Weights */}
      {currentStep === 2 && (
        <div className="bg-white rounded-3xl border border-[#DCE5DC] p-8 shadow-card space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-extrabold text-[#14231A]">Step 2: Assign Multi-Criteria Weights</h2>
              <p className="text-xs text-[#4A5F52] mt-1">
                Choose what matters most for your planning context: water demand, soil compatibility, expected profit, or market price stability.
              </p>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setCurrentStep(1)}
                className="px-4 py-2 rounded-xl bg-[#EEF3EC] text-xs font-bold text-[#14231A]"
              >
                Back
              </button>
              <button
                onClick={runRanking}
                disabled={loading}
                className="px-5 py-2.5 rounded-xl bg-[#047857] hover:bg-[#065F46] text-white text-xs font-bold flex items-center gap-2 shadow-md transition-all"
              >
                {loading ? 'Calculating...' : 'Run TOPSIS Ranking'} <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Quick Presets */}
          <div>
            <div className="text-xs font-bold text-[#7A8E80] uppercase tracking-wider mb-2">Preset Strategies</div>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              <button
                type="button"
                onClick={() => applyPreset({ water: 0.25, soil: 0.25, return: 0.25, variability: 0.25 })}
                className="p-3 rounded-xl bg-[#F6F8F4] border border-[#DCE5DC] hover:border-[#047857] text-left text-xs font-bold text-[#14231A]"
              >
                ⚖️ Balanced (25/25/25/25)
              </button>
              <button
                type="button"
                onClick={() => applyPreset({ water: 0.50, soil: 0.20, return: 0.20, variability: 0.10 })}
                className="p-3 rounded-xl bg-[#CCFBF1] border border-[#99F6E4] hover:border-[#0D9488] text-left text-xs font-bold text-[#0F766E]"
              >
                💧 Water-Saving (50% Water)
              </button>
              <button
                type="button"
                onClick={() => applyPreset({ water: 0.10, soil: 0.20, return: 0.60, variability: 0.10 })}
                className="p-3 rounded-xl bg-[#FEF3C7] border border-[#FDE68A] hover:border-[#D97706] text-left text-xs font-bold text-[#B45309]"
              >
                💰 Profit-First (60% Return)
              </button>
              <button
                type="button"
                onClick={() => applyPreset({ water: 0.20, soil: 0.20, return: 0.20, variability: 0.40 })}
                className="p-3 rounded-xl bg-[#FFE4E6] border border-[#FECDD3] hover:border-[#E11D48] text-left text-xs font-bold text-[#BE123C]"
              >
                🛡️ Low Market Risk (40% CV)
              </button>
            </div>
          </div>

          {/* Sliders */}
          <div className="space-y-4 pt-2">
            <div>
              <div className="flex justify-between text-xs font-bold mb-1">
                <span>💧 Water Demand (Cost)</span>
                <span className="text-[#0D9488]">{(weights.water * 100).toFixed(0)}%</span>
              </div>
              <input
                type="range"
                min="0"
                max="1"
                step="0.05"
                value={weights.water}
                onChange={(e) => setWeights({ ...weights, water: parseFloat(e.target.value) })}
                className="w-full accent-[#0D9488]"
              />
            </div>

            <div>
              <div className="flex justify-between text-xs font-bold mb-1">
                <span>🌱 Soil Suitability (Benefit)</span>
                <span className="text-[#047857]">{(weights.soil * 100).toFixed(0)}%</span>
              </div>
              <input
                type="range"
                min="0"
                max="1"
                step="0.05"
                value={weights.soil}
                onChange={(e) => setWeights({ ...weights, soil: parseFloat(e.target.value) })}
                className="w-full accent-[#047857]"
              />
            </div>

            <div>
              <div className="flex justify-between text-xs font-bold mb-1">
                <span>📈 Expected Return (Benefit)</span>
                <span className="text-[#D97706]">{(weights.return * 100).toFixed(0)}%</span>
              </div>
              <input
                type="range"
                min="0"
                max="1"
                step="0.05"
                value={weights.return}
                onChange={(e) => setWeights({ ...weights, return: parseFloat(e.target.value) })}
                className="w-full accent-[#D97706]"
              />
            </div>

            <div>
              <div className="flex justify-between text-xs font-bold mb-1">
                <span>📉 Price Variability Risk (Cost)</span>
                <span className="text-[#E11D48]">{(weights.variability * 100).toFixed(0)}%</span>
              </div>
              <input
                type="range"
                min="0"
                max="1"
                step="0.05"
                value={weights.variability}
                onChange={(e) => setWeights({ ...weights, variability: parseFloat(e.target.value) })}
                className="w-full accent-[#E11D48]"
              />
            </div>
          </div>
        </div>
      )}

      {/* Step 3: Ranking Results */}
      {currentStep === 3 && (
        <div className="bg-white rounded-3xl border border-[#DCE5DC] p-8 shadow-card space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-extrabold text-[#14231A]">Step 3: TOPSIS Ranking & Multi-Criteria Fit</h2>
              <p className="text-xs text-[#4A5F52] mt-1">
                Evaluated against the positive ideal solution ($A^+$) and negative ideal ($A^-$).
              </p>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setCurrentStep(2)}
                className="px-4 py-2 rounded-xl bg-[#EEF3EC] text-xs font-bold text-[#14231A]"
              >
                Change Weights
              </button>
              <button
                onClick={() => setCurrentStep(4)}
                className="px-5 py-2.5 rounded-xl bg-[#047857] hover:bg-[#065F46] text-white text-xs font-bold flex items-center gap-2 shadow-md transition-all"
              >
                Configure Optimizer <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </div>

          <div className="space-y-3">
            {rankingResult?.results?.slice(0, 6).map((r: any) => (
              <div key={r.crop_id} className="p-4 rounded-2xl bg-[#F6F8F4] border border-[#DCE5DC] flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className="w-8 h-8 rounded-full bg-[#047857] text-white font-black text-sm flex items-center justify-center">
                    {r.rank}
                  </div>
                  <div>
                    <div className="font-extrabold text-sm text-[#14231A]">{r.crop_name}</div>
                    <div className="text-xs text-[#4A5F52]">{r.explanation}</div>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-sm font-extrabold text-[#047857]">
                    {(r.closeness * 100).toFixed(1)}% Closeness
                  </div>
                  <div className="text-xs text-[#7A8E80]">
                    ₹{r.criteria_values?.return?.toLocaleString()}/ha
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Step 4: Portfolio Optimizer */}
      {currentStep === 4 && (
        <div className="bg-white rounded-3xl border border-[#DCE5DC] p-8 shadow-card space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-extrabold text-[#14231A]">Step 4: Solve Land Allocation (MILP)</h2>
              <p className="text-xs text-[#4A5F52] mt-1">
                Optimizes crop acreage under strict water, budget, labour, and diversification constraints.
              </p>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setCurrentStep(3)}
                className="px-4 py-2 rounded-xl bg-[#EEF3EC] text-xs font-bold text-[#14231A]"
              >
                Back
              </button>
              <button
                onClick={runOptimization}
                disabled={loading}
                className="px-5 py-2.5 rounded-xl bg-[#047857] hover:bg-[#065F46] text-white text-xs font-bold flex items-center gap-2 shadow-md transition-all"
              >
                {loading ? 'Optimizing...' : 'Solve Land Allocation'} <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-xs font-bold text-[#14231A] mb-1.5">Optimization Objective</label>
              <select
                value={objective}
                onChange={(e) => setObjective(e.target.value)}
                className="w-full px-3.5 py-2 rounded-xl border border-[#DCE5DC] bg-[#F6F8F4] text-xs font-bold text-[#14231A]"
              >
                <option value="max_return">Maximize Net Return (₹)</option>
                <option value="max_topsis">Maximize TOPSIS Benefit</option>
                <option value="balanced">Balanced Return & Risk</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-bold text-[#14231A] mb-1.5">Max Single Crop Share</label>
              <select
                value={maxShare}
                onChange={(e) => setMaxShare(parseFloat(e.target.value))}
                className="w-full px-3.5 py-2 rounded-xl border border-[#DCE5DC] bg-[#F6F8F4] text-xs font-bold text-[#14231A]"
              >
                <option value={0.30}>30% (Strict Diversification)</option>
                <option value={0.40}>40% (Recommended Standard)</option>
                <option value={0.50}>50% (Moderate Concentration)</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-bold text-[#14231A] mb-1.5">Minimum Crops to Plant</label>
              <select
                value={minCrops}
                onChange={(e) => setMinCrops(parseInt(e.target.value))}
                className="w-full px-3.5 py-2 rounded-xl border border-[#DCE5DC] bg-[#F6F8F4] text-xs font-bold text-[#14231A]"
              >
                <option value={2}>At least 2 crops</option>
                <option value={3}>At least 3 crops</option>
                <option value={4}>At least 4 crops</option>
              </select>
            </div>
          </div>

          {optimizationResult && (
            <div className="mt-6 pt-6 border-t border-[#DCE5DC] space-y-4">
              <div className="flex items-center justify-between">
                <span className="font-extrabold text-sm text-[#14231A]">Optimal Land Allocation Result</span>
                <span className="text-xs font-bold text-[#047857]">
                  Total Return: ₹{optimizationResult.totals?.net_return?.toLocaleString()}
                </span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                {optimizationResult.allocation?.map((a: any) => (
                  <div key={a.crop_id} className="p-3.5 rounded-2xl bg-[#ECF6EF] border border-[#A7F3D0]">
                    <div className="font-extrabold text-sm text-[#14231A]">{a.crop_name}</div>
                    <div className="text-xs text-[#047857] mt-1 font-bold">
                      {a.area_ha} ha ({((a.share || 0) * 100).toFixed(0)}% land)
                    </div>
                    <div className="text-[11px] text-[#4A5F52] mt-1">
                      Expected Profit: ₹{a.expected_return?.toLocaleString()}
                    </div>
                  </div>
                ))}
              </div>

              <div className="flex justify-end pt-2">
                <button
                  onClick={runSimulation}
                  disabled={loading}
                  className="px-5 py-2.5 rounded-xl bg-[#047857] hover:bg-[#065F46] text-white text-xs font-bold flex items-center gap-2 shadow-md"
                >
                  {loading ? 'Simulating...' : 'Test Climate & Price Shocks'} <ArrowRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Step 5: Simulation & Risk */}
      {currentStep === 5 && (
        <div className="bg-white rounded-3xl border border-[#DCE5DC] p-8 shadow-card space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-extrabold text-[#14231A]">Step 5: Monte Carlo Risk & Stress Test</h2>
              <p className="text-xs text-[#4A5F52] mt-1">
                2,500 stochastic trials simulating unpredictable drought and price collapses.
              </p>
            </div>
            <button
              onClick={() => setCurrentStep(6)}
              className="px-5 py-2.5 rounded-xl bg-[#047857] hover:bg-[#065F46] text-white text-xs font-bold flex items-center gap-2 shadow-md"
            >
              Generate Decision Report <ArrowRight className="w-4 h-4" />
            </button>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div className="p-4 rounded-2xl bg-[#F6F8F4] border border-[#DCE5DC]">
              <div className="text-xs text-[#7A8E80]">Mean Return</div>
              <div className="text-xl font-black text-[#14231A] mt-1">
                ₹{simulationResult?.stats?.mean?.toLocaleString() || '---'}
              </div>
            </div>
            <div className="p-4 rounded-2xl bg-[#F6F8F4] border border-[#DCE5DC]">
              <div className="text-xs text-[#7A8E80]">Probability of Loss</div>
              <div className="text-xl font-black text-[#E11D48] mt-1">
                {simulationResult?.stats?.p_loss_pct || 0}%
              </div>
            </div>
            <div className="p-4 rounded-2xl bg-[#F6F8F4] border border-[#DCE5DC]">
              <div className="text-xs text-[#7A8E80]">VaR (5th Percentile)</div>
              <div className="text-xl font-black text-[#D97706] mt-1">
                ₹{simulationResult?.stats?.p5_var?.toLocaleString() || '---'}
              </div>
            </div>
            <div className="p-4 rounded-2xl bg-[#F6F8F4] border border-[#DCE5DC]">
              <div className="text-xs text-[#7A8E80]">Risk Standard Dev</div>
              <div className="text-xl font-black text-[#0D9488] mt-1">
                ₹{simulationResult?.stats?.std?.toLocaleString() || '---'}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Step 6: Decision Report */}
      {currentStep === 6 && (
        <div className="bg-white rounded-3xl border border-[#DCE5DC] p-8 shadow-card text-center space-y-6">
          <div className="w-16 h-16 rounded-full bg-[#D1FAE5] text-[#047857] flex items-center justify-center mx-auto">
            <FileText className="w-8 h-8" />
          </div>

          <div>
            <h2 className="text-2xl font-extrabold text-[#14231A]">Planning Pipeline Completed!</h2>
            <p className="text-xs text-[#4A5F52] mt-1 max-w-md mx-auto">
              Your multi-criteria ranking and linear land allocation portfolio are successfully computed and recorded in MongoDB Atlas.
            </p>
          </div>

          <div className="flex flex-wrap justify-center gap-4 pt-4">
            <button
              onClick={() => navigate('/app/reports')}
              className="px-6 py-3 rounded-xl bg-[#047857] hover:bg-[#065F46] text-white text-xs font-bold shadow-md shadow-[#047857]/20 flex items-center gap-2"
            >
              Open Full Decision Reports Page
              <ArrowRight className="w-4 h-4" />
            </button>
            <button
              onClick={() => navigate('/app')}
              className="px-6 py-3 rounded-xl bg-[#EEF3EC] hover:bg-[#DCE5DC] text-[#14231A] text-xs font-bold"
            >
              Return to Dashboard
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
