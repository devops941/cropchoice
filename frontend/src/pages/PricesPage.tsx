import React, { useState, useEffect } from 'react';
import { pricesApi, cropsApi } from '../api/client';
import { TrendingUp, Plus, DollarSign, Calendar, BarChart2, ShieldCheck } from 'lucide-react';
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  Tooltip, 
  ResponsiveContainer, 
  CartesianGrid 
} from 'recharts';

export const PricesPage: React.FC = () => {
  const [crops, setCrops] = useState<any[]>([]);
  const [selectedCropId, setSelectedCropId] = useState<string>('');
  const [prices, setPrices] = useState<any[]>([]);
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  // New price state
  const [month, setMonth] = useState('2024-12');
  const [modalPrice, setModalPrice] = useState(2500);

  useEffect(() => {
    cropsApi.list().then((res) => {
      setCrops(res);
      if (res.length > 0) {
        setSelectedCropId(res[0].id);
      }
    });
  }, []);

  useEffect(() => {
    if (!selectedCropId) return;
    setLoading(true);
    Promise.all([
      pricesApi.list({ crop_id: selectedCropId, limit: 120 }),
      pricesApi.getStats(selectedCropId, 36)
    ]).then(([priceList, statsData]) => {
      setPrices(priceList);
      setStats(statsData);
    }).finally(() => {
      setLoading(false);
    });
  }, [selectedCropId]);

  const handleAddPrice = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedCropId) return;
    try {
      await pricesApi.add({
        crop_id: selectedCropId,
        month,
        modal_price_per_quintal: Number(modalPrice),
        market: 'APMC Central',
      });
      const updatedList = await pricesApi.list({ crop_id: selectedCropId, limit: 120 });
      setPrices(updatedList);
      const updatedStats = await pricesApi.getStats(selectedCropId, 36);
      setStats(updatedStats);
      alert('Price record recorded successfully.');
    } catch (err: any) {
      alert(err.message || 'Failed to add price point');
    }
  };

  const chartData = prices.map((p) => ({
    month: p.month,
    price: p.modal_price_per_quintal,
  }));

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-3xl border border-[#DCE5DC] p-6 shadow-card flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <TrendingUp className="w-5 h-5 text-[#D97706]" />
            <span className="text-xs font-bold uppercase tracking-wider text-[#D97706]">
              Agmarknet Mandi Price Statistics
            </span>
          </div>
          <h1 className="text-2xl font-extrabold text-[#14231A]">Mandi Prices & Market Volatility</h1>
          <p className="text-xs text-[#4A5F52] mt-1">
            10-year monthly historical modal prices used to evaluate expected return and price variability (CV).
          </p>
        </div>

        {/* Crop Selector */}
        {crops.length > 0 && (
          <div className="flex items-center gap-2">
            <span className="text-xs font-bold text-[#4A5F52]">Select Crop:</span>
            <select
              value={selectedCropId}
              onChange={(e) => setSelectedCropId(e.target.value)}
              className="px-3 py-2 rounded-xl border border-[#DCE5DC] bg-[#F6F8F4] text-xs font-bold text-[#14231A] outline-none"
            >
              {crops.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name}
                </option>
              ))}
            </select>
          </div>
        )}
      </div>

      {/* Stats Cards */}
      {stats && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <div className="p-4 rounded-2xl bg-white border border-[#DCE5DC] shadow-card">
            <div className="text-[11px] font-bold text-[#7A8E80] uppercase">Mean Price (36 Mo)</div>
            <div className="text-2xl font-black text-[#14231A] mt-1 tabular-nums">
              ₹{stats.mean_price?.toLocaleString()}
            </div>
            <div className="text-xs text-[#4A5F52] mt-0.5">Per quintal (100 kg)</div>
          </div>

          <div className="p-4 rounded-2xl bg-white border border-[#DCE5DC] shadow-card">
            <div className="text-[11px] font-bold text-[#7A8E80] uppercase">Price Variability (CV)</div>
            <div className="text-2xl font-black text-[#E11D48] mt-1 tabular-nums">
              {(stats.cv * 100).toFixed(1)}%
            </div>
            <div className="text-xs text-[#BE123C] mt-0.5 font-semibold">
              {stats.cv > 0.25 ? 'High Volatility' : 'Stable Price'}
            </div>
          </div>

          <div className="p-4 rounded-2xl bg-white border border-[#DCE5DC] shadow-card">
            <div className="text-[11px] font-bold text-[#7A8E80] uppercase">Historical Range</div>
            <div className="text-xl font-black text-[#047857] mt-1 tabular-nums">
              ₹{stats.min_price} - ₹{stats.max_price}
            </div>
            <div className="text-xs text-[#4A5F52] mt-0.5">Min / Max modal values</div>
          </div>

          <div className="p-4 rounded-2xl bg-white border border-[#DCE5DC] shadow-card">
            <div className="text-[11px] font-bold text-[#7A8E80] uppercase">Data Observations</div>
            <div className="text-2xl font-black text-[#0D9488] mt-1 tabular-nums">
              {stats.count} Months
            </div>
            <div className="text-xs text-[#0F766E] mt-0.5 font-semibold">
              {stats.is_fallback ? '⚠️ Under 24 mo' : '✓ Full History'}
            </div>
          </div>
        </div>
      )}

      {/* Chart & Add Price Form */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Chart (8 cols) */}
        <div className="lg:col-span-8 bg-white rounded-3xl border border-[#DCE5DC] p-6 shadow-card">
          <h2 className="text-base font-extrabold text-[#14231A] mb-1">Monthly Modal Price Trajectory</h2>
          <p className="text-xs text-[#4A5F52] mb-6">Historical mandi price series (INR per quintal)</p>

          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#EEF3EC" />
                <XAxis dataKey="month" tick={{ fontSize: 10 }} />
                <YAxis tick={{ fontSize: 10 }} />
                <Tooltip
                  formatter={(val: any) => [`₹${val}`, 'Modal Price']}
                  contentStyle={{ backgroundColor: '#ffffff', borderColor: '#DCE5DC', borderRadius: '12px' }}
                />
                <Line
                  type="monotone"
                  dataKey="price"
                  stroke="#D97706"
                  strokeWidth={2.5}
                  dot={false}
                  activeDot={{ r: 5, fill: '#047857' }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Add Entry Form (4 cols) */}
        <div className="lg:col-span-4 bg-white rounded-3xl border border-[#DCE5DC] p-6 shadow-card flex flex-col justify-between">
          <div>
            <h2 className="text-base font-extrabold text-[#14231A] mb-1">Log New Mandi Price</h2>
            <p className="text-xs text-[#4A5F52] mb-4">Record official Agmarknet trade price</p>

            <form onSubmit={handleAddPrice} className="space-y-4">
              <div>
                <label className="block text-xs font-bold text-[#14231A] mb-1">Month (YYYY-MM)</label>
                <input
                  type="text"
                  required
                  value={month}
                  onChange={(e) => setMonth(e.target.value)}
                  placeholder="2025-01"
                  className="w-full px-3 py-2 rounded-xl border border-[#DCE5DC] bg-[#F6F8F4] text-xs font-semibold outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-[#14231A] mb-1">Modal Price (₹/Quintal)</label>
                <input
                  type="number"
                  required
                  value={modalPrice}
                  onChange={(e) => setModalPrice(parseFloat(e.target.value))}
                  className="w-full px-3 py-2 rounded-xl border border-[#DCE5DC] bg-[#F6F8F4] text-xs font-semibold outline-none"
                />
              </div>

              <button
                type="submit"
                className="w-full mt-2 py-2.5 rounded-xl bg-[#047857] hover:bg-[#065F46] text-white text-xs font-bold shadow-md shadow-[#047857]/20 flex items-center justify-center gap-2"
              >
                <Plus className="w-4 h-4" />
                Add Price Observation
              </button>
            </form>
          </div>

          <div className="mt-4 p-3 rounded-2xl bg-[#F6F8F4] border border-[#DCE5DC] text-[11px] text-[#7A8E80]">
            Mandi prices can also be bulk uploaded via CSV from the <strong>Upload Data Center</strong>.
          </div>
        </div>
      </div>
    </div>
  );
};
