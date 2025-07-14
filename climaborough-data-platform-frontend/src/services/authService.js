// Authentication service for managing Keycloak interactions using keycloak-js
import Keycloak from 'keycloak-js';
import config from '../config/env.js';

// Validation for required environment variables
if (!config.keycloak.url) {
  console.warn('KEYCLOAK_URL not set, using fallback');
}
if (!config.keycloak.clientId) {
  console.warn('CLIENT_ID not set, using fallback');
}

// Initialize Keycloak instance
let keycloak = null;

const initKeycloak = () => {
  if (!keycloak) {
    keycloak = new Keycloak({
      url: config.keycloak.url || 'https://localhost:8080',
      realm: config.keycloak.realm || 'master',
      clientId: config.keycloak.clientId || 'your-client-id'
    });
  }
  return keycloak;
};

export const authService = {
  // Initialize Keycloak with fallback strategies
  async init(options = {}) {
    const kc = initKeycloak();
    
    // Primary initialization strategy
    const initOptions = {
      onLoad: options.onLoad || 'check-sso',
      checkLoginIframe: false, // Disable iframe checking to avoid X-Frame-Options issues
      enableLogging: true, // Enable logging for debugging
      pkceMethod: 'S256', // Use PKCE for security
      flow: 'standard', // Use standard flow
      responseMode: 'fragment', // Use fragment response mode
      checkLoginIframeInterval: 0, // Disable periodic iframe checks
      silentCheckSsoFallback: false, // Disable fallback that might cause issues
      ...options
    };
    
    try {
      // console.log('Initializing Keycloak with options:', initOptions);
      const authenticated = await kc.init(initOptions);
      
      // Set up token refresh
      this.setupTokenRefresh();
      
      // console.log('Keycloak initialized successfully, authenticated:', authenticated);
      return authenticated;
    } catch (error) {
      console.error('Primary Keycloak initialization failed:', error);
      
      // Fallback strategy: try with minimal options
      if (error.error && (error.error.includes('iframe') || error.error.includes('3rd party'))) {
        console.log('Attempting fallback initialization without SSO check...');
        
        try {
          const fallbackAuthenticated = await kc.init({
            onLoad: 'login-required', // Force login if needed
            checkLoginIframe: false,
            enableLogging: true,
            pkceMethod: 'S256',
            flow: 'standard',
            responseMode: 'fragment'
          });
          
          this.setupTokenRefresh();
          // console.log('Fallback Keycloak initialization successful');
          return fallbackAuthenticated;
        } catch (fallbackError) {
          console.error('Fallback initialization also failed:', fallbackError);
          throw fallbackError;
        }
      } else {
        throw error;
      }
    }
  },

  // Setup automatic token refresh
  setupTokenRefresh() {
    const kc = initKeycloak();
    
    kc.onTokenExpired = () => {
      this.refreshToken().catch((error) => {
        console.error('Failed to refresh token:', error);
        this.logout();
      });
    };
  },

  // Get current authentication status
  isAuthenticated() {
    const kc = initKeycloak();
    return kc.authenticated || false;
  },

  // Get user info from token
  getUserInfo() {
    const kc = initKeycloak();
    if (!kc.authenticated) return null;
    
    return {
      ...kc.tokenParsed,
      name: kc.tokenParsed?.name || kc.tokenParsed?.preferred_username,
      email: kc.tokenParsed?.email,
      username: kc.tokenParsed?.preferred_username,
      group_membership: kc.tokenParsed?.group_membership || []
    };
  },

  // Initiate login process
  login(redirectPath = '/') {
    const kc = initKeycloak();
    
    // Store the intended destination for after login
    sessionStorage.setItem('postLoginRedirect', redirectPath);
    
    return kc.login({
      redirectUri: window.location.origin + (redirectPath === '/' ? '' : redirectPath)
    });
  },

  // Handle callback from Keycloak after login (this is handled automatically by keycloak-js)
  async handleCallback() {
    // This method is kept for compatibility but keycloak-js handles callbacks automatically
    const redirectPath = sessionStorage.getItem('postLoginRedirect') || '/';
    sessionStorage.removeItem('postLoginRedirect');
    
    return redirectPath;
  },

  // Logout from Keycloak
  logout() {
    const kc = initKeycloak();
    
    // Clear post login redirect
    sessionStorage.removeItem('postLoginRedirect');
    
    return kc.logout({
      redirectUri: window.location.origin
    });
  },

  // Refresh the token
  async refreshToken() {
    const kc = initKeycloak();
    
    try {
      const refreshed = await kc.updateToken(30); // Refresh if token expires in 30 seconds
      if (refreshed) {
        // console.log('Token refreshed successfully');
      }
      return refreshed;
    } catch (error) {
      console.error('Failed to refresh token:', error);
      throw error;
    }
  },

  // Get the current access token
  async getAccessToken() {
    const kc = initKeycloak();
    
    if (!kc.authenticated) {
      throw new Error('Not authenticated');
    }
    
    // Ensure token is fresh
    await kc.updateToken(30);
    return kc.token;
  },

  // Get user roles/permissions
  getUserRoles() {
    const kc = initKeycloak();
    if (!kc.authenticated) return [];
    
    const realmRoles = kc.realmAccess?.roles || [];
    const clientRoles = Object.values(kc.resourceAccess || {}).flatMap(client => client.roles || []);
    const groupMembership = kc.tokenParsed?.group_membership || [];
    
    return [...realmRoles, ...clientRoles, ...groupMembership];
  },

  // Check if user has specific role
  hasRole(role) {
    const kc = initKeycloak();
    if (!kc.authenticated) return false;
    
    return kc.hasRealmRole(role) || kc.hasResourceRole(role) || this.getUserRoles().includes(role);
  },

  // Check if user belongs to a city group
  getUserCity() {
    const userInfo = this.getUserInfo();
    if (!userInfo) return null;
    
    const cityGroup = userInfo.group_membership?.find(group => group.startsWith('/City/'));
    return cityGroup ? cityGroup.split('/').pop() : null;
  },

  // Get the Keycloak instance (for advanced usage)
  getKeycloakInstance() {
    return initKeycloak();
  },

  // Clean up (for compatibility with old implementation)
  cleanupLocalStorage() {
    localStorage.removeItem('keycloak_token');
    localStorage.removeItem('keycloak_refresh_token');
    localStorage.removeItem('keycloak_expires_at');
    localStorage.removeItem('userType');
  }
};

// Create fetch wrapper for automatic token handling
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