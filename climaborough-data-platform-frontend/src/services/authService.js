// Authentication service for managing Keycloak interactions
import config from '../config/env.js';

const KEYCLOAK_SERVER_URL = config.keycloak.url || 'https://localhost:8080';
const KEYCLOAK_REALM = config.keycloak.realm || 'master';
const AUTH_SERVER_URL = `${KEYCLOAK_SERVER_URL}/realms/${KEYCLOAK_REALM}`;
const CLIENT_ID = config.keycloak.clientId || 'your-client-id';

// Validation for required environment variables
if (!config.keycloak.url) {
  console.warn('KEYCLOAK_URL not set, using fallback');
}
if (!config.keycloak.clientId) {
  console.warn('CLIENT_ID not set, using fallback');
}

// Cookie utility functions
const cookieUtils = {
  set(name, value, options = {}) {
    let cookieString = `${name}=${encodeURIComponent(value)}`;
    
    if (options.expires) {
      cookieString += `; expires=${options.expires.toUTCString()}`;
    }
    if (options.maxAge) {
      cookieString += `; max-age=${options.maxAge}`;
    }
    if (options.secure) {
      cookieString += '; secure';
    }
    if (options.httpOnly) {
      cookieString += '; httponly';
    }
    if (options.sameSite) {
      cookieString += `; samesite=${options.sameSite}`;
    }
    cookieString += '; path=/';
    
    // Add security check for production
    if (window.location.protocol === 'http:' && options.secure) {
      console.warn('Secure cookies cannot be set over HTTP. Use HTTPS in production.');
    }
    
    document.cookie = cookieString;
  },
  
  get(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) {
      return decodeURIComponent(parts.pop().split(';').shift());
    }
    return null;
  },
  
  remove(name) {
    document.cookie = `${name}=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/`;
  }
};

