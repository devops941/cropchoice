import React from 'react';
import { BookOpen, ShieldAlert } from 'lucide-react';

export const AboutPage: React.FC = () => {
  return (
    <div className="space-y-8 max-w-4xl mx-auto pb-12">
      {/* Header */}
      <div className="bg-white rounded-3xl border border-[#DCE5DC] p-8 shadow-card">
        <div className="flex items-center gap-2 mb-2">
          <BookOpen className="w-5 h-5 text-[#047857]" />
          <span className="text-xs font-bold uppercase tracking-wider text-[#047857]">
            Mathematical Specifications & Theoretical Framework
          </span>
        </div>
        <h1 className="text-3xl font-extrabold text-[#14231A] tracking-tight">
          CropChoice Methodology & Formulation
        </h1>
        <p className="text-xs text-[#4A5F52] mt-2 leading-relaxed">
          CropChoice replaces arbitrary intuition with rigorous multi-criteria decision analysis (MCDA), 
          linear programming, and stochastic simulation. Every recommendation can be traced directly to explicit equations.
        </p>
      </div>

      {/* 1. Soil Suitability */}
      <div className="bg-white rounded-3xl border border-[#DCE5DC] p-8 shadow-card space-y-4">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-xl bg-[#D1FAE5] text-[#047857] flex items-center justify-center font-bold text-xs">
            01
          </div>
          <h2 className="text-lg font-extrabold text-[#14231A]">
            1. FAO-Style Trapezoidal Soil Suitability Membership
          </h2>
        </div>
        <p className="text-xs text-[#4A5F52] leading-relaxed">
          For each chemical and physical soil property, membership score evaluates 
          whether the farm's laboratory soil test value falls within the crop's physiological boundaries [abs_min, opt_min, opt_max, abs_max]:
        </p>
        <div className="p-4 rounded-2xl bg-[#F6F8F4] border border-[#DCE5DC] font-mono text-xs text-[#14231A] overflow-x-auto whitespace-pre">
{`μ(x) = 
  0,                                         if x <= abs_min or x >= abs_max
  (x - abs_min) / (opt_min - abs_min),       if abs_min < x < opt_min
  1,                                         if opt_min <= x <= opt_max
  (abs_max - x) / (abs_max - opt_max),       if opt_max < x < abs_max`}
        </div>
        <p className="text-xs text-[#4A5F52]">
          Individual parameter scores are synthesized via geometric mean. Crops with overall soil score below 0.30 are flagged for exclusion.
        </p>
      </div>

      {/* 2. Saaty AHP */}
      <div className="bg-white rounded-3xl border border-[#DCE5DC] p-8 shadow-card space-y-4">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-xl bg-[#FEF3C7] text-[#B45309] flex items-center justify-center font-bold text-xs">
            02
          </div>
          <h2 className="text-lg font-extrabold text-[#14231A]">
            2. Analytic Hierarchy Process (AHP) Weighting & Consistency
          </h2>
        </div>
        <p className="text-xs text-[#4A5F52] leading-relaxed">
          Pairwise evaluations on the Saaty 1–9 fundamental scale form a reciprocal comparison matrix A where a_ji = 1/a_ij and a_ii = 1.
          Weights correspond to the normalized principal eigenvector w:
        </p>
        <div className="p-4 rounded-2xl bg-[#F6F8F4] border border-[#DCE5DC] font-mono text-xs text-[#14231A]">
          A · w = λ_max · w, &nbsp;&nbsp; with ∑ w_i = 1
        </div>
        <p className="text-xs text-[#4A5F52]">
          Matrix consistency is monitored via the Consistency Ratio (CR): CI = (λ_max - n) / (n - 1), and CR = CI / RI_n.
          Matrices with CR ≤ 0.10 are certified as mathematically consistent.
        </p>
      </div>

      {/* 3. TOPSIS */}
      <div className="bg-white rounded-3xl border border-[#DCE5DC] p-8 shadow-card space-y-4">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-xl bg-[#CCFBF1] text-[#0F766E] flex items-center justify-center font-bold text-xs">
            03
          </div>
          <h2 className="text-lg font-extrabold text-[#14231A]">
            3. TOPSIS Closeness Coefficient Formulation
          </h2>
        </div>
        <p className="text-xs text-[#4A5F52] leading-relaxed">
          TOPSIS identifies alternatives that minimize geometric Euclidean distance to the positive ideal solution (A+) 
          while maximizing distance from the negative ideal worst (A-):
        </p>
        <div className="p-4 rounded-2xl bg-[#F6F8F4] border border-[#DCE5DC] font-mono text-xs text-[#14231A] space-y-1">
          <div>r_ij = x_ij / √(∑ x_kj²), &nbsp; v_ij = w_j · r_ij</div>
          <div>S_i+ = √(∑ (v_ij - A_j+)²), &nbsp; S_i- = √(∑ (v_ij - A_j-)²)</div>
          <div className="font-bold text-[#047857]">C_i = S_i- / (S_i+ + S_i-)</div>
        </div>
      </div>

      {/* 4. Portfolio Optimization */}
      <div className="bg-white rounded-3xl border border-[#DCE5DC] p-8 shadow-card space-y-4">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-xl bg-[#F6E7DA] text-[#9A5B2F] flex items-center justify-center font-bold text-xs">
            04
          </div>
          <h2 className="text-lg font-extrabold text-[#14231A]">
            4. Mixed-Integer Linear Programming (MILP) Land Allocation
          </h2>
        </div>
        <p className="text-xs text-[#4A5F52] leading-relaxed">
          Continuous variables a_c represent allocated land hectares, and binary indicators y_c enforce minimum and maximum crop counts:
        </p>
        <div className="p-4 rounded-2xl bg-[#F6F8F4] border border-[#DCE5DC] font-mono text-xs text-[#14231A] space-y-1">
          <div>max ∑ a_c · R_c &nbsp; (or max ∑ a_c · C_c · 100,000)</div>
          <div>subject to:</div>
          <div>  ∑ a_c = Land_total</div>
          <div>  ∑ a_c · Water_c &lt;= Water_available</div>
          <div>  ∑ a_c · Cost_c &lt;= Budget_total</div>
          <div>  a_c &lt;= (Land_total · s_max) · y_c</div>
          <div>  a_c &gt;= min_area · y_c</div>
          <div>  ∑ y_c &gt;= min_crops</div>
        </div>
        <p className="text-xs text-[#4A5F52]">
          Diversification is quantified by the Herfindahl-Hirschman Index: HHI = ∑ s_c², effective crop count N_eff = 1 / HHI, 
          and Shannon entropy H = -∑ s_c ln(s_c).
        </p>
      </div>

      {/* Disclaimer Card */}
      <div className="p-6 rounded-3xl bg-[#FEF3C7] border border-[#FDE68A] text-xs text-[#78350F] flex items-start gap-4">
        <ShieldAlert className="w-6 h-6 shrink-0 text-[#D97706] mt-0.5" />
        <div className="space-y-1">
          <div className="font-extrabold text-[#B45309]">Advisory Disclaimer & Academic Integrity</div>
          <p className="leading-relaxed">
            CropChoice is designed as an analytical decision-support framework. Real agricultural yields and financial outcomes 
            are subject to unforeseen micro-climate conditions, pests, and market price shocks. Farm planning teams must 
            verify crop package recommendations with local state agriculture departments and extension officers.
          </p>
        </div>
      </div>
    </div>
  );
};
