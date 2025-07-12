// Frontend Authentication Utilities
// Copy this code to your frontend project

class AuthManager {
  constructor(baseURL = 'http://localhost:8000') {
    this.baseURL = baseURL;
    this.TOKEN_KEY = 'snapbrand_token';
    this.USER_KEY = 'snapbrand_user';
  }

  // Get token from localStorage
  getToken() {
    const token = localStorage.getItem(this.TOKEN_KEY);
    if (!token || token === 'null' || token === 'undefined') {
      return null;
    }
    return token;
  }

  // Set token in localStorage
  setToken(token) {
    if (token) {
      localStorage.setItem(this.TOKEN_KEY, token);
    } else {
      localStorage.removeItem(this.TOKEN_KEY);
    }
  }

  // Get user from localStorage
  getUser() {
    const user = localStorage.getItem(this.USER_KEY);
    if (!user || user === 'null') {
      return null;
    }
    try {
      return JSON.parse(user);
    } catch (e) {
      return null;
    }
  }

  // Set user in localStorage
  setUser(user) {
    if (user) {
      localStorage.setItem(this.USER_KEY, JSON.stringify(user));
    } else {
      localStorage.removeItem(this.USER_KEY);
    }
  }

  // Clear all auth data
  clearAuth() {
    localStorage.removeItem(this.TOKEN_KEY);
    localStorage.removeItem(this.USER_KEY);
  }

  // Check if user is authenticated
  isAuthenticated() {
    return this.getToken() !== null;
  }

  // Get auth headers
  getAuthHeaders() {
    const token = this.getToken();
    if (!token) {
      throw new Error('No token available');
    }
    return {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    };
  }

  // Login
  async login(email, password) {
    try {
      const response = await fetch(`${this.baseURL}/v1/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
          username: email,
          password: password,
        }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Login failed');
      }

      const data = await response.json();
      this.setToken(data.access_token);

      // Get user info
      const userResponse = await fetch(`${this.baseURL}/v1/auth/me`, {
        headers: this.getAuthHeaders(),
      });

      if (userResponse.ok) {
        const user = await userResponse.json();
        this.setUser(user);
        return { token: data.access_token, user };
      }

      return { token: data.access_token, user: null };
    } catch (error) {
      this.clearAuth();
      throw error;
    }
  }

  // Logout
  async logout() {
    this.clearAuth();
    // Optionally redirect to login page
    window.location.href = '/login';
  }

  // Refresh token
  async refreshToken() {
    try {
      const response = await fetch(`${this.baseURL}/v1/auth/refresh`, {
        method: 'POST',
        headers: this.getAuthHeaders(),
      });

      if (!response.ok) {
        throw new Error('Token refresh failed');
      }

      const data = await response.json();
      this.setToken(data.access_token);
      return data.access_token;
    } catch (error) {
      this.clearAuth();
      throw error;
    }
  }

  // Validate token
  async validateToken() {
    try {
      const response = await fetch(`${this.baseURL}/v1/auth/validate`, {
        headers: this.getAuthHeaders(),
      });

      return response.ok;
    } catch (error) {
      return false;
    }
  }

  // Make authenticated request
  async makeAuthenticatedRequest(url, options = {}) {
    const token = this.getToken();
    
    if (!token) {
      throw new Error('No token available. Please login.');
    }

    const headers = {
      ...this.getAuthHeaders(),
      ...options.headers,
    };

    try {
      const response = await fetch(url, {
        ...options,
        headers,
      });

      // If unauthorized, try to refresh token
      if (response.status === 401) {
        try {
          await this.refreshToken();
          // Retry the original request
          return await fetch(url, {
            ...options,
            headers: {
              ...this.getAuthHeaders(),
              ...options.headers,
            },
          });
        } catch (refreshError) {
          this.clearAuth();
          window.location.href = '/login';
          throw new Error('Session expired. Please login again.');
        }
      }

      return response;
    } catch (error) {
      throw error;
    }
  }

  // Fetch brand profiles
  async fetchBrandProfiles() {
    try {
      const response = await this.makeAuthenticatedRequest(`${this.baseURL}/brands/profiles`);
      
      if (!response.ok) {
        throw new Error('Failed to fetch brand profiles');
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching brand profiles:', error);
      throw error;
    }
  }

  // Create brand profile
  async createBrandProfile(brandData) {
    try {
      const response = await this.makeAuthenticatedRequest(`${this.baseURL}/brands/profiles`, {
        method: 'POST',
        body: JSON.stringify(brandData),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to create brand profile');
      }

      return await response.json();
    } catch (error) {
      console.error('Error creating brand profile:', error);
      throw error;
    }
  }
}

// Export for use in your frontend
// const authManager = new AuthManager('http://localhost:8000');
// export default authManager;

// Usage Examples:
/*
// Login
try {
  const { token, user } = await authManager.login('test@snapbrand.ai', 'password123');
  console.log('Login successful:', user);
} catch (error) {
  console.error('Login failed:', error.message);
}

// Fetch brand profiles
try {
  const brands = await authManager.fetchBrandProfiles();
  console.log('Brands:', brands);
} catch (error) {
  console.error('Error:', error.message);
}

// Create brand profile
try {
  const newBrand = await authManager.createBrandProfile({
    name: "My Brand",
    description: "A great brand",
    industry: "technology",
    // ... other fields
  });
  console.log('Brand created:', newBrand);
} catch (error) {
  console.error('Error:', error.message);
}
*/