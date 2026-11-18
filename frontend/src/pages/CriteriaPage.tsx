import React, { useState, useEffect } from 'react';
import { criteriaApi } from '../api/client';
import { Sliders, CheckCircle2, AlertTriangle, Scale, Save, Sparkles } from 'lucide-react';

export const CriteriaPage: React.FC = () => {
  const [mode, setMode] = useState<'sliders' | 'ahp'>('sliders');
  const [weights, setWeights] = useState<any>({ water: 0.25, soil: 0.25, return: 0.25, variability: 0.25 });
  const [presets, setPresets] = useState<any[]>([]);

  // AHP 4x4 matrix
  // order: [water, soil, return, variability]
  const criteriaNames = ['water', 'soil', 'return', 'variability'];
  const [matrix, setMatrix] = useState<number[][]>([
    [1.0, 1.0, 1.0, 1.0],
    [1.0, 1.0, 1.0, 1.0],
    [1.0, 1.0, 1.0, 1.0],
    [1.0, 1.0, 1.0, 1.0],
  ]);
  const [ahpResult, setAhpResult] = useState<any>(null);

  useEffect(() => {
    criteriaApi.getPresets().then(setPresets).catch(console.error);
  }, []);

  const handleSliderChange = (key: string, val: number) => {
    const updated = { ...weights, [key]: val };
    const tot = Object.values(updated).reduce((a: any, b: any) => a + b, 0) as number;
    setWeights(updated);
  };

  const handleNormalize = () => {
    const tot = Object.values(weights).reduce((a: any, b: any) => a + b, 0) as number;
    if (tot > 0) {
      const norm: any = {};
      for (const k in weights) {
        norm[k] = parseFloat((weights[k] / tot).toFixed(3));
      }
      setWeights(norm);
    }
  };

  const handleMatrixCellChange = (i: number, j: number, val: number) => {
    const newM = matrix.map((row) => [...row]);
    newM[i][j] = val;
    newM[j][i] = 1.0 / val;
    setMatrix(newM);
  };

  const computeAhp = async () => {
    try {
      const res = await criteriaApi.calculateAhp({ matrix, criteria_names: criteriaNames });
      setAhpResult(res);
      setWeights(res.weights);
    } catch (err: any) {
      alert(err.message || 'AHP calculation failed');
    }
  };

  const totalSum = Object.values(weights).reduce((a: any, b: any) => a + b, 0) as number;

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      {/* Header */}
      <div className="bg-white rounded-3xl border border-[#DCE5DC] p-6 shadow-card flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Sliders className="w-5 h-5 text-[#047857]" />
            <span className="text-xs font-bold uppercase tracking-wider text-[#047857]">
              Decision Science Weighting
            </span>
          </div>
          <h1 className="text-2xl font-extrabold text-[#14231A]">Criteria & Weighting Methods</h1>
          <p className="text-xs text-[#4A5F52] mt-1">
            Choose direct sliders with live normalization, or use Saaty's Analytic Hierarchy Process (AHP) with mathematical consistency checks.
          </p>
        </div>

        {/* Mode Switcher */}
        <div className="flex items-center p-1 bg-[#F6F8F4] border border-[#DCE5DC] rounded-2xl">
          <button
            onClick={() => setMode('sliders')}
            className={`px-4 py-2 rounded-xl text-xs font-bold transition-all ${
              mode === 'sliders'
                ? 'bg-[#047857] text-white shadow-sm'
                : 'text-[#4A5F52] hover:text-[#14231A]'
            }`}
          >
            Direct Sliders
          </button>
          <button
            onClick={() => setMode('ahp')}
            className={`px-4 py-2 rounded-xl text-xs font-bold transition-all ${
              mode === 'ahp'
                ? 'bg-[#047857] text-white shadow-sm'
                : 'text-[#4A5F52] hover:text-[#14231A]'
            }`}
          >
            Saaty AHP Matrix
          </button>
        </div>
      </div>

      {mode === 'sliders' ? (
        /* Sliders Mode */
        <div className="bg-white rounded-3xl border border-[#DCE5DC] p-8 shadow-card space-y-6">
          {/* Presets */}
          <div>
            <div className="text-xs font-bold text-[#7A8E80] uppercase tracking-wider mb-2">Preset Profiles</div>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              {presets.map((p) => (
                <button
                  key={p.id}
                  onClick={() => setWeights(p.weights)}
                  className="p-3.5 rounded-2xl bg-[#F6F8F4] border border-[#DCE5DC] hover:border-[#047857] text-left transition-all"
                >
                  <div className="font-extrabold text-xs text-[#14231A]">{p.name}</div>
                  <div className="text-[11px] text-[#7A8E80] mt-1 line-clamp-2">{p.description}</div>
                </button>
              ))}
            </div>
          </div>

          {/* Sliders */}
          <div className="space-y-5 pt-4">
            <div>
              <div className="flex justify-between text-xs font-bold mb-1.5">
                <span className="text-[#14231A]">💧 Water Demand (Cost criterion)</span>
                <span className="text-[#0D9488] tabular-nums">{((weights.water || 0) * 100).toFixed(1)}%</span>
              </div>
              <input
                type="range"
                min="0"
                max="1"
                step="0.02"
                value={weights.water || 0}
                onChange={(e) => handleSliderChange('water', parseFloat(e.target.value))}
                className="w-full accent-[#0D9488]"
              />
            </div>

            <div>
              <div className="flex justify-between text-xs font-bold mb-1.5">
                <span className="text-[#14231A]">🌱 Soil Suitability (Benefit criterion)</span>
                <span className="text-[#047857] tabular-nums">{((weights.soil || 0) * 100).toFixed(1)}%</span>
              </div>
              <input
                type="range"
                min="0"
                max="1"
                step="0.02"
                value={weights.soil || 0}
                onChange={(e) => handleSliderChange('soil', parseFloat(e.target.value))}
                className="w-full accent-[#047857]"
              />
            </div>

            <div>
              <div className="flex justify-between text-xs font-bold mb-1.5">
                <span className="text-[#14231A]">💰 Expected Return (Benefit criterion)</span>
                <span className="text-[#D97706] tabular-nums">{((weights.return || 0) * 100).toFixed(1)}%</span>
              </div>
              <input
                type="range"
                min="0"
                max="1"
                step="0.02"
                value={weights.return || 0}
                onChange={(e) => handleSliderChange('return', parseFloat(e.target.value))}
                className="w-full accent-[#D97706]"
              />
            </div>

            <div>
              <div className="flex justify-between text-xs font-bold mb-1.5">
                <span className="text-[#14231A]">📉 Price Variability Risk (Cost criterion)</span>
                <span className="text-[#E11D48] tabular-nums">{((weights.variability || 0) * 100).toFixed(1)}%</span>
              </div>
              <input
                type="range"
                min="0"
                max="1"
                step="0.02"
                value={weights.variability || 0}
                onChange={(e) => handleSliderChange('variability', parseFloat(e.target.value))}
                className="w-full accent-[#E11D48]"
              />
            </div>
          </div>

          {/* Sum & Normalization bar */}
          <div className="pt-4 border-t border-[#DCE5DC] flex items-center justify-between">
            <div className="flex items-center gap-3">
              <span className="text-xs font-semibold text-[#4A5F52]">Weights Sum:</span>
              <span
                className={`text-sm font-black tabular-nums ${
                  Math.abs(totalSum - 1.0) < 0.02 ? 'text-[#047857]' : 'text-[#D97706]'
                }`}
              >
                {(totalSum * 100).toFixed(0)}%
              </span>
            </div>

            <button
              onClick={handleNormalize}
              className="px-4 py-2 rounded-xl bg-[#047857] hover:bg-[#065F46] text-white text-xs font-bold transition-all"
            >
              Auto-Normalize to 100%
            </button>
          </div>
        </div>
      ) : (
        /* AHP Pairwise Matrix Mode */
        <div className="bg-white rounded-3xl border border-[#DCE5DC] p-8 shadow-card space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-lg font-extrabold text-[#14231A]">Saaty 1-9 Pairwise Comparison Matrix</h2>
              <p className="text-xs text-[#4A5F52]">
                1 = Equal, 3 = Moderate, 5 = Strong, 7 = Very Strong, 9 = Extreme Importance. Reciprocals are automatic.
              </p>
            </div>
            <button
              onClick={computeAhp}
              className="px-5 py-2.5 rounded-xl bg-[#047857] hover:bg-[#065F46] text-white text-xs font-bold flex items-center gap-2 shadow-md shadow-[#047857]/20"
            >
              Compute Eigenvector Weights
            </button>
          </div>

          <div className="border border-[#DCE5DC] rounded-2xl overflow-x-auto">
            <table className="w-full text-center text-xs">
              <thead className="bg-[#EEF3EC] text-[#14231A] font-bold">
                <tr>
                  <th className="p-3 text-left">Criterion</th>
                  <th className="p-3">Water</th>
                  <th className="p-3">Soil</th>
                  <th className="p-3">Return</th>
                  <th className="p-3">Variability</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#DCE5DC]">
                {criteriaNames.map((rowName, i) => (
                  <tr key={rowName}>
                    <td className="p-3 font-bold text-left capitalize text-[#14231A] bg-[#F6F8F4]">{rowName}</td>
                    {criteriaNames.map((colName, j) => (
                      <td key={colName} className="p-3 font-mono">
                        {i === j ? (
                          <span className="font-bold text-[#7A8E80]">1.0</span>
                        ) : i < j ? (
                          <input
                            type="number"
                            min="0.11"
                            max="9"
                            step="0.5"
                            value={matrix[i][j]}
                            onChange={(e) => handleMatrixCellChange(i, j, parseFloat(e.target.value) || 1.0)}
                            className="w-16 p-1 text-center font-bold border border-[#DCE5DC] rounded-lg bg-white"
                          />
                        ) : (
                          <span className="text-[#4A5F52] font-semibold">{matrix[i][j].toFixed(2)}</span>
                        )}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {ahpResult && (
            <div className="mt-6 p-5 rounded-2xl bg-[#F6F8F4] border border-[#DCE5DC] space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-[#14231A]">Consistency Ratio (CR):</span>
                <span
                  className={`text-xs font-black px-2.5 py-1 rounded-full border ${
                    ahpResult.is_consistent
                      ? 'bg-[#D1FAE5] text-[#065F46] border-[#A7F3D0]'
                      : 'bg-[#FFE4E6] text-[#BE123C] border-[#FECDD3]'
                  }`}
                >
                  CR = {ahpResult.consistency_ratio} ({ahpResult.is_consistent ? 'Consistent < 0.10' : 'Inconsistent > 0.10'})
                </span>
              </div>

              <div className="grid grid-cols-4 gap-3">
                {Object.entries(ahpResult.weights).map(([k, v]: any) => (
                  <div key={k} className="p-3 rounded-xl bg-white border border-[#DCE5DC] text-center">
                    <div className="text-[11px] font-bold text-[#7A8E80] uppercase">{k}</div>
                    <div className="text-lg font-black text-[#047857] mt-1 tabular-nums">
                      {(v * 100).toFixed(1)}%
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
