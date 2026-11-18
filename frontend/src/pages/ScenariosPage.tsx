import React, { useState, useEffect } from 'react';
import { useFarm } from '../context/FarmContext';
import { scenariosApi } from '../api/client';
import { Layers, Plus, TrendingDown, Droplet, CheckCircle2, Trash2 } from 'lucide-react';

export const ScenariosPage: React.FC = () => {
  const { selectedFarm, selectedFarmId } = useFarm();
  const [scenarios, setScenarios] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  // New scenario form
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [irrigationPct, setIrrigationPct] = useState(-30);
  const [pricePct, setPricePct] = useState(0);
  const [budgetPct, setBudgetPct] = useState(0);

  const fetchScenarios = async () => {
    if (!selectedFarmId) return;
    try {
      setLoading(true);
      const res = await scenariosApi.list(selectedFarmId);
      setScenarios(res);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchScenarios();
  }, [selectedFarmId]);

  const handleCreateScenario = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFarmId) return;
    try {
      await scenariosApi.create({
        farm_id: selectedFarmId,
        name,
        description,
        modifications: {
          irrigation_pct: Number(irrigationPct),
          price_pct: Number(pricePct),
          budget_pct: Number(budgetPct),
        },
      });
      setName('');
      setDescription('');
      fetchScenarios();
    } catch (err: any) {
      alert(err.message || 'Failed to simulate scenario');
    }
  };

  const handleDelete = async (id: string) => {
    await scenariosApi.delete(id);
    fetchScenarios();
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-3xl border border-[#DCE5DC] p-6 shadow-card">
        <div className="flex items-center gap-2 mb-1">
          <Layers className="w-5 h-5 text-[#047857]" />
          <span className="text-xs font-bold uppercase tracking-wider text-[#047857]">
            Stress Testing & What-If Engine
          </span>
        </div>
        <h1 className="text-2xl font-extrabold text-[#14231A]">Climate & Market Scenarios</h1>
        <p className="text-xs text-[#4A5F52] mt-1">
          Clone the baseline farm, apply rainfall shortages or price shocks, and compare impacts on crop selection and revenue.
        </p>
      </div>

      {/* Scenario Creator Form */}
      <div className="bg-white rounded-3xl border border-[#DCE5DC] p-6 shadow-card">
        <h2 className="text-base font-extrabold text-[#14231A] mb-4">Create New What-If Scenario</h2>
        <form onSubmit={handleCreateScenario} className="space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-bold text-[#14231A] mb-1">Scenario Title</label>
              <input
                type="text"
                required
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="e.g. Monsoon Delay (-40% Water)"
                className="w-full px-3 py-2 rounded-xl border border-[#DCE5DC] bg-[#F6F8F4] text-xs font-semibold outline-none"
              />
            </div>
            <div>
              <label className="block text-xs font-bold text-[#14231A] mb-1">Description</label>
              <input
                type="text"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Brief justification"
                className="w-full px-3 py-2 rounded-xl border border-[#DCE5DC] bg-[#F6F8F4] text-xs font-semibold outline-none"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-2">
            <div>
              <label className="block text-xs font-bold text-[#14231A] mb-1">
                Irrigation / Rainfall Shock: {irrigationPct}%
              </label>
              <input
                type="range"
                min="-60"
                max="50"
                step="5"
                value={irrigationPct}
                onChange={(e) => setIrrigationPct(parseInt(e.target.value))}
                className="w-full accent-[#0D9488]"
              />
            </div>

            <div>
              <label className="block text-xs font-bold text-[#14231A] mb-1">
                Market Price Shock: {pricePct}%
              </label>
              <input
                type="range"
                min="-50"
                max="50"
                step="5"
                value={pricePct}
                onChange={(e) => setPricePct(parseInt(e.target.value))}
                className="w-full accent-[#D97706]"
              />
            </div>

            <div>
              <label className="block text-xs font-bold text-[#14231A] mb-1">
                Budget Adjustment: {budgetPct}%
              </label>
              <input
                type="range"
                min="-50"
                max="100"
                step="10"
                value={budgetPct}
                onChange={(e) => setBudgetPct(parseInt(e.target.value))}
                className="w-full accent-[#047857]"
              />
            </div>
          </div>

          <div className="flex justify-end pt-2">
            <button
              type="submit"
              className="px-5 py-2.5 rounded-xl bg-[#047857] hover:bg-[#065F46] text-white text-xs font-bold shadow-md shadow-[#047857]/20 flex items-center gap-2"
            >
              <Plus className="w-4 h-4" />
              Simulate Scenario
            </button>
          </div>
        </form>
      </div>

      {/* Scenarios Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {scenarios.map((sc) => (
          <div key={sc.id} className="bg-white rounded-3xl border border-[#DCE5DC] p-6 shadow-card flex flex-col justify-between">
            <div>
              <div className="flex justify-between items-start">
                <h3 className="font-extrabold text-sm text-[#14231A]">{sc.name}</h3>
                <button
                  onClick={() => handleDelete(sc.id)}
                  className="text-[#7A8E80] hover:text-[#E11D48]"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
              <p className="text-xs text-[#4A5F52] mt-1">{sc.description}</p>

              <div className="mt-4 p-3 rounded-2xl bg-[#F6F8F4] border border-[#DCE5DC] space-y-2 text-xs">
                <div className="flex justify-between">
                  <span>Net Return:</span>
                  <strong className="text-[#D97706]">₹{sc.summary?.net_return?.toLocaleString()}</strong>
                </div>
                <div className="flex justify-between">
                  <span>Water Used:</span>
                  <strong className="text-[#0D9488]">{sc.summary?.water_m3?.toLocaleString()} m³</strong>
                </div>
                <div className="flex justify-between">
                  <span>Effective Crops:</span>
                  <strong className="text-[#047857]">{sc.summary?.effective_crops}</strong>
                </div>
                <div className="flex justify-between pt-1 border-t border-[#DCE5DC]">
                  <span>Top Allocation:</span>
                  <span className="font-bold text-[#14231A]">{sc.summary?.top_crops?.join(', ')}</span>
                </div>
              </div>
            </div>

            <div className="mt-4 pt-3 border-t border-[#DCE5DC] flex items-center justify-between text-[11px] text-[#7A8E80]">
              <span>Feasibility: Verified</span>
              <CheckCircle2 className="w-4 h-4 text-[#047857]" />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
