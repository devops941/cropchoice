import React, { useState } from 'react';
import { useFarm } from '../context/FarmContext';
import { farmsApi } from '../api/client';
import { MapPin, Plus, Edit2, Trash2, Check, X, Droplet, Layers, DollarSign } from 'lucide-react';

export const FarmsPage: React.FC = () => {
  const { farms, loadFarms, selectedFarmId, setSelectedFarmId } = useFarm();
  const [showModal, setShowModal] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const initialForm = {
    name: '',
    land_ha: 5.0,
    season: 'kharif',
    ph: 6.8,
    ec: 0.6,
    oc: 0.75,
    texture: 'loam',
    drainage: 'good',
    rainfall_mm: 650,
    irrigation_m3: 18000,
    budget_inr: 350000,
    labour_person_days: 300,
  };

  const [form, setForm] = useState(initialForm);

  const handleOpenCreate = () => {
    setEditingId(null);
    setForm(initialForm);
    setShowModal(true);
  };

  const handleOpenEdit = (f: any) => {
    setEditingId(f.id);
    setForm({
      name: f.name,
      land_ha: f.land_ha,
      season: f.season || 'kharif',
      ph: f.soil?.ph || 6.8,
      ec: f.soil?.ec || 0.6,
      oc: f.soil?.oc || 0.75,
      texture: f.soil?.texture || 'loam',
      drainage: f.soil?.drainage || 'good',
      rainfall_mm: f.water?.rainfall_mm || 650,
      irrigation_m3: f.water?.irrigation_m3 || 18000,
      budget_inr: f.budget_inr || 350000,
      labour_person_days: f.labour_person_days || 300,
    });
    setShowModal(true);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const payload = {
        name: form.name,
        land_ha: Number(form.land_ha),
        season: form.season,
        soil: {
          ph: Number(form.ph),
          ec: Number(form.ec),
          oc: Number(form.oc),
          texture: form.texture,
          drainage: form.drainage,
          n: 280,
          p: 22,
          k: 310,
        },
        water: {
          rainfall_mm: Number(form.rainfall_mm),
          effective_rainfall_pct: 70,
          irrigation_m3: Number(form.irrigation_m3),
        },
        budget_inr: Number(form.budget_inr),
        labour_person_days: Number(form.labour_person_days),
      };

      if (editingId) {
        await farmsApi.update(editingId, payload);
      } else {
        await farmsApi.create(payload);
      }

      await loadFarms();
      setShowModal(false);
    } catch (err: any) {
      alert(err.message || 'Operation failed');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (confirm('Are you sure you want to delete this farm profile?')) {
      await farmsApi.delete(id);
      await loadFarms();
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-3xl border border-[#DCE5DC] p-6 shadow-card flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <MapPin className="w-5 h-5 text-[#047857]" />
            <span className="text-xs font-bold uppercase tracking-wider text-[#047857]">
              Farm Profiles & Soil Tests
            </span>
          </div>
          <h1 className="text-2xl font-extrabold text-[#14231A]">Farm Management</h1>
          <p className="text-xs text-[#4A5F52] mt-1">
            Maintain land parcel dimensions, soil laboratory test results, and seasonal water availability.
          </p>
        </div>

        <button
          onClick={handleOpenCreate}
          className="px-4 py-2.5 rounded-xl bg-[#047857] hover:bg-[#065F46] text-white text-xs font-bold flex items-center gap-2 shadow-md shadow-[#047857]/20 transition-all"
        >
          <Plus className="w-4 h-4" />
          Add Farm Profile
        </button>
      </div>

      {/* Farm Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {farms.map((f) => {
          const isSelected = selectedFarmId === f.id;
          return (
            <div
              key={f.id}
              className={`bg-white rounded-3xl border p-6 shadow-card flex flex-col justify-between transition-all ${
                isSelected ? 'border-[#047857] ring-2 ring-[#047857]/15' : 'border-[#DCE5DC]'
              }`}
            >
              <div>
                <div className="flex items-start justify-between">
                  <div>
                    <h3 className="text-base font-extrabold text-[#14231A]">{f.name}</h3>
                    <p className="text-xs text-[#4A5F52] mt-0.5">
                      {f.land_ha} ha · <span className="capitalize">{f.season}</span> season
                    </p>
                  </div>
                  {isSelected && (
                    <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-[#D1FAE5] text-[#065F46] border border-[#A7F3D0]">
                      Active Farm
                    </span>
                  )}
                </div>

                {/* Soil & Water parameters */}
                <div className="mt-5 space-y-2.5 text-xs text-[#4A5F52]">
                  <div className="flex justify-between py-1 border-b border-[#DCE5DC]/60">
                    <span>Soil pH:</span>
                    <strong className="text-[#14231A]">{f.soil?.ph}</strong>
                  </div>
                  <div className="flex justify-between py-1 border-b border-[#DCE5DC]/60">
                    <span>Salinity (EC):</span>
                    <strong className="text-[#14231A]">{f.soil?.ec} dS/m</strong>
                  </div>
                  <div className="flex justify-between py-1 border-b border-[#DCE5DC]/60">
                    <span>Organic Carbon (OC):</span>
                    <strong className="text-[#14231A]">{f.soil?.oc}%</strong>
                  </div>
                  <div className="flex justify-between py-1 border-b border-[#DCE5DC]/60">
                    <span>Texture / Drainage:</span>
                    <strong className="text-[#14231A] capitalize">{f.soil?.texture} · {f.soil?.drainage}</strong>
                  </div>
                  <div className="flex justify-between py-1 border-b border-[#DCE5DC]/60">
                    <span>Irrigation Volume:</span>
                    <strong className="text-[#0D9488]">{f.water?.irrigation_m3?.toLocaleString()} m³</strong>
                  </div>
                  <div className="flex justify-between py-1">
                    <span>Working Budget:</span>
                    <strong className="text-[#D97706]">₹{f.budget_inr?.toLocaleString()}</strong>
                  </div>
                </div>
              </div>

              <div className="mt-6 pt-4 border-t border-[#DCE5DC] flex items-center justify-between">
                <button
                  onClick={() => setSelectedFarmId(f.id)}
                  className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all ${
                    isSelected
                      ? 'bg-[#047857] text-white'
                      : 'bg-[#EEF3EC] text-[#14231A] hover:bg-[#DCE5DC]'
                  }`}
                >
                  {isSelected ? 'Selected' : 'Set as Active'}
                </button>

                <div className="flex items-center gap-2">
                  <button
                    onClick={() => handleOpenEdit(f)}
                    className="p-2 rounded-xl text-[#4A5F52] hover:text-[#047857] hover:bg-[#EEF3EC] transition-colors"
                  >
                    <Edit2 className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => handleDelete(f.id)}
                    className="p-2 rounded-xl text-[#7A8E80] hover:text-[#E11D48] hover:bg-[#FFE4E6] transition-colors"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Modal Dialog */}
      {showModal && (
        <div className="fixed inset-0 z-50 bg-black/40 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-3xl border border-[#DCE5DC] p-6 lg:p-8 max-w-xl w-full shadow-2xl max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-extrabold text-[#14231A]">
                {editingId ? 'Edit Farm Profile' : 'New Farm & Soil Record'}
              </h2>
              <button
                onClick={() => setShowModal(false)}
                className="p-2 text-[#7A8E80] hover:text-[#14231A]"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="col-span-2">
                  <label className="block text-xs font-bold text-[#14231A] mb-1">Farm Name</label>
                  <input
                    type="text"
                    required
                    value={form.name}
                    onChange={(e) => setForm({ ...form, name: e.target.value })}
                    className="w-full px-3 py-2 rounded-xl border border-[#DCE5DC] bg-[#F6F8F4] text-xs font-semibold text-[#14231A] outline-none"
                    placeholder="e.g. Cauvery Riverbank Parcel"
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold text-[#14231A] mb-1">Total Land (ha)</label>
                  <input
                    type="number"
                    step="0.1"
                    min="0.5"
                    value={form.land_ha}
                    onChange={(e) => setForm({ ...form, land_ha: parseFloat(e.target.value) })}
                    className="w-full px-3 py-2 rounded-xl border border-[#DCE5DC] bg-[#F6F8F4] text-xs font-semibold text-[#14231A]"
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold text-[#14231A] mb-1">Season</label>
                  <select
                    value={form.season}
                    onChange={(e) => setForm({ ...form, season: e.target.value })}
                    className="w-full px-3 py-2 rounded-xl border border-[#DCE5DC] bg-[#F6F8F4] text-xs font-semibold text-[#14231A]"
                  >
                    <option value="kharif">Kharif (Monsoon)</option>
                    <option value="rabi">Rabi (Winter)</option>
                    <option value="zaid">Zaid (Summer)</option>
                  </select>
                </div>
              </div>

              <div className="p-4 rounded-2xl bg-[#F6F8F4] border border-[#DCE5DC] space-y-3">
                <div className="text-xs font-bold text-[#047857] uppercase tracking-wider">Soil Laboratory Test</div>
                <div className="grid grid-cols-3 gap-3">
                  <div>
                    <label className="block text-[11px] font-bold text-[#4A5F52] mb-1">pH (3-10)</label>
                    <input
                      type="number"
                      step="0.1"
                      value={form.ph}
                      onChange={(e) => setForm({ ...form, ph: parseFloat(e.target.value) })}
                      className="w-full px-2.5 py-1.5 rounded-lg border border-[#DCE5DC] bg-white text-xs font-semibold"
                    />
                  </div>
                  <div>
                    <label className="block text-[11px] font-bold text-[#4A5F52] mb-1">EC (dS/m)</label>
                    <input
                      type="number"
                      step="0.1"
                      value={form.ec}
                      onChange={(e) => setForm({ ...form, ec: parseFloat(e.target.value) })}
                      className="w-full px-2.5 py-1.5 rounded-lg border border-[#DCE5DC] bg-white text-xs font-semibold"
                    />
                  </div>
                  <div>
                    <label className="block text-[11px] font-bold text-[#4A5F52] mb-1">OC (%)</label>
                    <input
                      type="number"
                      step="0.05"
                      value={form.oc}
                      onChange={(e) => setForm({ ...form, oc: parseFloat(e.target.value) })}
                      className="w-full px-2.5 py-1.5 rounded-lg border border-[#DCE5DC] bg-white text-xs font-semibold"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-[11px] font-bold text-[#4A5F52] mb-1">Texture</label>
                    <select
                      value={form.texture}
                      onChange={(e) => setForm({ ...form, texture: e.target.value })}
                      className="w-full px-2.5 py-1.5 rounded-lg border border-[#DCE5DC] bg-white text-xs font-semibold"
                    >
                      <option value="loam">Loam</option>
                      <option value="sandy_loam">Sandy Loam</option>
                      <option value="clay_loam">Clay Loam</option>
                      <option value="clay">Clay</option>
                      <option value="sandy">Sandy</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-[11px] font-bold text-[#4A5F52] mb-1">Drainage</label>
                    <select
                      value={form.drainage}
                      onChange={(e) => setForm({ ...form, drainage: e.target.value })}
                      className="w-full px-2.5 py-1.5 rounded-lg border border-[#DCE5DC] bg-white text-xs font-semibold"
                    >
                      <option value="good">Well Drained</option>
                      <option value="moderate">Moderately Drained</option>
                      <option value="poor">Poorly Drained</option>
                    </select>
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-bold text-[#14231A] mb-1">Irrigation Volume (m³)</label>
                  <input
                    type="number"
                    value={form.irrigation_m3}
                    onChange={(e) => setForm({ ...form, irrigation_m3: parseFloat(e.target.value) })}
                    className="w-full px-3 py-2 rounded-xl border border-[#DCE5DC] bg-[#F6F8F4] text-xs font-semibold"
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold text-[#14231A] mb-1">Working Budget (INR)</label>
                  <input
                    type="number"
                    value={form.budget_inr}
                    onChange={(e) => setForm({ ...form, budget_inr: parseFloat(e.target.value) })}
                    className="w-full px-3 py-2 rounded-xl border border-[#DCE5DC] bg-[#F6F8F4] text-xs font-semibold"
                  />
                </div>
              </div>

              <div className="flex justify-end gap-3 pt-4">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-4 py-2 rounded-xl bg-[#EEF3EC] text-xs font-bold text-[#14231A]"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={loading}
                  className="px-5 py-2 rounded-xl bg-[#047857] hover:bg-[#065F46] text-white text-xs font-bold shadow-md shadow-[#047857]/20"
                >
                  {loading ? 'Saving...' : 'Save Farm Record'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
