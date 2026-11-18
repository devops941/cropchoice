import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { authApi } from '../api/client';
import { Sprout, Eye, EyeOff, ShieldCheck, CheckCircle2, ArrowRight, Sparkles } from 'lucide-react';

export const LoginPage: React.FC = () => {
  const [email, setEmail] = useState('planner@cropchoice.local');
  const [password, setPassword] = useState('Planner@2026!');
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const res = await authApi.login({ email, password });
      login(res.access_token, res.user);
      navigate('/app');
    } catch (err: any) {
      setError(err.message || 'Login failed. Please verify credentials.');
    } finally {
      setLoading(false);
    }
  };

  const fillCredentials = (userEmail: string, userPass: string) => {
    setEmail(userEmail);
    setPassword(userPass);
    setError(null);
  };

  return (
    <div className="min-h-screen flex flex-col md:flex-row bg-[#F6F8F4]">
      {/* Left Brand Panel (Split Layout 12.4) */}
      <div className="md:w-1/2 bg-gradient-to-br from-[#ECF6EF] via-[#F1F7F2] to-[#F6F8F4] border-b md:border-b-0 md:border-r border-[#DCE5DC] p-8 lg:p-16 flex flex-col justify-between">
        <div>
          <Link to="/" className="inline-flex items-center gap-3 group">
            <div className="w-12 h-12 rounded-2xl bg-[#047857] flex items-center justify-center text-white shadow-lg shadow-[#047857]/20 group-hover:scale-105 transition-transform">
              <Sprout className="w-6 h-6" />
            </div>
            <div>
              <span className="text-xl font-extrabold text-[#14231A] tracking-tight">CropChoice</span>
              <span className="block text-xs font-semibold text-[#047857]">Strategic Agriculture Engine</span>
            </div>
          </Link>

          <div className="mt-16 lg:mt-24 max-w-md">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white border border-[#DCE5DC] text-[#047857] text-xs font-bold mb-4 shadow-sm">
              <Sparkles className="w-3.5 h-3.5" />
              2026 Analytical Optimization
            </div>
            <h1 className="text-3xl lg:text-4xl font-extrabold text-[#14231A] tracking-tight leading-tight">
              Choose the right crops. <br />
              <span className="text-[#047857]">Defend the decision.</span>
            </h1>
            <p className="mt-4 text-sm text-[#4A5F52] leading-relaxed">
              Transparent multi-criteria ranking and linear programming for farm land allocation under water, soil, and price uncertainty.
            </p>

            <div className="mt-8 space-y-3.5">
              <div className="flex items-start gap-3">
                <CheckCircle2 className="w-5 h-5 text-[#047857] shrink-0 mt-0.5" />
                <span className="text-xs font-medium text-[#14231A]">
                  <strong>FAO Soil & Water Scoring</strong> — Trapezoidal suitability combined with real irrigation balance.
                </span>
              </div>
              <div className="flex items-start gap-3">
                <CheckCircle2 className="w-5 h-5 text-[#047857] shrink-0 mt-0.5" />
                <span className="text-xs font-medium text-[#14231A]">
                  <strong>AHP & TOPSIS Ranking</strong> — Consistent weights and geometric closeness with WSM cross-checks.
                </span>
              </div>
              <div className="flex items-start gap-3">
                <CheckCircle2 className="w-5 h-5 text-[#047857] shrink-0 mt-0.5" />
                <span className="text-xs font-medium text-[#14231A]">
                  <strong>PuLP / SciPy Optimization</strong> — Diversification enforcement via HHI, Shannon entropy, and Monte Carlo risk.
                </span>
              </div>
            </div>
          </div>
        </div>

        <div className="mt-12 text-xs text-[#7A8E80]">
          © 2026 CropChoice · Connected to MongoDB Atlas
        </div>
      </div>

      {/* Right Form Card */}
      <div className="md:w-1/2 flex items-center justify-center p-6 lg:p-12">
        <div className="w-full max-w-md bg-white rounded-3xl border border-[#DCE5DC] p-8 shadow-card">
          <div className="mb-6">
            <h2 className="text-2xl font-bold text-[#14231A]">Sign in to your account</h2>
            <p className="text-xs text-[#4A5F52] mt-1">Access your farm profiles, rankings, and portfolio runs.</p>
          </div>

          {/* Quick Demo Fill Buttons */}
          <div className="mb-6 p-3 rounded-2xl bg-[#F6F8F4] border border-[#DCE5DC]">
            <div className="text-[11px] font-bold uppercase tracking-wider text-[#7A8E80] mb-2 flex items-center justify-between">
              <span>Quick Demo Sign-In</span>
              <span className="text-[10px] text-[#047857] font-semibold">1-Click Fill</span>
            </div>
            <div className="grid grid-cols-2 gap-2">
              <button
                type="button"
                onClick={() => fillCredentials('planner@cropchoice.local', 'Planner@2026!')}
                className="py-1.5 px-3 rounded-xl bg-white border border-[#DCE5DC] hover:border-[#047857] text-[11px] font-bold text-[#14231A] text-left transition-colors flex items-center justify-between"
              >
                <span>Planner</span>
                <span className="text-[10px] text-[#7A8E80]">Demo</span>
              </button>
              <button
                type="button"
                onClick={() => fillCredentials('admin@cropchoice.local', 'Admin@CropChoice2026!')}
                className="py-1.5 px-3 rounded-xl bg-white border border-[#DCE5DC] hover:border-[#D97706] text-[11px] font-bold text-[#14231A] text-left transition-colors flex items-center justify-between"
              >
                <span>Admin</span>
                <span className="text-[10px] text-[#D97706] flex items-center gap-0.5"><ShieldCheck className="w-3 h-3" /> Full</span>
              </button>
            </div>
          </div>

          {error && (
            <div className="mb-5 p-3 rounded-xl bg-[#FFE4E6] border border-[#FECDD3] text-xs font-semibold text-[#BE123C]">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-bold text-[#14231A] mb-1.5">Email address</label>
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="planner@cropchoice.local"
                className="w-full px-3.5 py-2.5 rounded-xl border border-[#DCE5DC] focus:border-[#047857] focus:ring-2 focus:ring-[#047857]/20 text-sm text-[#14231A] placeholder-[#7A8E80] bg-[#F6F8F4] transition-all outline-none"
              />
            </div>

            <div>
              <label className="block text-xs font-bold text-[#14231A] mb-1.5">Password</label>
              <div className="relative">
                <input
                  type={showPassword ? 'text' : 'password'}
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••••••"
                  className="w-full px-3.5 py-2.5 pr-10 rounded-xl border border-[#DCE5DC] focus:border-[#047857] focus:ring-2 focus:ring-[#047857]/20 text-sm text-[#14231A] placeholder-[#7A8E80] bg-[#F6F8F4] transition-all outline-none"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-3 text-[#7A8E80] hover:text-[#14231A]"
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            <div className="flex items-center justify-between text-xs pt-1">
              <label className="flex items-center gap-2 cursor-pointer text-[#4A5F52]">
                <input
                  type="checkbox"
                  checked={rememberMe}
                  onChange={(e) => setRememberMe(e.target.checked)}
                  className="w-4 h-4 text-[#047857] rounded border-[#DCE5DC] focus:ring-[#047857]"
                />
                Remember me
              </label>
              <Link to="/about" className="font-semibold text-[#047857] hover:underline">
                Need help?
              </Link>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full mt-2 py-3 px-4 rounded-xl font-bold text-sm text-white bg-[#047857] hover:bg-[#065F46] focus:ring-4 focus:ring-[#047857]/20 transition-all shadow-md shadow-[#047857]/20 flex items-center justify-center gap-2 disabled:opacity-50"
            >
              {loading ? (
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
              ) : (
                <>
                  Sign In to Dashboard
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </form>

          <div className="mt-6 text-center text-xs text-[#4A5F52]">
            Don't have an account?{' '}
            <Link to="/register" className="font-bold text-[#047857] hover:underline">
              Create Planner Account
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};
