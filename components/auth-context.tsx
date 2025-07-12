'use client';

import React, { createContext, useContext, useEffect, useState } from 'react';
import { User, ApiClient } from '../lib/api';
import { AuthUtils } from '../lib/auth-utils';

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (username: string, password: string) => Promise<void>;
  register: (email: string, username: string, password: string, fullName?: string) => Promise<void>;
  logout: () => void;
  refetchUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const apiClient = new ApiClient();

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const refetchUser = async () => {
    try {
      const currentUser = await apiClient.getCurrentUser();
      setUser(currentUser);
      AuthUtils.setUser(currentUser);
    } catch (error) {
      console.error('Failed to fetch user:', error);
      setUser(null);
      AuthUtils.clearAuth();
    }
  };

  useEffect(() => {
    // Sync token on init
    AuthUtils.syncToken();
    
    const token = AuthUtils.getToken();
    if (token) {
      // Try to load user from localStorage first
      const cachedUser = AuthUtils.getUser();
      if (cachedUser) {
        setUser(cachedUser);
      }
      
      // Then fetch fresh user data
      refetchUser().finally(() => setIsLoading(false));
    } else {
      setIsLoading(false);
    }
  }, []);

  const login = async (username: string, password: string) => {
    try {
      const response = await apiClient.login({ username, password });
      AuthUtils.setToken(response.access_token);
      await refetchUser();
    } catch (error) {
      console.error('Login failed:', error);
      throw error;
    }
  };

  const register = async (email: string, username: string, password: string, fullName?: string) => {
    try {
      const newUser = await apiClient.register({
        email,
        username,
        password,
        full_name: fullName,
      });
      setUser(newUser);
      AuthUtils.setUser(newUser);
      // After registration, login automatically
      await login(username, password);
    } catch (error) {
      console.error('Registration failed:', error);
      throw error;
    }
  };

  const logout = () => {
    AuthUtils.clearAuth();
    setUser(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isLoading,
        isAuthenticated: !!user,
        login,
        register,
        logout,
        refetchUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

export { apiClient }; 