<script setup>
import { ref } from 'vue';
import { authService } from '../../services/authService';

const emit = defineEmits(['login-complete', 'login-cancel']);

const loading = ref(false);
const errorMessage = ref('');

const loginWithKeycloak = () => {
  loading.value = true;
  errorMessage.value = '';
  
  try {
    authService.login();
  } catch (error) {
    console.error('Login error:', error);
    errorMessage.value = 'Unable to initiate login. Please try again.';
    loading.value = false;
  }
};
</script>

<template>
  <div class="login-form">
    <h2>{{ $t('login.title') }}</h2>
    <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
    
    <div class="login-options">
      <v-btn 
        color="primary" 
        class="keycloak-button" 
        @click="loginWithKeycloak"
        :loading="loading"
      >
        {{ $t('login.sign_in') }}
      </v-btn>
      
      <v-btn 
        text 
        @click="$emit('login-cancel')" 
        class="cancel-button"
      >
        {{ $t('login.cancel') }}
      </v-btn>
    </div>
  </div>
</template>

<style scoped>
.login-form {
  padding: 24px;
  border-radius: 8px;
  max-width: 400px;
  width: 100%;
}

h2 {
  margin-top: 0;
  margin-bottom: 24px;
  color: #0177a9;
  text-align: center;
}

.login-options {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-top: 24px;
}

.keycloak-button {
  background-color: #0177a9 !important;
  color: white !important;
  width: 100%;
  padding: 12px !important;
  font-weight: bold;
}

.cancel-button {
  color: #666;
  width: 100%;
}

.error-message {
  color: #f44336;
  margin-bottom: 16px;
  text-align: center;
}
</style>