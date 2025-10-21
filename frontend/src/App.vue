<script setup>
import ClimaboroughHeader from "./components/ClimaboroughHeader.vue"
import Footer from "./components/Footer.vue"
import { RouterView } from 'vue-router'
import { Icon } from "@iconify/vue";
import { onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import { authService } from './services/authService';

const router = useRouter();
const isInitializing = ref(true);
const initError = ref(null);

onMounted(async () => {
  try {
    //console.log('Starting authentication initialization...');
    
    // Initialize Keycloak with robust error handling
    const authenticated = await authService.init({
      onLoad: 'check-sso' // This will fallback to login-required if SSO check fails
    });
    
    // Clean up any old localStorage tokens
    authService.cleanupLocalStorage();
    
    //console.log('Authentication initialized, user authenticated:', authenticated);
    
    // Handle post-login redirect if user was authenticated during init
    if (authenticated) {
      const redirectPath = sessionStorage.getItem('postLoginRedirect');
      if (redirectPath) {
        sessionStorage.removeItem('postLoginRedirect');
        //console.log('Redirecting to:', redirectPath);
        router.push(redirectPath);
      }
      
      // Emit login success event for components to react to
      window.dispatchEvent(new CustomEvent('keycloak-login-success'));
    }
    
  } catch (error) {
    console.error('Failed to initialize authentication:', error);
    
    // More specific error handling
    if (error.error && (error.error.includes('iframe') || error.error.includes('3rd party'))) {
      console.warn('Third-party cookie/iframe issue detected. Authentication will work but manual login may be required.');
      initError.value = 'Authentication system loaded. Please log in to access protected features.';
    } else {
      initError.value = error.message || 'Authentication initialization failed';
    }
  } finally {
    isInitializing.value = false;
    //console.log('Authentication initialization complete');
  }
});

</script>

<template>
  <div class="app-container">
    <!-- Loading state during Keycloak initialization -->
    <div v-if="isInitializing" class="loading-container">
      <div class="loading-spinner"></div>
      <p>Initializing authentication...</p>
    </div>
    
    <!-- Error state -->
    <div v-else-if="initError" class="error-container">
      <div class="error-content">
        <h2>Authentication Notice</h2>
        <p>{{ initError }}</p>
        <div class="error-actions">
          <button @click="() => window.location.reload()" class="retry-button">
            Retry
          </button>
          <button @click="() => { initError = null; isInitializing = false; }" class="continue-button">
            Continue to App
          </button>
        </div>
      </div>
    </div>
    
    <!-- Main app -->
    <template v-else>
      <ClimaboroughHeader />
      <router-view></router-view>
      <Footer />
    </template>
  </div>
</template>

<style>
.app-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

body {
  margin: 0;
  padding: 0;
  overflow-x: hidden;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  gap: 1rem;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #3498db;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  padding: 2rem;
  text-align: center;
}

.error-content {
  max-width: 500px;
  padding: 2rem;
  border-radius: 8px;
  background: #f8f9fa;
  border: 1px solid #e9ecef;
}

.error-content h2 {
  color: #0177a9;
  margin-bottom: 1rem;
}

.error-content p {
  color: #6c757d;
  margin-bottom: 2rem;
  line-height: 1.5;
}

.error-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
}

.retry-button,
.continue-button {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
  transition: background-color 0.2s;
}

.retry-button {
  background-color: #0177a9;
  color: white;
}

.retry-button:hover {
  background-color: #025a80;
}

.continue-button {
  background-color: #aec326;
  color: white;
}

.continue-button:hover {
  background-color: #8ca01e;
}
</style>