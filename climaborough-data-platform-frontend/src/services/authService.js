// Authentication service using official Keycloak JavaScript adapter
import Keycloak from 'keycloak-js';
import config from '../config/env.js';

let keycloak = null;
let initPromise = null;

// Initialize Keycloak instance
const initKeycloak = () => {
  if (initPromise) {
    return initPromise;
  }

  const keycloakConfig = {
    url: config.keycloak.url,
    realm: config.keycloak.realm,
    clientId: config.keycloak.clientId
  };

  keycloak = new Keycloak(keycloakConfig);

  initPromise = keycloak.init({
    onLoad: 'check-sso',
    checkLoginIframe: false, // Disable iframe checking for better performance
    pkceMethod: 'S256' // Use PKCE for better security
    // silentCheckSsoRedirectUri: window.location.origin + '/silent-check-sso.html', // Removed due to X-Frame-Options issue
  }).then((authenticated) => {
    //console.log('Keycloak initialized, authenticated:', authenticated);
    
    // Set up token refresh
    if (authenticated) {
      setupTokenRefresh();
    }
    
    return keycloak;
  }).catch((error) => {
    console.error('Keycloak initialization failed:', error);
    throw error;
  });

  return initPromise;
};

// Set up automatic token refresh
const setupTokenRefresh = () => {
  if (!keycloak) return;

  // Refresh token when it's about to expire (5 minutes before)
  setInterval(() => {
    if (keycloak.authenticated) {
      keycloak.updateToken(300).then((refreshed) => {
        if (refreshed) {
          //console.log('Token refreshed');
          // Dispatch event for other components to listen to
          window.dispatchEvent(new CustomEvent('keycloak-token-refreshed', {
            detail: { token: keycloak.token }
          }));
        }
      }).catch((error) => {
        console.error('Failed to refresh token:', error);
        // Force re-authentication
        keycloak.login();
      });
    }
  }, 60000); // Check every minute
};

export const authService = {
  // Initialize Keycloak
  async init() {
    return await initKeycloak();
  },

  // Get Keycloak instance
  getKeycloak() {
    return keycloak;
  },

  // Check if user is authenticated
  isAuthenticated() {
    return keycloak?.authenticated || false;
  },

  // Login
  login(redirectPath = '/') {
    if (!keycloak) {
      console.error('Keycloak not initialized');
      return;
    }
    
    // Store redirect path for after login
    sessionStorage.setItem('postLoginRedirect', redirectPath);
    
    return keycloak.login({
      redirectUri: window.location.origin + '/auth/callback'
    });
  },

  // Logout
  logout() {
    if (!keycloak) {
      console.error('Keycloak not initialized');
      return;
    }
    
    return keycloak.logout({
      redirectUri: window.location.origin
    });
  },

  // Clean up old localStorage tokens from previous authentication system
  cleanupLocalStorage() {
    const keysToRemove = [
      'access_token',
      'refresh_token', 
      'token_expiry',
      'user_info',
      'auth_token',
      'keycloak_token'
    ];
    
    keysToRemove.forEach(key => {
      if (localStorage.getItem(key)) {
        localStorage.removeItem(key);
        //console.log(`Cleaned up old auth data: ${key}`);
      }
    });
  },

  // Get access token
  async getAccessToken() {
    if (!keycloak?.authenticated) {
      return null;
    }

    try {
      // Refresh token if it's about to expire (5 minutes)
      await keycloak.updateToken(300);
      return keycloak.token;
    } catch (error) {
      console.error('Failed to get access token:', error);
      return null;
    }
  },

  // Get user info
  getUserInfo() {
    if (!keycloak?.authenticated) {
      return null;
    }
    
    return keycloak.tokenParsed;
  },

  // Get user profile (detailed info)
  async getUserProfile() {
    if (!keycloak?.authenticated) {
      return null;
    }

    try {
      return await keycloak.loadUserProfile();
    } catch (error) {
      console.error('Failed to load user profile:', error);
      return null;
    }
  },

  // Get user roles
  getUserRoles() {
    if (!keycloak?.authenticated) {
      return [];
    }
    
    const realmRoles = keycloak.realmAccess?.roles || [];
    const resourceRoles = keycloak.resourceAccess?.[config.keycloak.clientId]?.roles || [];
    
    return [...realmRoles, ...resourceRoles];
  },

  // Check if user has specific role
  hasRole(role) {
    if (!keycloak?.authenticated) {
      return false;
    }
    
    return keycloak.hasRealmRole(role) || keycloak.hasResourceRole(role);
  },

  // Get user city from groups
  getUserCity() {
    const userInfo = this.getUserInfo();
    if (!userInfo || !userInfo.group_membership) {
      return null;
    }
    
    // Find city catalog group (e.g., /athens-catalog -> athens)
    const cityGroup = userInfo.group_membership.find(group => group.endsWith('-catalog'));
    
    if (cityGroup) {
      // Extract city name from group path (e.g., /athens-catalog -> athens)
      const cityName = cityGroup.replace(/^\//, '').replace(/-catalog$/, '');
      
      // Capitalize first letter for proper city name
      return cityName.charAt(0).toUpperCase() + cityName.slice(1);
    }
    
    return null;
  },

  // Check if user has admin role
  isAdmin() {
    const userInfo = this.getUserInfo();
    if (!userInfo || !userInfo.group_membership) {
      return false;
    }
    
    const groups = userInfo.group_membership;
    return groups.includes('/Administrator') || groups.includes('/Super-Administrator');
  },

  // Check if user is a city user (has a city catalog group)
  isCityUser() {
    const userInfo = this.getUserInfo();
    if (!userInfo || !userInfo.group_membership) {
      return false;
    }
    
    return userInfo.group_membership.some(group => group.endsWith('-catalog'));
  },

  // Get all user groups
  getUserGroups() {
    const userInfo = this.getUserInfo();
    if (!userInfo || !userInfo.group_membership) {
      return [];
    }
    
    return userInfo.group_membership;
  },

  // Check if user belongs to a specific city catalog
  belongsToCityGroup(cityName) {
    if (!cityName) return false;
    
    const userInfo = this.getUserInfo();
    if (!userInfo || !userInfo.group_membership) {
      return false;
    }
    
    const normalizedCityName = cityName.toLowerCase();
    const cityGroup = `/${normalizedCityName}-catalog`;
    
    return userInfo.group_membership.includes(cityGroup);
  },

  // Update token
  async updateToken(minValidity = 5) {
    if (!keycloak?.authenticated) {
      return false;
    }

    try {
      return await keycloak.updateToken(minValidity);
    } catch (error) {
      console.error('Token update failed:', error);
      return false;
    }
  },

  // Handle callback (for compatibility, but Keycloak JS handles this automatically)
  async handleCallback() {
    // This is handled automatically by Keycloak JS
    const redirectPath = sessionStorage.getItem('postLoginRedirect') || '/';
    sessionStorage.removeItem('postLoginRedirect');
    
    // Dispatch success event
    window.dispatchEvent(new CustomEvent('keycloak-login-success'));
    
    return redirectPath;
  }
};

// Create fetch wrapper with automatic token handling
export const authFetch = async (url, options = {}) => {
  try {
    const token = await authService.getAccessToken();
    const headers = {
      ...options.headers,
      ...(token && { Authorization: `Bearer ${token}` })
    };

    return fetch(url, {
      ...options,
      headers
    });
  } catch (error) {
    console.error('Error in authFetch:', error);
    throw error;
  }
};