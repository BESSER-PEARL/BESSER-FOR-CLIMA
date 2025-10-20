// Environment configuration helper
const requiredEnvVars = [
  'VITE_KEYCLOAK_URL',
  'VITE_KEYCLOAK_REALM',
  'VITE_CLIENT_ID'
];

const config = {
  keycloak: {
    url: import.meta.env.VITE_KEYCLOAK_URL,
    realm: import.meta.env.VITE_KEYCLOAK_REALM,
    clientId: import.meta.env.VITE_CLIENT_ID
  },
  environment: import.meta.env.VITE_ENV || 'development',
  isDevelopment: (import.meta.env.VITE_ENV || 'development') === 'development',
  isProduction: (import.meta.env.VITE_ENV || 'development') === 'production'
};

// Validate required environment variables
const validateEnv = () => {
  const missing = requiredEnvVars.filter(envVar => !import.meta.env[envVar]);
  
  if (missing.length > 0) {
    console.error('Missing required environment variables:', missing);
    if (config.isProduction) {
      throw new Error(`Missing required environment variables: ${missing.join(', ')}`);
    }
  }
};

validateEnv();

export default config;