export const authService = {
  // Clean up old localStorage tokens (migration helper)
  cleanupLocalStorage() {
    localStorage.removeItem('keycloak_token');
    localStorage.removeItem('keycloak_refresh_token');
    localStorage.removeItem('keycloak_expires_at');
    localStorage.removeItem('userType');
  },  // Get current authentication status
  isAuthenticated() {
    // Clean up old localStorage on first call
    this.cleanupLocalStorage();
    
    const token = cookieUtils.get('keycloak_token');
    const expiresAt = cookieUtils.get('keycloak_expires_at');
    
    if (!token) return false;
    
    // Validate token format (basic JWT structure check)
    if (!this.isValidJWTFormat(token)) {
      console.warn('Invalid token format detected, clearing cookies');
      this.clearAllTokens();
      return false;
    }
    
    // Check if token is expired
    if (expiresAt && Date.now() > parseInt(expiresAt)) {
      // Token is expired, try to refresh silently
      this.refreshToken().catch(() => {
        // If refresh fails, clear cookies
        this.clearAllTokens();
      });
      return false;
    }
    
    return true;
  },

  // Helper method to validate JWT format
  isValidJWTFormat(token) {
    try {
      const parts = token.split('.');
      return parts.length === 3 && parts.every(part => part.length > 0);
    } catch {
      return false;
    }
  },

  // Helper method to clear all authentication tokens
  clearAllTokens() {
    cookieUtils.remove('keycloak_token');
    cookieUtils.remove('keycloak_refresh_token');
    cookieUtils.remove('keycloak_expires_at');
    this.cleanupLocalStorage();
  },
    // Get user info from token
  getUserInfo() {
    const token = cookieUtils.get('keycloak_token');
    if (!token) return null;
    
    try {
      const base64Url = token.split('.')[1];
      const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
      const jsonPayload = decodeURIComponent(atob(base64).split('').map(function(c) {
        return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
      }).join(''));
      
      return JSON.parse(jsonPayload);
    } catch (error) {
      console.error('Error parsing token:', error);
      return null;
    }
  },
    // Initiate login process
  login(redirectPath = '/') {
    // Store the intended destination for after login
    sessionStorage.setItem('postLoginRedirect', redirectPath);
    
    const redirectUri = `${window.location.origin}/callback`;
    const state = this.generateRandomString(32); // CSRF protection
    
    // Store state for validation
    sessionStorage.setItem('oauth_state', state);
    
    const authUrl = `${AUTH_SERVER_URL}/protocol/openid-connect/auth` +
      `?client_id=${CLIENT_ID}` +
      `&redirect_uri=${encodeURIComponent(redirectUri)}` +
      '&response_type=code' +
      '&scope=openid profile email' +
      `&state=${state}`;
      
    window.location.href = authUrl;
  },

  // Generate random string for CSRF protection
  generateRandomString(length) {
    const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    let result = '';
    for (let i = 0; i < length; i++) {
      result += characters.charAt(Math.floor(Math.random() * characters.length));
    }
    return result;
  },
  // Handle callback from Keycloak after login
  async handleCallback(code, state = null) {
    const redirectUri = `${window.location.origin}/callback`;
    
    // Validate state parameter for CSRF protection
    const storedState = sessionStorage.getItem('oauth_state');
    if (state && storedState && state !== storedState) {
      sessionStorage.removeItem('oauth_state');
      throw new Error('Invalid state parameter - possible CSRF attack');
    }
    sessionStorage.removeItem('oauth_state');
    
    try {
      const response = await fetch(`${AUTH_SERVER_URL}/protocol/openid-connect/token`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
          grant_type: 'authorization_code',
          client_id: CLIENT_ID,
          code: code,
          redirect_uri: redirectUri
        })
      });
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(`Failed to exchange authorization code: ${errorData.error || response.statusText}`);
      }
      
      const data = await response.json();
      
      // Store tokens in secure cookies
      const tokenExpiry = new Date(Date.now() + (data.expires_in * 1000));
      const isSecure = window.location.protocol === 'https:';
      
      cookieUtils.set('keycloak_token', data.access_token, {
        expires: tokenExpiry,
        secure: isSecure,
        sameSite: 'Strict'
      });
      
      if (data.refresh_token) {
        cookieUtils.set('keycloak_refresh_token', data.refresh_token, {
          expires: new Date(Date.now() + (30 * 24 * 60 * 60 * 1000)), // 30 days
          secure: isSecure,
          sameSite: 'Strict'
        });
      }
      
      if (data.expires_in) {
        const expiresAt = Date.now() + (data.expires_in * 1000);
        cookieUtils.set('keycloak_expires_at', expiresAt.toString(), {
          expires: tokenExpiry,
          secure: isSecure,
          sameSite: 'Strict'
        });
      }
      
      return true;
    } catch (error) {
      console.error('Error handling callback:', error);
      this.clearAllTokens();
      return Promise.reject(error);
    }
  },
  // Logout from Keycloak
  logout() {
    const redirectUri = encodeURIComponent(window.location.origin);
    
    // Clear all authentication data
    this.clearAllTokens();
    sessionStorage.removeItem('postLoginRedirect');
    
    // Redirect to Keycloak logout
    window.location.href = `${AUTH_SERVER_URL}/protocol/openid-connect/logout?client_id=${CLIENT_ID}&post_logout_redirect_uri=${redirectUri}`;
  },
    // Refresh the token
  async refreshToken() {
    const refreshToken = cookieUtils.get('keycloak_refresh_token');
    if (!refreshToken) return Promise.reject('No refresh token available');
    
    try {
      const response = await fetch(`${AUTH_SERVER_URL}/protocol/openid-connect/token`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
          grant_type: 'refresh_token',
          client_id: CLIENT_ID,
          refresh_token: refreshToken
        })
      });
      
      if (!response.ok) {
        throw new Error('Failed to refresh token');
      }
        const data = await response.json();
      
      // Store tokens in secure cookies
      const tokenExpiry = new Date(Date.now() + (data.expires_in * 1000));
      
      cookieUtils.set('keycloak_token', data.access_token, {
        expires: tokenExpiry,
        secure: true,
        sameSite: 'Strict'
      });
      
      if (data.refresh_token) {
        cookieUtils.set('keycloak_refresh_token', data.refresh_token, {
          expires: new Date(Date.now() + (30 * 24 * 60 * 60 * 1000)), // 30 days
          secure: true,
          sameSite: 'Strict'
        });
      }
      
      if (data.expires_in) {
        const expiresAt = Date.now() + (data.expires_in * 1000);
        cookieUtils.set('keycloak_expires_at', expiresAt.toString(), {
          expires: tokenExpiry,
          secure: true,
          sameSite: 'Strict'
        });
      }
      
      return true;    } catch (error) {
      console.error('Error refreshing token:', error);
      // Clear cookies on refresh failure
      this.clearAllTokens();
      return Promise.reject(error);
    }
  },
    // Get the current access token (with auto-refresh if needed)
  async getAccessToken() {
    if (!this.isAuthenticated()) {
      return Promise.reject('Not authenticated');
    }
    
    const expiresAt = cookieUtils.get('keycloak_expires_at');
    if (expiresAt && Date.now() > parseInt(expiresAt) - 30000) { // Refresh if less than 30s left
      await this.refreshToken();
    }
    
    return cookieUtils.get('keycloak_token');
  },
  
  // Get user roles/permissions
  getUserRoles() {
    const userInfo = this.getUserInfo();
    if (!userInfo) return [];
    
    return userInfo.group_membership || [];
  },
  
  // Check if user has specific role
  hasRole(role) {
    const roles = this.getUserRoles();
    return roles.includes(role);
  },
  
  // Check if user belongs to a city group
  getUserCity() {
    const userInfo = this.getUserInfo();
    if (!userInfo) return null;
    
    const cityGroup = userInfo.group_membership?.find(group => group.startsWith('/City/'));
    return cityGroup ? cityGroup.split('/').pop() : null;
  }
};

// Create axios interceptor or fetch wrapper for automatic token handling
export const authFetch = async (url, options = {}) => {
  try {
    const token = await authService.getAccessToken();
    
    const headers = {
      ...options.headers,
      'Authorization': `Bearer ${token}`
    };
    
    return fetch(url, {
      ...options,
      headers
    });
  } catch (error) {
    console.error('Auth fetch error:', error);
    throw error;
  }
}; 