<template>
  <div class="auth-required-container">
    <!-- Always show content -->
    <slot />
    
    <!-- Show modal overlay if not authenticated -->
    <v-dialog 
      v-model="showAuthModal" 
      persistent 
      max-width="500"
      :overlay-opacity="0.8"
    >
      <v-card class="auth-modal-card">
        <v-card-title class="auth-modal-header">
          <v-icon color="primary" size="large" class="mr-3">mdi-lock</v-icon>
          <span>{{ $t('auth.access_required') || 'Authentication Required' }}</span>
        </v-card-title>
        
        <v-card-text class="auth-modal-content">
          <p class="text-body-1 mb-4">
            {{ $t('auth.please_login') || 'Please log in to access this page.' }}
          </p>
        </v-card-text>
        
        <v-card-actions class="auth-modal-actions">
          <v-btn 
            color="primary" 
            size="large"
            @click="handleLogin"
            :loading="loginLoading"
            class="login-button flex-grow-1"
          >
            <v-icon left>mdi-login</v-icon>
            {{ $t('login.title') || 'Sign In' }}
          </v-btn>
          
          <v-btn 
            variant="outlined" 
            @click="goHome"
            class="home-button"
          >
            <v-icon left>mdi-home</v-icon>
            {{ $t('auth.go_home') || 'Home' }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { authService } from '../services/authService';

const router = useRouter();
const route = useRoute();
const loginLoading = ref(false);

// Reactive authentication status
const isAuthenticated = computed(() => authService.isAuthenticated());

// Control modal visibility
const showAuthModal = ref(!isAuthenticated.value);

// Watch authentication status and update modal visibility
watch(isAuthenticated, (newValue) => {
  showAuthModal.value = !newValue;
}, { immediate: true });

const handleLogin = () => {
  loginLoading.value = true;
  try {
    // Store current path for redirect after login
    const currentPath = route.fullPath;
    authService.login(currentPath);
  } catch (error) {
    console.error('Login error:', error);
    loginLoading.value = false;
  }
};

const goHome = () => {
  router.push('/');
};
</script>

<style scoped>
.auth-required-container {
  position: relative;
}

.auth-modal-card {
  border-radius: 16px !important;
  overflow: hidden;
}

.auth-modal-header {
  background: linear-gradient(135deg, #0177a9 0%, #025a80 100%);
  color: white !important;
  padding: 24px;
  text-align: center;
  
  .v-card-title {
    justify-content: center;
    font-size: 1.3rem;
    font-weight: 600;
  }
}

.auth-modal-content {
  padding: 32px 24px 16px 24px;
  text-align: center;
  
  p {
    color: #666;
    font-size: 1.1rem;
    line-height: 1.5;
    margin: 0;
  }
}

.auth-modal-actions {
  padding: 16px 24px 24px 24px;
  flex-direction: column;
  gap: 12px;
}

.login-button {
  background: linear-gradient(45deg, #0177a9, #025a80) !important;
  color: white !important;
  font-weight: 600;
  padding: 12px 32px !important;
  border-radius: 8px;
  min-height: 48px;
}

.login-button:hover {
  background: linear-gradient(45deg, #025a80, #0177a9) !important;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(1, 119, 169, 0.3);
}

.home-button {
  color: #666 !important;
  border-color: #ddd !important;
  min-height: 44px;
}

.home-button:hover {
  background-color: #f5f5f5 !important;
  border-color: #bbb !important;
}

/* Vuetify dialog overlay customization */
:deep(.v-overlay__scrim) {
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(4px);
}
</style>
