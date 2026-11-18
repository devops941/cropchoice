import React, { useState, useEffect } from 'react';
import { useFarm } from '../context/FarmContext';
import { cropsApi } from '../api/client';
import { Leaf, Search, Droplet, Clock, DollarSign, CheckCircle2, AlertCircle } from 'lucide-react';

export const CropsPage: React.FC = () => {
  const { selectedFarm } = useFarm();
  const [crops, setCrops] = useState<any[]>([]);
  const [search, setSearch] = useState('');
  const [category, setCategory] = useState<string>('all');
  const [loading, setLoading] = useState(true);

  const fetchCrops = async () => {
    try {
      setLoading(true);
      const data = await cropsApi.list({
        search: search || undefined,
        category: category !== 'all' ? category : undefined,
      });
      setCrops(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCrops();
  }, [category]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    fetchCrops();
  };

  const categories = ['all', 'Cereals', 'Oilseeds', 'Pulses', 'Horticulture', 'Spices', 'Millets', 'Commercial'];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-3xl border border-[#DCE5DC] p-6 shadow-card flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Leaf className="w-5 h-5 text-[#047857]" />
            <span className="text-xs font-bold uppercase tracking-wider text-[#047857]">
              Shared Crop Knowledgebase
            </span>
          </div>
          <h1 className="text-2xl font-extrabold text-[#14231A]">Crop Library & Agronomic Profiles</h1>
          <p className="text-xs text-[#4A5F52] mt-1">
            Official package of practices, physiological water demands, and soil tolerance boundaries.
          </p>
        </div>

        <form onSubmit={handleSearchSubmit} className="flex items-center gap-2">
          <div className="relative">
            <Search className="w-4 h-4 text-[#7A8E80] absolute left-3 top-2.5" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search crops..."
              className="pl-9 pr-4 py-2 rounded-xl border border-[#DCE5DC] bg-[#F6F8F4] text-xs font-semibold text-[#14231A] outline-none focus:border-[#047857]"
            />
          </div>
          <button
            type="submit"
            className="px-4 py-2 rounded-xl bg-[#047857] text-white text-xs font-bold hover:bg-[#065F46]"
          >
            Filter
          </button>
        </form>
      </div>

      {/* Categories Filter Strip */}
      <div className="flex items-center gap-2 overflow-x-auto pb-1">
        {categories.map((cat) => (
          <button
            key={cat}
            onClick={() => setCategory(cat)}
            className={`px-3.5 py-1.5 rounded-full text-xs font-bold capitalize whitespace-nowrap transition-all ${
              category === cat
                ? 'bg-[#047857] text-white shadow-sm'
                : 'bg-white border border-[#DCE5DC] text-[#4A5F52] hover:bg-[#EEF3EC]'
            }`}
          >
            {cat}
          </button>
        ))}
      </div>

      {/* Grid of Crops */}
      {loading ? (
        <div className="py-20 text-center text-xs font-semibold text-[#7A8E80]">
          Loading crops catalog...
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-5">
          {crops.map((c) => (
            <div
              key={c.id}
              className="bg-white rounded-3xl border border-[#DCE5DC] p-5 shadow-card hover:shadow-card-hover transition-all flex flex-col justify-between"
            >
              <div>
                <div className="flex items-start justify-between mb-2">
                  <h3 className="font-extrabold text-base text-[#14231A]">{c.name}</h3>
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-[#D1FAE5] text-[#065F46] border border-[#A7F3D0]">
                    {c.category}
                  </span>
                </div>

                <div className="mt-4 space-y-2 text-xs text-[#4A5F52]">
                  <div className="flex justify-between py-1 border-b border-[#DCE5DC]/60">
                    <span>Duration:</span>
                    <strong className="text-[#14231A]">{c.duration_days} days</strong>
                  </div>
                  <div className="flex justify-between py-1 border-b border-[#DCE5DC]/60">
                    <span>Water Demand:</span>
                    <strong className="text-[#0D9488]">{c.water_req_mm} mm</strong>
                  </div>
                  <div className="flex justify-between py-1 border-b border-[#DCE5DC]/60">
                    <span>Typical Yield:</span>
                    <strong className="text-[#14231A]">{c.typical_yield_t_ha} t/ha</strong>
                  </div>
                  <div className="flex justify-between py-1 border-b border-[#DCE5DC]/60">
                    <span>Optimal pH:</span>
                    <strong className="text-[#047857]">
                      {c.soil?.ph?.opt_min || 6.0} - {c.soil?.ph?.opt_max || 7.5}
                    </strong>
                  </div>
                  <div className="flex justify-between py-1">
                    <span>Seasons:</span>
                    <strong className="text-[#14231A] capitalize">{c.seasons?.join(', ')}</strong>
                  </div>
                </div>
              </div>

              <div className="mt-5 pt-3 border-t border-[#DCE5DC] text-[11px] text-[#7A8E80] italic">
                {c.source_note || 'Official Agricultural University Handbook'}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
