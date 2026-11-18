import React, { useState, useEffect } from 'react';
import { adminApi } from '../api/client';
import { ShieldCheck, Users, Lock, Unlock, Database, Activity, CheckCircle2 } from 'lucide-react';

export const AdminPage: React.FC = () => {
  const [users, setUsers] = useState<any[]>([]);
  const [auditLogs, setAuditLogs] = useState<any[]>([]);
  const [systemStatus, setSystemStatus] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  const fetchAdminData = async () => {
    try {
      setLoading(true);
      const [u, l, s] = await Promise.all([
        adminApi.listUsers(),
        adminApi.getAuditLog(50),
        adminApi.getSystemStatus(),
      ]);
      setUsers(u);
      setAuditLogs(l);
      setSystemStatus(s);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAdminData();
  }, []);

  const handleRoleToggle = async (userId: string, currentRole: string) => {
    const newRole = currentRole === 'admin' ? 'planner' : 'admin';
    await adminApi.setRole(userId, newRole);
    fetchAdminData();
  };

  const handleLockToggle = async (userId: string, isLocked: boolean) => {
    await adminApi.toggleLock(userId, !isLocked);
    fetchAdminData();
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-3xl border border-[#DCE5DC] p-6 shadow-card">
        <div className="flex items-center gap-2 mb-1">
          <ShieldCheck className="w-5 h-5 text-[#D97706]" />
          <span className="text-xs font-bold uppercase tracking-wider text-[#D97706]">
            Superuser Control Panel
          </span>
        </div>
        <h1 className="text-2xl font-extrabold text-[#14231A]">System Administration</h1>
        <p className="text-xs text-[#4A5F52] mt-1">
          User access controls, account lockout security, immutable audit logs, and MongoDB Atlas telemetry.
        </p>
      </div>

      {/* System Telemetry Cards */}
      {systemStatus && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <div className="p-4 rounded-2xl bg-white border border-[#DCE5DC] shadow-card">
            <div className="text-[11px] font-bold text-[#7A8E80] uppercase">Database Status</div>
            <div className="text-lg font-black text-[#047857] mt-1 flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-[#10B981] animate-pulse" />
              Connected (Atlas)
            </div>
            <div className="text-xs text-[#4A5F52] mt-0.5 font-mono">{systemStatus.database_name}</div>
          </div>

          <div className="p-4 rounded-2xl bg-white border border-[#DCE5DC] shadow-card">
            <div className="text-[11px] font-bold text-[#7A8E80] uppercase">Crop Genomes</div>
            <div className="text-2xl font-black text-[#14231A] mt-1 tabular-nums">
              {systemStatus.collections?.crops} crops
            </div>
            <div className="text-xs text-[#047857] mt-0.5">Shared Master Library</div>
          </div>

          <div className="p-4 rounded-2xl bg-white border border-[#DCE5DC] shadow-card">
            <div className="text-[11px] font-bold text-[#7A8E80] uppercase">Price History Data</div>
            <div className="text-2xl font-black text-[#D97706] mt-1 tabular-nums">
              {systemStatus.collections?.prices?.toLocaleString()} points
            </div>
            <div className="text-xs text-[#B45309] mt-0.5">Monthly Agmarknet series</div>
          </div>

          <div className="p-4 rounded-2xl bg-white border border-[#DCE5DC] shadow-card">
            <div className="text-[11px] font-bold text-[#7A8E80] uppercase">Audited Events</div>
            <div className="text-2xl font-black text-[#0D9488] mt-1 tabular-nums">
              {systemStatus.collections?.audit_logs} logs
            </div>
            <div className="text-xs text-[#0F766E] mt-0.5">Traceable audit entries</div>
          </div>
        </div>
      )}

      {/* User Management Table */}
      <div className="bg-white rounded-3xl border border-[#DCE5DC] p-6 shadow-card">
        <h2 className="text-base font-extrabold text-[#14231A] mb-4">User Accounts & Role Permissions</h2>
        <div className="border border-[#DCE5DC] rounded-2xl overflow-hidden">
          <table className="w-full text-left text-xs">
            <thead className="bg-[#EEF3EC] text-[#14231A] font-bold">
              <tr>
                <th className="p-3">Name</th>
                <th className="p-3">Email</th>
                <th className="p-3">Role</th>
                <th className="p-3">Status</th>
                <th className="p-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#DCE5DC]">
              {users.map((u) => {
                const isLocked = !!u.locked_until && new Date(u.locked_until) > new Date();
                return (
                  <tr key={u.id} className="hover:bg-[#F6F8F4] transition-colors">
                    <td className="p-3 font-bold text-[#14231A]">{u.name}</td>
                    <td className="p-3 font-mono text-[11px] text-[#4A5F52]">{u.email}</td>
                    <td className="p-3">
                      <span
                        className={`text-[10px] font-bold px-2 py-0.5 rounded-full uppercase ${
                          u.role === 'admin'
                            ? 'bg-[#FEF3C7] text-[#B45309] border border-[#FDE68A]'
                            : 'bg-[#D1FAE5] text-[#065F46] border border-[#A7F3D0]'
                        }`}
                      >
                        {u.role}
                      </span>
                    </td>
                    <td className="p-3">
                      {isLocked ? (
                        <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-[#FFE4E6] text-[#BE123C]">
                          Locked
                        </span>
                      ) : (
                        <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-[#D1FAE5] text-[#065F46]">
                          Active
                        </span>
                      )}
                    </td>
                    <td className="p-3 text-right space-x-2">
                      <button
                        onClick={() => handleRoleToggle(u.id, u.role)}
                        className="px-2.5 py-1 rounded-lg border border-[#DCE5DC] text-[11px] font-bold text-[#4A5F52] hover:bg-[#EEF3EC]"
                      >
                        Set as {u.role === 'admin' ? 'Planner' : 'Admin'}
                      </button>
                      <button
                        onClick={() => handleLockToggle(u.id, isLocked)}
                        className="px-2.5 py-1 rounded-lg border border-[#DCE5DC] text-[11px] font-bold text-[#BE123C] hover:bg-[#FFE4E6]"
                      >
                        {isLocked ? 'Unlock' : 'Lock Account'}
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Audit Log Table */}
      <div className="bg-white rounded-3xl border border-[#DCE5DC] p-6 shadow-card">
        <h2 className="text-base font-extrabold text-[#14231A] mb-4">Security & Action Audit Log</h2>
        <div className="border border-[#DCE5DC] rounded-2xl overflow-hidden max-h-80 overflow-y-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-[#EEF3EC] text-[#14231A] font-bold sticky top-0">
              <tr>
                <th className="p-3">Timestamp</th>
                <th className="p-3">Action</th>
                <th className="p-3">Entity</th>
                <th className="p-3">User ID</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#DCE5DC] font-mono text-[11px]">
              {auditLogs.map((log) => (
                <tr key={log.id} className="hover:bg-[#F6F8F4]">
                  <td className="p-3 text-[#7A8E80]">{new Date(log.at).toLocaleString()}</td>
                  <td className="p-3 font-bold uppercase text-[#047857]">{log.action}</td>
                  <td className="p-3 text-[#14231A]">{log.collection}</td>
                  <td className="p-3 text-[#7A8E80]">{log.user_id}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
