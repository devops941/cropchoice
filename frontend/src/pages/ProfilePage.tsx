import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { authApi } from '../api/client';
import { User, KeyRound, Shield, CheckCircle2 } from 'lucide-react';

export const ProfilePage: React.FC = () => {
  const { user, updateUser } = useAuth();
  const [name, setName] = useState(user?.name || '');
  const [areaUnit, setAreaUnit] = useState(user?.preferences?.area_unit || 'ha');
  const [currency, setCurrency] = useState(user?.preferences?.currency || 'INR');
  const [region, setRegion] = useState(user?.preferences?.region || 'South India');
  const [savingPref, setSavingPref] = useState(false);
  const [prefMsg, setPrefMsg] = useState<string | null>(null);

  // Password change state
  const [oldPassword, setOldPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [pwdMsg, setPwdMsg] = useState<string | null>(null);
  const [pwdErr, setPwdErr] = useState<string | null>(null);
  const [changingPwd, setChangingPwd] = useState(false);

  const handleSavePreferences = async (e: React.FormEvent) => {
    e.preventDefault();
    setSavingPref(true);
    setPrefMsg(null);
    try {
      const updated = await authApi.updateMe({
        name,
        preferences: { area_unit: areaUnit, currency, region },
      });
      updateUser(updated);
      setPrefMsg('Preferences saved successfully.');
    } catch (err: any) {
      alert(err.message || 'Failed to update preferences');
    } finally {
      setSavingPref(false);
    }
  };

  const handleChangePassword = async (e: React.FormEvent) => {
    e.preventDefault();
    setChangingPwd(true);
    setPwdMsg(null);
    setPwdErr(null);
    try {
      await authApi.changePassword({ old_password: oldPassword, new_password: newPassword });
      setPwdMsg('Password updated successfully.');
      setOldPassword('');
      setNewPassword('');
    } catch (err: any) {
      setPwdErr(err.message || 'Failed to update password');
    } finally {
      setChangingPwd(false);
    }
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      {/* Header */}
      <div className="bg-white rounded-3xl border border-[#DCE5DC] p-6 shadow-card">
        <div className="flex items-center gap-2 mb-1">
          <User className="w-5 h-5 text-[#047857]" />
          <span className="text-xs font-bold uppercase tracking-wider text-[#047857]">User Settings</span>
        </div>
        <h1 className="text-2xl font-extrabold text-[#14231A]">Account & Planning Units</h1>
        <p className="text-xs text-[#4A5F52] mt-1">
          Configure preferred measurement units and personal security credentials.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Profile & Preferences */}
        <div className="bg-white rounded-3xl border border-[#DCE5DC] p-6 shadow-card">
          <h2 className="text-base font-extrabold text-[#14231A] mb-4">Agronomic Preferences</h2>

          {prefMsg && (
            <div className="mb-4 p-3 rounded-xl bg-[#D1FAE5] border border-[#A7F3D0] text-xs font-bold text-[#065F46] flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4" />
              {prefMsg}
            </div>
          )}

          <form onSubmit={handleSavePreferences} className="space-y-4">
            <div>
              <label className="block text-xs font-bold text-[#14231A] mb-1">Full Name</label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="w-full px-3.5 py-2 rounded-xl border border-[#DCE5DC] bg-[#F6F8F4] text-xs font-semibold outline-none"
              />
            </div>

            <div>
              <label className="block text-xs font-bold text-[#14231A] mb-1">Email Address</label>
              <input
                type="email"
                disabled
                value={user?.email || ''}
                className="w-full px-3.5 py-2 rounded-xl border border-[#DCE5DC] bg-[#EEF3EC] text-xs font-semibold text-[#7A8E80]"
              />
            </div>

            <div>
              <label className="block text-xs font-bold text-[#14231A] mb-1">Land Area Unit</label>
              <select
                value={areaUnit}
                onChange={(e) => setAreaUnit(e.target.value)}
                className="w-full px-3.5 py-2 rounded-xl border border-[#DCE5DC] bg-[#F6F8F4] text-xs font-semibold outline-none"
              >
                <option value="ha">Hectares (ha)</option>
                <option value="acre">Acres</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-bold text-[#14231A] mb-1">Currency</label>
              <select
                value={currency}
                onChange={(e) => setCurrency(e.target.value)}
                className="w-full px-3.5 py-2 rounded-xl border border-[#DCE5DC] bg-[#F6F8F4] text-xs font-semibold outline-none"
              >
                <option value="INR">Indian Rupee (₹ INR)</option>
                <option value="USD">US Dollar ($ USD)</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-bold text-[#14231A] mb-1">Default Agricultural Region</label>
              <input
                type="text"
                value={region}
                onChange={(e) => setRegion(e.target.value)}
                className="w-full px-3.5 py-2 rounded-xl border border-[#DCE5DC] bg-[#F6F8F4] text-xs font-semibold outline-none"
              />
            </div>

            <button
              type="submit"
              disabled={savingPref}
              className="w-full mt-2 py-2.5 rounded-xl bg-[#047857] hover:bg-[#065F46] text-white text-xs font-bold shadow-md shadow-[#047857]/20"
            >
              {savingPref ? 'Saving...' : 'Save Preferences'}
            </button>
          </form>
        </div>

        {/* Change Password */}
        <div className="bg-white rounded-3xl border border-[#DCE5DC] p-6 shadow-card flex flex-col justify-between">
          <div>
            <h2 className="text-base font-extrabold text-[#14231A] mb-4">Security Credentials</h2>

            {pwdMsg && (
              <div className="mb-4 p-3 rounded-xl bg-[#D1FAE5] border border-[#A7F3D0] text-xs font-bold text-[#065F46]">
                {pwdMsg}
              </div>
            )}
            {pwdErr && (
              <div className="mb-4 p-3 rounded-xl bg-[#FFE4E6] border border-[#FECDD3] text-xs font-bold text-[#BE123C]">
                {pwdErr}
              </div>
            )}

            <form onSubmit={handleChangePassword} className="space-y-4">
              <div>
                <label className="block text-xs font-bold text-[#14231A] mb-1">Current Password</label>
                <input
                  type="password"
                  required
                  value={oldPassword}
                  onChange={(e) => setOldPassword(e.target.value)}
                  className="w-full px-3.5 py-2 rounded-xl border border-[#DCE5DC] bg-[#F6F8F4] text-xs font-semibold outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-[#14231A] mb-1">New Password</label>
                <input
                  type="password"
                  required
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  placeholder="Minimum 6 characters"
                  className="w-full px-3.5 py-2 rounded-xl border border-[#DCE5DC] bg-[#F6F8F4] text-xs font-semibold outline-none"
                />
              </div>

              <button
                type="submit"
                disabled={changingPwd}
                className="w-full mt-2 py-2.5 rounded-xl bg-[#EEF3EC] hover:bg-[#DCE5DC] text-[#14231A] text-xs font-bold border border-[#DCE5DC]"
              >
                {changingPwd ? 'Updating...' : 'Change Password'}
              </button>
            </form>
          </div>

          <div className="mt-6 p-4 rounded-2xl bg-[#F6F8F4] border border-[#DCE5DC] text-xs text-[#7A8E80]">
            Role: <strong className="text-[#14231A] capitalize">{user?.role || 'planner'}</strong> · 
            Sessions are authenticated via signed JWT bearer tokens with automatic revocation.
          </div>
        </div>
      </div>
    </div>
  );
};
