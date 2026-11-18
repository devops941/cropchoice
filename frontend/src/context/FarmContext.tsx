import React, { createContext, useContext, useState, useEffect } from 'react';
import { farmsApi } from '../api/client';
import { useAuth } from './AuthContext';

export interface Farm {
  id: string;
  name: string;
  land_ha: number;
  season: string;
  soil: {
    ph: number;
    ec: number;
    oc: number;
    n: number;
    p: number;
    k: number;
    texture: string;
    drainage: string;
  };
  water: {
    rainfall_mm: number;
    effective_rainfall_pct: number;
    irrigation_m3: number;
  };
  budget_inr: number;
  labour_person_days: number;
  location?: {
    state: string;
    district: string;
    lat: number;
    lon: number;
  };
}

interface FarmContextType {
  farms: Farm[];
  selectedFarmId: string | null;
  selectedFarm: Farm | null;
  setSelectedFarmId: (id: string) => void;
  loadFarms: () => Promise<void>;
  loading: boolean;
}

const FarmContext = createContext<FarmContextType | undefined>(undefined);

export const FarmProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated } = useAuth();
  const [farms, setFarms] = useState<Farm[]>([]);
  const [selectedFarmId, setSelectedFarmId] = useState<string | null>(
    localStorage.getItem('cropchoice_selected_farm')
  );
  const [loading, setLoading] = useState(false);

  const loadFarms = async () => {
    if (!isAuthenticated) return;
    try {
      setLoading(true);
      const data = await farmsApi.list();
      setFarms(data);
      if (data.length > 0) {
        if (!selectedFarmId || !data.some((f: Farm) => f.id === selectedFarmId)) {
          setSelectedFarmId(data[0].id);
          localStorage.setItem('cropchoice_selected_farm', data[0].id);
        }
      }
    } catch (e) {
      console.error('Failed to load farms', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadFarms();
  }, [isAuthenticated]);

  const handleSelectFarm = (id: string) => {
    setSelectedFarmId(id);
    localStorage.setItem('cropchoice_selected_farm', id);
  };

  const selectedFarm = farms.find((f) => f.id === selectedFarmId) || (farms.length > 0 ? farms[0] : null);

  return (
    <FarmContext.Provider
      value={{
        farms,
        selectedFarmId,
        selectedFarm,
        setSelectedFarmId: handleSelectFarm,
        loadFarms,
        loading,
      }}
    >
      {children}
    </FarmContext.Provider>
  );
};

export const useFarm = () => {
  const context = useContext(FarmContext);
  if (!context) throw new Error('useFarm must be used within a FarmProvider');
  return context;
};
