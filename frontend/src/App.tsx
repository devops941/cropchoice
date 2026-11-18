import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { FarmProvider } from './context/FarmContext';
import { AppLayout } from './components/layout/AppLayout';

import { LandingPage } from './pages/LandingPage';
import { LoginPage } from './pages/LoginPage';
import { RegisterPage } from './pages/RegisterPage';
import { DashboardPage } from './pages/DashboardPage';
import { WizardPage } from './pages/WizardPage';
import { FarmsPage } from './pages/FarmsPage';
import { CropsPage } from './pages/CropsPage';
import { PricesPage } from './pages/PricesPage';
import { CriteriaPage } from './pages/CriteriaPage';
import { RankingPage } from './pages/RankingPage';
import { OptimizerPage } from './pages/OptimizerPage';
import { ScenariosPage } from './pages/ScenariosPage';
import { SimulationPage } from './pages/SimulationPage';
import { ImportPage } from './pages/ImportPage';
import { ReportsPage } from './pages/ReportsPage';
import { AdminPage } from './pages/AdminPage';
import { ProfilePage } from './pages/ProfilePage';
import { AboutPage } from './pages/AboutPage';

const ProtectedRoute: React.FC<{ children: React.ReactNode; adminOnly?: boolean }> = ({
  children,
  adminOnly = false,
}) => {
  const { isAuthenticated, isAdmin } = useAuth();

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (adminOnly && !isAdmin) {
    return <Navigate to="/app" replace />;
  }

  return <>{children}</>;
};

export const App: React.FC = () => {
  return (
    <AuthProvider>
      <FarmProvider>
        <BrowserRouter>
          <Routes>
            {/* Public Pages */}
            <Route path="/" element={<LandingPage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route path="/about" element={<AboutPage />} />

            {/* Authenticated Dashboard Shell */}
            <Route
              path="/app"
              element={
                <ProtectedRoute>
                  <AppLayout />
                </ProtectedRoute>
              }
            >
              <Route index element={<DashboardPage />} />
              <Route path="wizard" element={<WizardPage />} />
              <Route path="farms" element={<FarmsPage />} />
              <Route path="crops" element={<CropsPage />} />
              <Route path="prices" element={<PricesPage />} />
              <Route path="criteria" element={<CriteriaPage />} />
              <Route path="ranking" element={<RankingPage />} />
              <Route path="optimizer" element={<OptimizerPage />} />
              <Route path="scenarios" element={<ScenariosPage />} />
              <Route path="simulation" element={<SimulationPage />} />
              <Route path="import" element={<ImportPage />} />
              <Route path="reports" element={<ReportsPage />} />
              <Route path="profile" element={<ProfilePage />} />
              <Route
                path="admin"
                element={
                  <ProtectedRoute adminOnly>
                    <AdminPage />
                  </ProtectedRoute>
                }
              />
            </Route>

            {/* Fallback */}
            <Route path="*" element={<Navigate to="/app" replace />} />
          </Routes>
        </BrowserRouter>
      </FarmProvider>
    </AuthProvider>
  );
};

export default App;
