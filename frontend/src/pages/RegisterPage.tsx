import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { authApi } from '../api/client';
import { Sprout, ArrowRight } from 'lucide-react';

export const RegisterPage: React.FC = () => {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (password !== confirmPassword) {
      setError('Passwords do not match.');
      return;
    }
    setError(null);
    setLoading(true);

    try {
      const res = await authApi.register({ name, email, password });
      login(res.access_token, res.user);
      navigate('/app');
    } catch (err: any) {
      setError(err.message || 'Registration failed.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-6 bg-[#F6F8F4]">
      <div className="w-full max-w-md bg-white rounded-3xl border border-[#DCE5DC] p-8 shadow-card">
        <div className="flex items-center gap-2 mb-6">
          <div className="w-8 h-8 rounded-xl bg-[#047857] flex items-center justify-center text-white">
            <Sprout className="w-4 h-4" />
          </div>
          <span className="font-extrabold text-lg text-[#14231A]">CropChoice</span>
        </div>

        <h2 className="text-2xl font-bold text-[#14231A]">Create Planner Account</h2>
        <p className="text-xs text-[#4A5F52] mt-1 mb-6">Set up your agricultural decision workspace.</p>

        {error && (
          <div className="mb-4 p-3 rounded-xl bg-[#FFE4E6] border border-[#FECDD3] text-xs font-semibold text-[#BE123C]">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-bold text-[#14231A] mb-1.5">Full Name</label>
            <input
              type="text"
              required
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Dr. Anand Swaminathan"
              className="w-full px-3.5 py-2.5 rounded-xl border border-[#DCE5DC] focus:border-[#047857] focus:ring-2 focus:ring-[#047857]/20 text-sm text-[#14231A] bg-[#F6F8F4] outline-none"
            />
          </div>

          <div>
            <label className="block text-xs font-bold text-[#14231A] mb-1.5">Work Email</label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="anand@agri.tn.gov.in"
              className="w-full px-3.5 py-2.5 rounded-xl border border-[#DCE5DC] focus:border-[#047857] focus:ring-2 focus:ring-[#047857]/20 text-sm text-[#14231A] bg-[#F6F8F4] outline-none"
            />
          </div>

          <div>
            <label className="block text-xs font-bold text-[#14231A] mb-1.5">Password</label>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="At least 6 characters"
              className="w-full px-3.5 py-2.5 rounded-xl border border-[#DCE5DC] focus:border-[#047857] focus:ring-2 focus:ring-[#047857]/20 text-sm text-[#14231A] bg-[#F6F8F4] outline-none"
            />
          </div>

          <div>
            <label className="block text-xs font-bold text-[#14231A] mb-1.5">Confirm Password</label>
            <input
              type="password"
              required
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              placeholder="Repeat password"
              className="w-full px-3.5 py-2.5 rounded-xl border border-[#DCE5DC] focus:border-[#047857] focus:ring-2 focus:ring-[#047857]/20 text-sm text-[#14231A] bg-[#F6F8F4] outline-none"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full mt-2 py-3 px-4 rounded-xl font-bold text-sm text-white bg-[#047857] hover:bg-[#065F46] shadow-md shadow-[#047857]/20 transition-all flex items-center justify-center gap-2"
          >
            {loading ? 'Creating...' : 'Register as Planner'}
            <ArrowRight className="w-4 h-4" />
          </button>
        </form>

        <div className="mt-6 text-center text-xs text-[#4A5F52]">
          Already have an account?{' '}
          <Link to="/login" className="font-bold text-[#047857] hover:underline">
            Sign In
          </Link>
        </div>
      </div>
    </div>
  );
};
