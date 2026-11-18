import React, { createContext, useContext, useState, useEffect } from 'react';
import { getStoredUser, setStoredUser, getAuthToken, setAuthToken, removeAuthToken, authApi } from '../api/client';

interface User {
  id: string;
  name: string;
  email: string;
  role: 'admin' | 'planner';
  preferences?: any;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isAdmin: boolean;
  login: (token: string, user: User) => void;
  logout: () => void;
  updateUser: (user: User) => void;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(getStoredUser());
  const [token, setToken] = useState<string | null>(getAuthToken());

  useEffect(() => {
    if (token && !user) {
      authApi.getMe().then((data) => {
        setUser(data);
        setStoredUser(data);
      }).catch(() => {
        logout();
      });
    }
  }, [token]);

  const login = (newToken: string, newUser: User) => {
    setToken(newToken);
    setUser(newUser);
    setAuthToken(newToken);
    setStoredUser(newUser);
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    removeAuthToken();
  };

  const updateUser = (updatedUser: User) => {
    setUser(updatedUser);
    setStoredUser(updatedUser);
  };

  const refreshUser = async () => {
    try {
      const data = await authApi.getMe();
      setUser(data);
      setStoredUser(data);
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isAuthenticated: !!token && !!user,
        isAdmin: user?.role === 'admin',
        login,
        logout,
        updateUser,
        refreshUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within an AuthProvider');
  return context;
};
