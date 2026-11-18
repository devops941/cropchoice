const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

export function getAuthToken(): string | null {
  return localStorage.getItem('cropchoice_token');
}

export function setAuthToken(token: string) {
  localStorage.setItem('cropchoice_token', token);
}

export function removeAuthToken() {
  localStorage.removeItem('cropchoice_token');
  localStorage.removeItem('cropchoice_user');
}

export function getStoredUser(): any | null {
  const user = localStorage.getItem('cropchoice_user');
  return user ? JSON.parse(user) : null;
}

export function setStoredUser(user: any) {
  localStorage.setItem('cropchoice_user', JSON.stringify(user));
}

export async function apiRequest<T = any>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = getAuthToken();
  const headers = new Headers(options.headers || {});

  if (!headers.has('Content-Type') && !(options.body instanceof FormData)) {
    headers.set('Content-Type', 'application/json');
  }

  if (token) {
    headers.set('Authorization', `Bearer ${token}`);
  }

  const response = await fetch(`${BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (response.status === 401) {
    removeAuthToken();
    if (!window.location.pathname.startsWith('/login') && !window.location.pathname.startsWith('/register') && window.location.pathname !== '/') {
      window.location.href = '/login';
    }
  }

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(errorData.detail || `Request failed with status ${response.status}`);
  }

  return response.json();
}

// Auth API
export const authApi = {
  login: (data: any) => apiRequest('/auth/login', { method: 'POST', body: JSON.stringify(data) }),
  register: (data: any) => apiRequest('/auth/register', { method: 'POST', body: JSON.stringify(data) }),
  getMe: () => apiRequest('/auth/me'),
  updateMe: (data: any) => apiRequest('/auth/me', { method: 'PUT', body: JSON.stringify(data) }),
  changePassword: (data: any) => apiRequest('/auth/change-password', { method: 'POST', body: JSON.stringify(data) }),
};

// Dashboard API
export const dashboardApi = {
  getOverview: (farmId?: string) => apiRequest(`/dashboard/overview${farmId ? `?farm_id=${farmId}` : ''}`),
};

// Farms API
export const farmsApi = {
  list: () => apiRequest('/farms'),
  get: (id: string) => apiRequest(`/farms/${id}`),
  create: (data: any) => apiRequest('/farms', { method: 'POST', body: JSON.stringify(data) }),
  update: (id: string, data: any) => apiRequest(`/farms/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  delete: (id: string) => apiRequest(`/farms/${id}`, { method: 'DELETE' }),
};

// Crops API
export const cropsApi = {
  list: (params?: any) => {
    const query = new URLSearchParams(params || {}).toString();
    return apiRequest(`/crops${query ? `?${query}` : ''}`);
  },
  get: (id: string) => apiRequest(`/crops/${id}`),
  create: (data: any) => apiRequest('/crops', { method: 'POST', body: JSON.stringify(data) }),
  update: (id: string, data: any) => apiRequest(`/crops/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  delete: (id: string) => apiRequest(`/crops/${id}`, { method: 'DELETE' }),
  getSoilFit: (cropId: string, farmId: string) => apiRequest(`/crops/${cropId}/soil-fit?farm_id=${farmId}`),
};

// Prices API
export const pricesApi = {
  list: (params?: any) => {
    const query = new URLSearchParams(params || {}).toString();
    return apiRequest(`/prices${query ? `?${query}` : ''}`);
  },
  add: (data: any) => apiRequest('/prices', { method: 'POST', body: JSON.stringify(data) }),
  getStats: (cropId: string, months = 36) => apiRequest(`/prices/${cropId}/stats?months=${months}`),
};

// Criteria & AHP API
export const criteriaApi = {
  getPresets: () => apiRequest('/criteria/presets'),
  calculateAhp: (data: any) => apiRequest('/criteria/ahp', { method: 'POST', body: JSON.stringify(data) }),
  listProfiles: () => apiRequest('/criteria/profiles'),
  createProfile: (data: any) => apiRequest('/criteria/profiles', { method: 'POST', body: JSON.stringify(data) }),
  deleteProfile: (id: string) => apiRequest(`/criteria/profiles/${id}`, { method: 'DELETE' }),
};

// Rankings API
export const rankingsApi = {
  run: (data: any) => apiRequest('/rankings', { method: 'POST', body: JSON.stringify(data) }),
  list: (farmId?: string) => apiRequest(`/rankings${farmId ? `?farm_id=${farmId}` : ''}`),
  get: (id: string) => apiRequest(`/rankings/${id}`),
  computeSensitivity: (id: string) => apiRequest(`/rankings/${id}/sensitivity`, { method: 'POST' }),
};

// Optimizer API
export const optimizerApi = {
  run: (data: any) => apiRequest('/optimizations', { method: 'POST', body: JSON.stringify(data) }),
  list: (farmId?: string) => apiRequest(`/optimizations${farmId ? `?farm_id=${farmId}` : ''}`),
  get: (id: string) => apiRequest(`/optimizations/${id}`),
  checkFeasibility: (data: any) => apiRequest('/optimizations/feasibility-check', { method: 'POST', body: JSON.stringify(data) }),
};

// Scenarios API
export const scenariosApi = {
  list: (farmId?: string) => apiRequest(`/scenarios${farmId ? `?farm_id=${farmId}` : ''}`),
  create: (data: any) => apiRequest('/scenarios', { method: 'POST', body: JSON.stringify(data) }),
  compare: (scenarioIds: string[]) => apiRequest('/scenarios/compare', { method: 'POST', body: JSON.stringify(scenarioIds) }),
  delete: (id: string) => apiRequest(`/scenarios/${id}`, { method: 'DELETE' }),
};

// Simulations API
export const simulationsApi = {
  run: (data: any) => apiRequest('/simulations', { method: 'POST', body: JSON.stringify(data) }),
  getByOpt: (optId: string) => apiRequest(`/simulations/by-optimization/${optId}`),
  get: (id: string) => apiRequest(`/simulations/${id}`),
};

// Import & Export API
export const importExportApi = {
  getSampleUrl: (kind: string, ext = 'csv') => `${BASE_URL}/import-export/sample/${kind}.${ext}`,
  upload: async (kind: string, file: File, autoCommit = false) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('auto_commit', autoCommit ? 'true' : 'false');
    return apiRequest(`/import-export/upload/${kind}`, { method: 'POST', body: formData });
  },
  exportRankingUrl: (id: string) => `${BASE_URL}/import-export/export/ranking/${id}.csv`,
  exportOptimizationUrl: (id: string) => `${BASE_URL}/import-export/export/optimization/${id}.xlsx`,
};

// Reports API
export const reportsApi = {
  generate: (data: any) => apiRequest('/reports/generate', { method: 'POST', body: JSON.stringify(data) }),
};

// Admin API
export const adminApi = {
  listUsers: () => apiRequest('/admin/users'),
  setRole: (userId: string, role: string) => apiRequest(`/admin/users/${userId}/role`, { method: 'PUT', body: JSON.stringify({ role }) }),
  toggleLock: (userId: string, lock: boolean) => apiRequest(`/admin/users/${userId}/toggle-lock`, { method: 'PUT', body: JSON.stringify({ lock }) }),
  getAuditLog: (limit = 100) => apiRequest(`/admin/audit-log?limit=${limit}`),
  getSystemStatus: () => apiRequest('/admin/system'),
};
