<template>
  <div class="login-page">
    <div class="login-container">
      <div class="login-card">
        <div class="login-header">
          <img 
            src="/climaborough-logo-white.png" 
            alt="Climaborough" 
            class="logo"
          />
          <h1>{{ $t('login.welcome') || 'Welcome to Climaborough' }}</h1>
          <p>{{ $t('login.description') || 'Access your personalized climate data platform' }}</p>
        </div>
        
        <div class="login-content">
          <div v-if="errorMessage" class="error-message">
            <v-alert type="error" variant="tonal">
              {{ errorMessage }}
            </v-alert>
          </div>
          
          <v-btn 
            color="primary" 
            size="large"
            @click="handleLogin"
            :loading="loginLoading"
            class="login-button"
            block
          >
            <v-icon left>mdi-login</v-icon>
            {{ $t('login.sign_in') || 'Sign In with Keycloak' }}
          </v-btn>
          
          <div class="login-footer">
            <p>{{ $t('login.secure_auth') || 'Secure authentication provided by Keycloak' }}</p>
            <v-btn 
              variant="text" 
              @click="goHome"
              class="home-link"
            >
              {{ $t('login.back_home') || '← Back to Home' }}
            </v-btn>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { authService } from '../services/authService';

const router = useRouter();
const route = useRoute();
const loginLoading = ref(false);
const errorMessage = ref('');

// Check for error parameters in URL
onMounted(() => {
  const urlParams = new URLSearchParams(window.location.search);
  const error = urlParams.get('error');
  
  if (error === 'oauth_error') {
    errorMessage.value = 'Authentication failed. Please try again.';
  } else if (error === 'auth_failed') {
    errorMessage.value = 'Login process failed. Please try again.';
  }
  
  // Check if user is already authenticated
  if (authService.isAuthenticated()) {
    const redirectPath = sessionStorage.getItem('postLoginRedirect') || '/projects';
    sessionStorage.removeItem('postLoginRedirect');
    router.push(redirectPath);
  }
});

const handleLogin = () => {
  loginLoading.value = true;
  errorMessage.value = '';
  
  try {
    // Get the intended destination
    const redirectPath = sessionStorage.getItem('postLoginRedirect') || '/projects';
    authService.login(redirectPath);
  } catch (error) {
    console.error('Login error:', error);
    errorMessage.value = 'Unable to initiate login. Please try again.';
    loginLoading.value = false;
  }
};

const goHome = () => {
  router.push('/');
};
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #0177a9 0%, #025a80 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.login-container {
  width: 100%;
  max-width: 480px;
}

.login-card {
  background: white;
  border-radius: 20px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.login-header {
  background: linear-gradient(135deg, #0177a9 0%, #025a80 100%);
  color: white;
  padding: 48px 32px;
  text-align: center;
}

.logo {
  height: 60px;
  margin-bottom: 24px;
  filter: brightness(0) invert(1);
}

.login-header h1 {
  font-size: 1.8rem;
  font-weight: 600;
  margin-bottom: 12px;
}

.login-header p {
  opacity: 0.9;
  font-size: 1.1rem;
}

.login-content {
  padding: 48px 32px;
}

.error-message {
  margin-bottom: 24px;
}

.login-button {
  background: linear-gradient(45deg, #0177a9, #025a80) !important;
  color: white !important;
  font-weight: 600;
  padding: 16px !important;
  border-radius: 12px;
  margin-bottom: 32px;
}

.login-button:hover {
  background: linear-gradient(45deg, #025a80, #0177a9) !important;
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(1, 119, 169, 0.3);
}

.login-footer {
  text-align: center;
  border-top: 1px solid #f0f0f0;
  padding-top: 24px;
}

.login-footer p {
  color: #666;
  font-size: 0.9rem;
  margin-bottom: 16px;
}

.home-link {
  color: #0177a9 !important;
  text-decoration: none;
}

@media (max-width: 600px) {
  .login-header, .login-content {
    padding: 32px 24px;
  }
  
  .login-header h1 {
    font-size: 1.5rem;
  }
  
  .logo {
    height: 50px;
  }
}
</style>
