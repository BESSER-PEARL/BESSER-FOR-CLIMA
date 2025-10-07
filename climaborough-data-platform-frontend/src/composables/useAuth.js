// Authentication composable for Vue 3 
// Provides reactive authentication state and methods
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { authService } from '../services/authService';

// Global reactive state
const isAuthenticated = ref(false);
const userInfo = ref(null);
const isInitialized = ref(false);

// Update authentication state
const updateAuthState = () => {
  isAuthenticated.value = authService.isAuthenticated();
  userInfo.value = authService.getUserInfo();
};

// Initialize authentication state
const initAuthState = () => {
  updateAuthState();
  isInitialized.value = true;
};

export const useAuth = () => {
  // Event handlers
  const handleAuthSuccess = () => {
    updateAuthState();
  };

  const handleAuthLogout = () => {
    isAuthenticated.value = false;
    userInfo.value = null;
  };

  // Computed properties
  const userType = computed(() => {
    if (!userInfo.value || !userInfo.value.group_membership) return null;
    
    const groups = userInfo.value.group_membership;
    
    // Check for administrator roles
    if (groups.includes('/Administrator') || groups.includes('/Super-Administrator')) {
      return 'admin';
    }
    
    // Check for city-specific catalog groups (e.g., /athens-catalog, /cascais-catalog)
    if (groups.some(group => group.endsWith('-catalog'))) {
      return 'cityuser';
    }
    
    return null;
  });

  const userCity = computed(() => {
    if (!userInfo.value || !userInfo.value.group_membership) return null;
    
    const groups = userInfo.value.group_membership;
    
    // Find city catalog group (e.g., /athens-catalog -> athens)
    const cityGroup = groups.find(group => group.endsWith('-catalog'));
    
    if (cityGroup) {
      // Extract city name from group path (e.g., /athens-catalog -> athens)
      const cityName = cityGroup.replace(/^\//, '').replace(/-catalog$/, '');
      
      // Capitalize first letter for proper city name
      return cityName.charAt(0).toUpperCase() + cityName.slice(1);
    }
    
    return null;
  });

  // Methods
  const login = (redirectPath = '/') => {
    return authService.login(redirectPath);
  };

  const logout = () => {
    return authService.logout();
  };

  const hasRole = (role) => {
    return authService.hasRole(role);
  };

  const getUserRoles = () => {
    return authService.getUserRoles();
  };

  const getAccessToken = async () => {
    return await authService.getAccessToken();
  };

  // Lifecycle
  onMounted(() => {
    if (!isInitialized.value) {
      initAuthState();
    }
    
    // Set up event listeners
    window.addEventListener('keycloak-login-success', handleAuthSuccess);
    window.addEventListener('keycloak-logout', handleAuthLogout);
    
    // Periodic auth state check
    const authCheckInterval = setInterval(updateAuthState, 30000); // Check every 30 seconds
    
    // Cleanup on unmount
    onUnmounted(() => {
      window.removeEventListener('keycloak-login-success', handleAuthSuccess);
      window.removeEventListener('keycloak-logout', handleAuthLogout);
      clearInterval(authCheckInterval);
    });
  });

  return {
    // State
    isAuthenticated: computed(() => isAuthenticated.value),
    userInfo: computed(() => userInfo.value),
    userType,
    userCity,
    isInitialized: computed(() => isInitialized.value),
    
    // Methods
    login,
    logout,
    hasRole,
    getUserRoles,
    getAccessToken,
    updateAuthState
  };
};

// Export global state for direct access if needed
export const authState = {
  isAuthenticated: computed(() => isAuthenticated.value),
  userInfo: computed(() => userInfo.value),
  isInitialized: computed(() => isInitialized.value)
};
