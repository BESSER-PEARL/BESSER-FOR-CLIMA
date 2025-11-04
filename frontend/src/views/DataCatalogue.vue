<template>
  <AuthRequired>
    <div class="data-catalogue">
      <!-- <h1>Data Catalogue</h1> -->
      <div class="iframe-container" :class="{ fullscreen: isFullscreen }">
        <iframe 
          :src="dashboardUrl"
          title="Data Catalogue"
          allow="fullscreen"
          class="dashboard-iframe"
          ref="dataIframe"
          sandbox="allow-same-origin allow-scripts allow-forms allow-popups allow-downloads allow-storage-access-by-user-activation">
        </iframe>
      </div>
      <!-- Optional fullscreen toggle -->
      <!--
      <div class="controls">
        <button @click="toggleFullscreen" class="control-button">Toggle Fullscreen</button>
      </div>
      -->
    </div>
  </AuthRequired>
</template>


<script setup>
import { ref, onMounted } from 'vue';
import { authService } from '../services/authService';
import { useAuth } from '../composables/useAuth';

const auth = useAuth();
import AuthRequired from '../components/AuthRequired.vue';

const dashboardUrl = ref('https://ui.climaplatform.eu/app/data-catalog?embed=true');
const isFullscreen = ref(false);
const dataIframe = ref(null);

const toggleFullscreen = () => {
  isFullscreen.value = !isFullscreen.value;
};

onMounted(async () => {
  if (!auth.isAuthenticated.value) {
    console.warn("User not authenticated, consider redirecting to login");
    return;
  }

  try {
    const token = await auth.getAccessToken();
    
    // Optionally pass token to iframe via postMessage
    const message = {
      type: 'AUTH_TOKEN',
      token,
    };

    const sendMessageToIframe = () => {
      const iframe = dataIframe.value;
      if (iframe && iframe.contentWindow) {
        iframe.contentWindow.postMessage(message, 'https://ui.climaplatform.eu');
      }
    };

    // Wait a bit to ensure iframe loads
    setTimeout(sendMessageToIframe, 1500);
  } catch (error) {
    console.error("Error getting access token:", error);
  }

  // Listen for messages from the iframe (e.g., for CMP data)
  window.addEventListener('message', (event) => {
    if (event.origin !== 'https://ui.climaplatform.eu') return;

    const { type, data } = event.data;
    //console.log("Message from iframe:", type, data);

    if (type === 'CMP_ERROR') {
      console.warn('Consent data error:', data);
    }
  });
});
</script>


<style scoped>
.data-catalogue {
  width: 100%;
  height: 100%;
  padding: 20px;
}

.iframe-container {
  width: 100%;
  height: calc(100vh - 200px);
  overflow: hidden;
  border-radius: 8px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.iframe-container.fullscreen {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  z-index: 9999;
  border-radius: 0;
}

.dashboard-iframe {
  width: 100%;
  height: 100%;
  border: none;
}

.controls {
  margin-top: 15px;
  display: flex;
  justify-content: center;
}

.control-button {
  background-color: #0177a9;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
  transition: background-color 0.2s;
}

.control-button:hover {
  background-color: #015a80;
}
</style>