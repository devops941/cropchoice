import React, { useState } from 'react';
import { useFarm } from '../context/FarmContext';
import { reportsApi, importExportApi } from '../api/client';
import { FileText, Printer, Download, Sparkles, CheckCircle2, ShieldAlert } from 'lucide-react';

export const ReportsPage: React.FC = () => {
  const { selectedFarm, selectedFarmId } = useFarm();
  const [report, setReport] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const generateReport = async () => {
    if (!selectedFarmId) return;
    try {
      setLoading(true);
      const res = await reportsApi.generate({ farm_id: selectedFarmId });
      setReport(res);
    } catch (err: any) {
      alert(err.message || 'Report generation failed');
    } finally {
      setLoading(false);
    }
  };

  const handlePrint = () => {
    window.print();
  };

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      {/* Header */}
      <div className="bg-white rounded-3xl border border-[#DCE5DC] p-6 shadow-card flex flex-col sm:flex-row sm:items-center justify-between gap-4 print:hidden">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <FileText className="w-5 h-5 text-[#047857]" />
            <span className="text-xs font-bold uppercase tracking-wider text-[#047857]">
              Audited Decision Document
            </span>
          </div>
          <h1 className="text-2xl font-extrabold text-[#14231A]">Crop Planning Decision Reports</h1>
          <p className="text-xs text-[#4A5F52] mt-1">
            Compile complete mathematical findings, criteria weight justifications, and optimal acreage maps.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={generateReport}
            disabled={loading || !selectedFarmId}
            className="px-5 py-2.5 rounded-xl bg-[#047857] hover:bg-[#065F46] disabled:opacity-50 text-white text-xs font-bold shadow-md shadow-[#047857]/20 flex items-center gap-2"
          >
            <Sparkles className="w-4 h-4" />
            {loading ? 'Compiling Report...' : 'Generate New Report'}
          </button>

          {report && (
            <button
              onClick={handlePrint}
              className="px-4 py-2.5 rounded-xl bg-[#EEF3EC] hover:bg-[#DCE5DC] text-[#14231A] text-xs font-bold flex items-center gap-2 border border-[#DCE5DC]"
            >
              <Printer className="w-4 h-4 text-[#047857]" />
              Print / Save PDF
            </button>
          )}
        </div>
      </div>

      {report ? (
        <div className="bg-white rounded-3xl border border-[#DCE5DC] p-8 lg:p-12 shadow-card space-y-8 print:border-none print:shadow-none print:p-0">
          {/* Document Header */}
          <div className="border-b border-[#DCE5DC] pb-6 flex justify-between items-start">
            <div>
              <div className="text-[11px] font-bold text-[#047857] uppercase tracking-wider">
                CropChoice Agricultural Decision Report
              </div>
              <h2 className="text-2xl font-black text-[#14231A] mt-1">{report.title}</h2>
              <p className="text-xs text-[#7A8E80] mt-1">Generated: {new Date(report.generated_at).toLocaleString()}</p>
            </div>
            <div className="text-right">
              <span className="text-[10px] font-bold px-2.5 py-1 rounded-full bg-[#D1FAE5] text-[#065F46] border border-[#A7F3D0]">
                Official Audit Copy
              </span>
            </div>
          </div>

          {/* Farm Soil Profile */}
          <div className="space-y-3">
            <h3 className="text-sm font-extrabold text-[#14231A] uppercase tracking-wider">
              1. Farm & Soil Laboratory Parameters
            </h3>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 p-4 rounded-2xl bg-[#F6F8F4] border border-[#DCE5DC] text-xs">
              <div>Land Area: <strong className="text-[#14231A]">{report.farm?.land_ha} ha</strong></div>
              <div>Season: <strong className="text-[#14231A] capitalize">{report.farm?.season}</strong></div>
              <div>Soil pH: <strong className="text-[#14231A]">{report.farm?.soil?.ph}</strong></div>
              <div>Salinity (EC): <strong className="text-[#14231A]">{report.farm?.soil?.ec} dS/m</strong></div>
              <div>Organic Carbon: <strong className="text-[#14231A]">{report.farm?.soil?.oc}%</strong></div>
              <div>Soil Texture: <strong className="text-[#14231A] capitalize">{report.farm?.soil?.texture}</strong></div>
              <div>Irrigation Water: <strong className="text-[#0D9488]">{report.farm?.water?.irrigation_m3?.toLocaleString()} m³</strong></div>
              <div>Budget: <strong className="text-[#D97706]">₹{report.farm?.budget_inr?.toLocaleString()}</strong></div>
            </div>
          </div>

          {/* Optimal Portfolio Allocation */}
          {report.optimization && (
            <div className="space-y-3">
              <h3 className="text-sm font-extrabold text-[#14231A] uppercase tracking-wider">
                2. Recommended Land Allocation (MILP Solution)
              </h3>
              <div className="border border-[#DCE5DC] rounded-2xl overflow-hidden">
                <table className="w-full text-left text-xs">
                  <thead className="bg-[#EEF3EC] text-[#14231A] font-bold">
                    <tr>
                      <th className="p-3">Selected Crop</th>
                      <th className="p-3">Category</th>
                      <th className="p-3">Area (ha)</th>
                      <th className="p-3">Share (%)</th>
                      <th className="p-3">Expected Net Profit</th>
                      <th className="p-3">Water Required</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[#DCE5DC]">
                    {report.optimization?.allocation?.map((a: any, i: number) => (
                      <tr key={i}>
                        <td className="p-3 font-bold text-[#14231A]">{a.crop_name}</td>
                        <td className="p-3 text-[#4A5F52]">{a.category}</td>
                        <td className="p-3 font-bold">{a.area_ha} ha</td>
                        <td className="p-3 text-[#047857] font-semibold">{((a.share || 0) * 100).toFixed(1)}%</td>
                        <td className="p-3 font-bold text-[#D97706]">₹{a.expected_return?.toLocaleString()}</td>
                        <td className="p-3 text-[#0D9488]">{a.water_m3?.toLocaleString()} m³</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Totals strip */}
              <div className="grid grid-cols-3 gap-3 p-3.5 rounded-xl bg-[#F6F8F4] border border-[#DCE5DC] text-xs">
                <div>Total Return: <strong className="text-[#D97706]">₹{report.optimization.totals?.net_return?.toLocaleString()}</strong></div>
                <div>Water Consumption: <strong className="text-[#0D9488]">{report.optimization.totals?.water_m3?.toLocaleString()} m³</strong></div>
                <div>Effective Crops (1/HHI): <strong className="text-[#047857]">{report.optimization.diversification?.effective_crops}</strong></div>
              </div>
            </div>
          )}

          {/* Top Rankings Table */}
          {report.ranking && (
            <div className="space-y-3">
              <h3 className="text-sm font-extrabold text-[#14231A] uppercase tracking-wider">
                3. TOPSIS Multi-Criteria Alternatives Ranking
              </h3>
              <div className="border border-[#DCE5DC] rounded-2xl overflow-hidden">
                <table className="w-full text-left text-xs">
                  <thead className="bg-[#EEF3EC] text-[#14231A] font-bold">
                    <tr>
                      <th className="p-2.5">Rank</th>
                      <th className="p-2.5">Crop</th>
                      <th className="p-2.5">Closeness ($C_i$)</th>
                      <th className="p-2.5">Soil Score</th>
                      <th className="p-2.5">Net Profit/ha</th>
                      <th className="p-2.5">Water</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[#DCE5DC]">
                    {report.ranking?.results?.slice(0, 5).map((r: any) => (
                      <tr key={r.crop_id}>
                        <td className="p-2.5 font-bold">#{r.rank}</td>
                        <td className="p-2.5 font-bold text-[#14231A]">{r.crop_name}</td>
                        <td className="p-2.5 text-[#047857] font-semibold">{(r.closeness * 100).toFixed(1)}%</td>
                        <td className="p-2.5">{r.criteria_values?.soil}</td>
                        <td className="p-2.5 text-[#D97706] font-bold">₹{r.criteria_values?.return?.toLocaleString()}</td>
                        <td className="p-2.5 text-[#0D9488]">{r.criteria_values?.water} mm</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Disclaimer */}
          <div className="pt-6 border-t border-[#DCE5DC] text-xs text-[#7A8E80] leading-relaxed">
            <strong>Disclaimer:</strong> {report.disclaimer} All seed agronomic data is illustrative and grounded in standard state agricultural university benchmarks.
          </div>
        </div>
      ) : (
        <div className="bg-white rounded-3xl border border-[#DCE5DC] p-12 text-center shadow-card">
          <FileText className="w-12 h-12 text-[#047857] mx-auto mb-3" />
          <h3 className="text-base font-bold text-[#14231A]">No Report Compiled Yet</h3>
          <p className="text-xs text-[#4A5F52] mt-1 mb-4">Click "Generate New Report" to compile findings.</p>
        </div>
      )}
    </div>
  );
};
