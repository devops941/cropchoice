import React from 'react';
import { Link } from 'react-router-dom';
import { 
  Sprout, 
  ArrowRight, 
  Award, 
  PieChart, 
  Activity, 
  Layers, 
  ShieldCheck, 
  CheckCircle2, 
  Compass, 
  Database,
  BarChart3
} from 'lucide-react';

export const LandingPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-[#F6F8F4] text-[#14231A]">
      {/* Top Navigation */}
      <header className="border-b border-[#DCE5DC] bg-white/80 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-[#047857] to-[#059669] flex items-center justify-center text-white shadow-md shadow-[#047857]/20">
              <Sprout className="w-5 h-5" />
            </div>
            <div>
              <span className="font-extrabold text-lg text-[#14231A] tracking-tight">CropChoice</span>
              <span className="ml-2 text-[10px] font-bold uppercase px-2 py-0.5 rounded-full bg-[#D1FAE5] text-[#065F46] border border-[#A7F3D0]">
                2026 Edition
              </span>
            </div>
          </div>

          <div className="hidden md:flex items-center gap-8 text-xs font-semibold text-[#4A5F52]">
            <a href="#features" className="hover:text-[#047857] transition-colors">Capabilities</a>
            <a href="#methodology" className="hover:text-[#047857] transition-colors">Methodology</a>
            <Link to="/about" className="hover:text-[#047857] transition-colors">Documentation</Link>
          </div>

          <div className="flex items-center gap-3">
            <Link
              to="/login"
              className="px-4 py-2 text-xs font-bold text-[#047857] hover:bg-[#EEF3EC] rounded-xl transition-all"
            >
              Sign In
            </Link>
            <Link
              to="/login"
              className="px-4 py-2 text-xs font-bold text-white bg-[#047857] hover:bg-[#065F46] rounded-xl shadow-md shadow-[#047857]/20 transition-all flex items-center gap-1.5"
            >
              Launch Dashboard
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative overflow-hidden pt-16 pb-20 lg:pt-24 lg:pb-32">
        <div className="max-w-7xl mx-auto px-6 text-center">
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-[#D1FAE5] border border-[#A7F3D0] text-[#065F46] text-xs font-bold mb-6">
            <span className="w-2 h-2 rounded-full bg-[#10B981] animate-pulse" />
            Next-Gen Agricultural Decision Support System
          </div>

          <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight text-[#14231A] max-w-4xl mx-auto leading-[1.15]">
            Choose the Right Crops. <br />
            <span className="bg-gradient-to-r from-[#047857] via-[#059669] to-[#D97706] bg-clip-text text-transparent">
              Defend Every Acre with Math.
            </span>
          </h1>

          <p className="mt-6 text-base sm:text-lg text-[#4A5F52] max-w-2xl mx-auto leading-relaxed">
            Multi-criteria crop ranking with <strong>TOPSIS & AHP</strong>, coupled with rigorous 
            <strong> MILP portfolio land allocation</strong> and <strong>Monte Carlo risk simulation</strong>.
            Powered by real MongoDB data, zero guesswork.
          </p>

          <div className="mt-8 flex flex-wrap justify-center items-center gap-4">
            <Link
              to="/login"
              className="px-6 py-3.5 text-sm font-bold text-white bg-[#047857] hover:bg-[#065F46] rounded-xl shadow-lg shadow-[#047857]/25 transition-all flex items-center gap-2"
            >
              Start Crop Planning
              <ArrowRight className="w-4 h-4" />
            </Link>
            <Link
              to="/about"
              className="px-6 py-3.5 text-sm font-bold text-[#14231A] bg-white border border-[#DCE5DC] hover:bg-[#EEF3EC] rounded-xl transition-all flex items-center gap-2 shadow-sm"
            >
              Explore Formulas & Docs
            </Link>
          </div>

          {/* Key Value Stats */}
          <div className="mt-16 grid grid-cols-2 sm:grid-cols-4 gap-4 max-w-4xl mx-auto">
            <div className="p-4 rounded-2xl bg-white border border-[#DCE5DC] shadow-card">
              <div className="text-2xl font-black text-[#047857]">16+</div>
              <div className="text-xs font-semibold text-[#7A8E80] mt-1">Crop Genomes</div>
            </div>
            <div className="p-4 rounded-2xl bg-white border border-[#DCE5DC] shadow-card">
              <div className="text-2xl font-black text-[#D97706]">10 Years</div>
              <div className="text-xs font-semibold text-[#7A8E80] mt-1">Mandi Price Series</div>
            </div>
            <div className="p-4 rounded-2xl bg-white border border-[#DCE5DC] shadow-card">
              <div className="text-2xl font-black text-[#0D9488]">TOPSIS + AHP</div>
              <div className="text-xs font-semibold text-[#7A8E80] mt-1">MCDM Engine</div>
            </div>
            <div className="p-4 rounded-2xl bg-white border border-[#DCE5DC] shadow-card">
              <div className="text-2xl font-black text-[#C2763F]">5,000 Runs</div>
              <div className="text-xs font-semibold text-[#7A8E80] mt-1">Monte Carlo VaR</div>
            </div>
          </div>
        </div>
      </section>

      {/* 4-Step Architecture */}
      <section id="features" className="py-20 bg-white border-y border-[#DCE5DC]">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center max-w-2xl mx-auto mb-16">
            <h2 className="text-xs font-bold uppercase tracking-wider text-[#047857]">System Workflow</h2>
            <p className="mt-2 text-3xl font-extrabold text-[#14231A]">From Soil Test to Optimal Acreage</p>
            <p className="mt-3 text-sm text-[#4A5F52]">
              A continuous, transparent analytical pipeline designed for farmers, agronomists, and planning officers.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="p-6 rounded-2xl bg-[#F6F8F4] border border-[#DCE5DC] relative">
              <div className="w-10 h-10 rounded-xl bg-[#D1FAE5] text-[#047857] flex items-center justify-center font-bold text-sm mb-4">
                01
              </div>
              <h3 className="font-bold text-base text-[#14231A]">Farm & Soil Profiling</h3>
              <p className="text-xs text-[#4A5F52] mt-2 leading-relaxed">
                Enter or upload soil pH, EC, organic carbon, texture, and seasonal water availability.
              </p>
            </div>

            <div className="p-6 rounded-2xl bg-[#F6F8F4] border border-[#DCE5DC] relative">
              <div className="w-10 h-10 rounded-xl bg-[#FEF3C7] text-[#B45309] flex items-center justify-center font-bold text-sm mb-4">
                02
              </div>
              <h3 className="font-bold text-base text-[#14231A]">AHP Criteria Weighting</h3>
              <p className="text-xs text-[#4A5F52] mt-2 leading-relaxed">
                Derive consistent weights for water, soil, return, and risk using Saaty pairwise comparisons.
              </p>
            </div>

            <div className="p-6 rounded-2xl bg-[#F6F8F4] border border-[#DCE5DC] relative">
              <div className="w-10 h-10 rounded-xl bg-[#CCFBF1] text-[#0F766E] flex items-center justify-center font-bold text-sm mb-4">
                03
              </div>
              <h3 className="font-bold text-base text-[#14231A]">TOPSIS Ranking</h3>
              <p className="text-xs text-[#4A5F52] mt-2 leading-relaxed">
                Ranks all alternatives by geometric closeness to the positive ideal solution with plain explanations.
              </p>
            </div>

            <div className="p-6 rounded-2xl bg-[#F6F8F4] border border-[#DCE5DC] relative">
              <div className="w-10 h-10 rounded-xl bg-[#F6E7DA] text-[#9A5B2F] flex items-center justify-center font-bold text-sm mb-4">
                04
              </div>
              <h3 className="font-bold text-base text-[#14231A]">MILP Portfolio Optimization</h3>
              <p className="text-xs text-[#4A5F52] mt-2 leading-relaxed">
                Allocates land hectares under water, budget, and labour limits with enforced crop diversification.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 border-t border-[#DCE5DC] bg-[#F6F8F4] text-xs text-[#7A8E80]">
        <div className="max-w-7xl mx-auto px-6 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <Sprout className="w-4 h-4 text-[#047857]" />
            <span className="font-bold text-[#14231A]">CropChoice Decision Support System</span>
            <span>· 2026 Academic & Research Release</span>
          </div>
          <div>
            Illustrative demo data: verify with official state agricultural university sources.
          </div>
        </div>
      </footer>
    </div>
  );
};
