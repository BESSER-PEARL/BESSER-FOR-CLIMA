<script setup>
import { onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { authService } from '../services/authService';

const router = useRouter();

onMounted(async () => {
  const urlParams = new URLSearchParams(window.location.search);
  const code = urlParams.get('code');
  const state = urlParams.get('state');
  const error = urlParams.get('error');
  
  // Handle OAuth error
  if (error) {
    console.error('OAuth error:', error, urlParams.get('error_description'));
    router.push('/?error=oauth_error');
    return;
  }
  
  if (code) {
    try {
      // Use the authService to handle the callback with state validation
      await authService.handleCallback(code, state);
      
      // Dispatch event for other components
      window.dispatchEvent(new Event('keycloak-login-success'));
      
      // Redirect to intended destination or home
      const redirectPath = sessionStorage.getItem('postLoginRedirect') || '/';
      sessionStorage.removeItem('postLoginRedirect');
      router.push(redirectPath);
    } catch (error) {
      console.error('Error during authentication:', error);
      router.push('/?error=auth_failed');
    }
  } else {
    router.push('/');
  }
});
</script>

<template>
  <div class="callback-container">
    <v-progress-circular
      indeterminate
      color="primary"
    ></v-progress-circular>
    <p>Completing authentication...</p>
  </div>
</template>

<style scoped>
.callback-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100vh;
  gap: 20px;
}
</style> 