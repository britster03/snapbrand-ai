// Authentication utilities for frontend
import { apiClient } from './api';

export interface AuthState {
  isAuthenticated: boolean;
  token: string | null;
  user: any | null;
}

export class AuthUtils {
  private static TOKEN_KEY = 'access_token';
  private static USER_KEY = 'user';

  /**
   * Get the current authentication state
   */
  static getAuthState(): AuthState {
    const token = this.getToken();
    const user = this.getUser();
    
    return {
      isAuthenticated: !!token && token !== 'null' && token !== 'undefined',
      token,
      user,
    };
  }

  /**
   * Get token from localStorage
   */
  static getToken(): string | null {
    if (typeof window === 'undefined') return null;
    
    const token = localStorage.getItem(this.TOKEN_KEY);
    if (!token || token === 'null' || token === 'undefined') {
      return null;
    }
    return token;
  }

  /**
   * Set token in localStorage and sync with API client
   */
  static setToken(token: string | null): void {
    if (typeof window === 'undefined') return;
    
    if (token) {
      localStorage.setItem(this.TOKEN_KEY, token);
      apiClient.setAccessToken(token);
    } else {
      localStorage.removeItem(this.TOKEN_KEY);
      apiClient.clearAccessToken();
    }
  }

  /**
   * Get user from localStorage
   */
  static getUser(): any | null {
    if (typeof window === 'undefined') return null;
    
    const user = localStorage.getItem(this.USER_KEY);
    if (!user || user === 'null') return null;
    
    try {
      return JSON.parse(user);
    } catch {
      return null;
    }
  }

  /**
   * Set user in localStorage
   */
  static setUser(user: any | null): void {
    if (typeof window === 'undefined') return;
    
    if (user) {
      localStorage.setItem(this.USER_KEY, JSON.stringify(user));
    } else {
      localStorage.removeItem(this.USER_KEY);
    }
  }

  /**
   * Clear all authentication data
   */
  static clearAuth(): void {
    if (typeof window === 'undefined') return;
    
    localStorage.removeItem(this.TOKEN_KEY);
    localStorage.removeItem(this.USER_KEY);
    apiClient.clearAccessToken();
  }

  /**
   * Check if user is authenticated
   */
  static isAuthenticated(): boolean {
    return this.getAuthState().isAuthenticated;
  }

  /**
   * Get authorization headers
   */
  static getAuthHeaders(): Record<string, string> {
    const token = this.getToken();
    if (!token) {
      throw new Error('No authentication token available');
    }
    
    return {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    };
  }

  /**
   * Redirect to login if not authenticated
   */
  static requireAuth(): boolean {
    if (!this.isAuthenticated()) {
      if (typeof window !== 'undefined') {
        window.location.href = '/login';
      }
      return false;
    }
    return true;
  }

  /**
   * Sync token between localStorage and API client
   */
  static syncToken(): void {
    const token = this.getToken();
    if (token) {
      apiClient.setAccessToken(token);
    } else {
      apiClient.clearAccessToken();
    }
  }
}

/**
 * React hook for authentication state
 */
export function useAuthState(): AuthState {
  if (typeof window === 'undefined') {
    return { isAuthenticated: false, token: null, user: null };
  }
  
  return AuthUtils.getAuthState();
}

/**
 * Initialize authentication utilities
 */
export function initAuth(): void {
  AuthUtils.syncToken();
}