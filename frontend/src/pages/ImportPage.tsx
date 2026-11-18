import React, { useState } from 'react';
import { importExportApi } from '../api/client';
import { 
  UploadCloud, 
  FileSpreadsheet, 
  Download, 
  CheckCircle2, 
  AlertTriangle, 
  ArrowRight,
  Sparkles,
  Database,
  FileCheck
} from 'lucide-react';

export const ImportPage: React.FC = () => {
  const [kind, setKind] = useState<'crops' | 'prices' | 'economics' | 'farms'>('farms');
  const [file, setFile] = useState<File | null>(null);
  const [autoCommit, setAutoCommit] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setResult(null);
      setError(null);
    }
  };

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) {
      setError('Please select an Excel or CSV file first.');
      return;
    }

    setUploading(true);
    setError(null);

    try {
      const res = await importExportApi.upload(kind, file, autoCommit);
      setResult(res);
    } catch (err: any) {
      setError(err.message || 'File upload and parsing failed.');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      {/* Header */}
      <div className="bg-white rounded-3xl border border-[#DCE5DC] p-6 shadow-card flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <UploadCloud className="w-5 h-5 text-[#047857]" />
            <span className="text-xs font-bold uppercase tracking-wider text-[#047857]">
              Data Ingestion & Batch Loading
            </span>
          </div>
          <h1 className="text-2xl font-extrabold text-[#14231A]">Upload Agricultural Data</h1>
          <p className="text-xs text-[#4A5F52] mt-1">
            Upload CSV/Excel files for soil test records, crop library updates, mandi price series, or economics data.
          </p>
        </div>

        {/* Download Sample Buttons */}
        <div className="flex items-center gap-2">
          <a
            href={importExportApi.getSampleUrl(kind, 'xlsx')}
            download={`${kind}_sample.xlsx`}
            className="px-3.5 py-2.5 rounded-xl bg-[#047857] hover:bg-[#065F46] text-white text-xs font-bold flex items-center gap-2 shadow-sm transition-all"
          >
            <Download className="w-4 h-4" />
            Excel Template (.xlsx)
          </a>
          <a
            href={importExportApi.getSampleUrl(kind, 'csv')}
            download={`${kind}_sample.csv`}
            className="px-3.5 py-2.5 rounded-xl bg-[#EEF3EC] hover:bg-[#DCE5DC] text-[#14231A] text-xs font-bold flex items-center gap-2 border border-[#DCE5DC] transition-all"
          >
            <Download className="w-4 h-4 text-[#047857]" />
            CSV (.csv)
          </a>
        </div>
      </div>

      {/* Dataset Selection Tabs */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {[
          { id: 'farms', label: 'Soil & Farm Records', desc: 'pH, EC, land, water, budget' },
          { id: 'crops', label: 'Crop Library', desc: 'Requirements, duration, yield' },
          { id: 'prices', label: 'Mandi Price Series', desc: 'Monthly modal prices' },
          { id: 'economics', label: 'Crop Economics', desc: 'CACP costs, yields, MSP' },
        ].map((tab) => {
          const isSelected = kind === tab.id;
          return (
            <button
              key={tab.id}
              type="button"
              onClick={() => {
                setKind(tab.id as any);
                setFile(null);
                setResult(null);
                setError(null);
              }}
              className={`p-4 rounded-2xl border text-left transition-all ${
                isSelected
                  ? 'bg-white border-[#047857] shadow-card ring-2 ring-[#047857]/15'
                  : 'bg-[#F6F8F4] border-[#DCE5DC] hover:border-[#7A8E80]'
              }`}
            >
              <div className="flex items-center justify-between mb-1">
                <span className={`text-xs font-black ${isSelected ? 'text-[#047857]' : 'text-[#14231A]'}`}>
                  {tab.label}
                </span>
                {isSelected && <span className="w-2 h-2 rounded-full bg-[#047857]" />}
              </div>
              <p className="text-[11px] text-[#7A8E80]">{tab.desc}</p>
            </button>
          );
        })}
      </div>

      {/* Upload Box */}
      <div className="bg-white rounded-3xl border border-[#DCE5DC] p-8 shadow-card">
        <form onSubmit={handleUpload} className="space-y-6">
          <div className="border-2 border-dashed border-[#DCE5DC] hover:border-[#047857] rounded-3xl p-8 text-center transition-colors bg-[#F6F8F4]/50">
            <FileSpreadsheet className="w-12 h-12 text-[#047857] mx-auto mb-3 opacity-80" />
            <h3 className="font-extrabold text-sm text-[#14231A]">
              {file ? file.name : `Select or drag & drop ${kind.toUpperCase()} Excel/CSV file`}
            </h3>
            <p className="text-xs text-[#7A8E80] mt-1 mb-4">
              Supported file formats: .xlsx, .xls, .csv, .txt (with headers)
            </p>
            <input
              type="file"
              id="csv-file-input"
              accept=".xlsx,.xls,.csv,.txt"
              onChange={handleFileChange}
              className="hidden"
            />
            <label
              htmlFor="csv-file-input"
              className="px-5 py-2.5 rounded-xl bg-[#047857] hover:bg-[#065F46] text-white text-xs font-bold cursor-pointer inline-flex items-center gap-2 shadow-md shadow-[#047857]/20 transition-all"
            >
              Browse Computer
            </label>
          </div>

          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pt-2">
            <label className="flex items-center gap-2 cursor-pointer text-xs font-semibold text-[#14231A]">
              <input
                type="checkbox"
                checked={autoCommit}
                onChange={(e) => setAutoCommit(e.target.checked)}
                className="w-4 h-4 text-[#047857] rounded border-[#DCE5DC] focus:ring-[#047857]"
              />
              Directly save validated rows into MongoDB Atlas
            </label>

            <button
              type="submit"
              disabled={!file || uploading}
              className="px-6 py-3 rounded-xl bg-[#047857] hover:bg-[#065F46] disabled:opacity-40 text-white text-xs font-bold flex items-center justify-center gap-2 shadow-md shadow-[#047857]/20 transition-all"
            >
              {uploading ? (
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
              ) : (
                <>
                  <UploadCloud className="w-4 h-4" />
                  Validate & Upload Dataset
                </>
              )}
            </button>
          </div>
        </form>

        {error && (
          <div className="mt-6 p-4 rounded-2xl bg-[#FFE4E6] border border-[#FECDD3] text-xs font-bold text-[#BE123C] flex items-center gap-3">
            <AlertTriangle className="w-5 h-5 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {/* Upload Results & Preview */}
        {result && (
          <div className="mt-8 pt-8 border-t border-[#DCE5DC] space-y-6">
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
              <div className="p-4 rounded-2xl bg-[#F6F8F4] border border-[#DCE5DC]">
                <div className="text-[11px] font-bold text-[#7A8E80] uppercase">Total Rows</div>
                <div className="text-xl font-black text-[#14231A] mt-1">{result.total_rows}</div>
              </div>
              <div className="p-4 rounded-2xl bg-[#D1FAE5] border border-[#A7F3D0]">
                <div className="text-[11px] font-bold text-[#065F46] uppercase">Valid Records</div>
                <div className="text-xl font-black text-[#047857] mt-1">{result.valid_rows_count}</div>
              </div>
              <div className="p-4 rounded-2xl bg-[#FFE4E6] border border-[#FECDD3]">
                <div className="text-[11px] font-bold text-[#BE123C] uppercase">Errors</div>
                <div className="text-xl font-black text-[#BE123C] mt-1">{result.error_count}</div>
              </div>
              <div className="p-4 rounded-2xl bg-[#ECF6EF] border border-[#DCE5DC]">
                <div className="text-[11px] font-bold text-[#047857] uppercase">MongoDB Saved</div>
                <div className="text-xl font-black text-[#047857] mt-1">
                  {result.committed_count || result.valid_rows_count}
                </div>
              </div>
            </div>

            {/* Error table if any */}
            {result.errors && result.errors.length > 0 && (
              <div>
                <h4 className="text-xs font-bold text-[#BE123C] uppercase tracking-wider mb-2">
                  Validation Issues ({result.errors.length})
                </h4>
                <div className="border border-[#FECDD3] rounded-2xl overflow-hidden bg-[#FFF1F2]">
                  <table className="w-full text-left text-xs">
                    <thead className="bg-[#FFE4E6] border-b border-[#FECDD3] text-[#BE123C] font-bold">
                      <tr>
                        <th className="p-3">Row</th>
                        <th className="p-3">Field</th>
                        <th className="p-3">Problem</th>
                        <th className="p-3">Recommended Fix</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-[#FECDD3] text-[#9F1239]">
                      {result.errors.map((err: any, i: number) => (
                        <tr key={i}>
                          <td className="p-3 font-bold">{err.row}</td>
                          <td className="p-3 font-mono text-[11px]">{err.column}</td>
                          <td className="p-3">{err.message}</td>
                          <td className="p-3 font-semibold">{err.suggestion}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {/* Preview table */}
            {result.preview_data && result.preview_data.length > 0 && (
              <div>
                <h4 className="text-xs font-bold text-[#047857] uppercase tracking-wider mb-2">
                  Data Preview (First 5 Rows)
                </h4>
                <div className="border border-[#DCE5DC] rounded-2xl overflow-x-auto bg-[#F6F8F4]">
                  <table className="w-full text-left text-xs">
                    <thead className="bg-[#EEF3EC] border-b border-[#DCE5DC] text-[#14231A] font-bold">
                      <tr>
                        {Object.keys(result.preview_data[0] || {}).map((k) => (
                          <th key={k} className="p-3 capitalize">{k.replace('_', ' ')}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-[#DCE5DC]">
                      {result.preview_data.slice(0, 5).map((row: any, i: number) => (
                        <tr key={i} className="hover:bg-white transition-colors">
                          {Object.values(row).map((val: any, j: number) => (
                            <td key={j} className="p-3 text-[#4A5F52]">
                              {typeof val === 'object' ? JSON.stringify(val) : String(val)}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
