# Authentication System Migration

## Overview
The frontend has been migrated to use Keycloak-js directly for authentication, providing a more robust and secure authentication flow.

## Key Changes

### 1. New Authentication Service
- The `authService` now uses `keycloak-js` library directly
- Provides automatic token refresh
- Better error handling and security

### 2. Authentication Composable
- New `useAuth()` composable provides reactive authentication state
- Can be used in any Vue component for authentication-related functionality
- Automatically manages authentication state across the application

### 3. Component Updates
All components have been updated to use the new authentication system:
- `ClimaboroughHeader.vue` - Uses auth composable for user state
- `AuthRequired.vue` - Updated to use reactive authentication
- `LoginForm.vue` - Simplified to use Keycloak directly
- `Dashboard.vue` - Uses auth composable for user permissions
- `Projects.vue` - Updated user type and city detection
- `DataCatalogue.vue` - Uses auth composable for API calls
- `DashboardChat.vue` - Updated for token management

### 4. Router Updates
- Improved navigation guards
- Better handling of post-login redirects
- Automatic authentication state events

## Environment Variables Required

Create a `.env` file with the following variables:

```env
VITE_KEYCLOAK_URL=https://your-keycloak-server.com
VITE_KEYCLOAK_REALM=your-realm
VITE_CLIENT_ID=your-client-id
VITE_ENV=development
```

## Usage

### In Vue Components

```javascript
import { useAuth } from '@/composables/useAuth';

export default {
  setup() {
    const auth = useAuth();
    
    // Check if user is authenticated
    const isLoggedIn = auth.isAuthenticated;
    
    // Get user information
    const user = auth.userInfo;
    const userType = auth.userType;
    const userCity = auth.userCity;
    
    // Login/logout
    const login = () => auth.login('/redirect-path');
    const logout = () => auth.logout();
    
    // Check permissions
    const hasRole = auth.hasRole('admin');
    
    // Get access token for API calls
    const makeAuthenticatedRequest = async () => {
      const token = await auth.getAccessToken();
      // Use token in API calls
    };
    
    return {
      isLoggedIn,
      user,
      userType,
      userCity,
      login,
      logout,
      hasRole
    };
  }
};
```

### Authentication Flow

1. **Initialization**: Keycloak is initialized in `App.vue` on application start
2. **Silent Check**: Automatically checks if user is already authenticated
3. **Login**: Redirects to Keycloak login page when needed
4. **Token Management**: Automatically refreshes tokens when needed
5. **Logout**: Clears all authentication state and redirects

### Silent Check SSO

The application includes a `silent-check-sso.html` file for seamless authentication checks. This allows the application to verify authentication status without redirecting the user to the login page.

## Security Features

- **PKCE**: Uses Proof Key for Code Exchange for enhanced security
- **Automatic Token Refresh**: Tokens are automatically refreshed before expiration
- **Secure Storage**: No tokens stored in localStorage (handled by Keycloak-js)
- **CSRF Protection**: Built-in protection against cross-site request forgery

## Migration Notes

- Old localStorage-based authentication is automatically cleaned up
- All components have been updated to use the new authentication system
- The authentication service is backward compatible with existing API calls
- No changes needed to backend authentication validation

## Troubleshooting

### Third-Party Cookie/Iframe Issues

If you encounter errors like:
```
The loading of "https://auth.climaplatform.eu/realms/climaborough/protocol/openid-connect/3p-cookies/step1.html" in a frame is denied by "X-Frame-Options" directive set to "sameorigin".
Failed to initialize Keycloak: Object { error: "Timeout when waiting for 3rd party check iframe message." }
```

**Solution:** The authentication system has been configured to handle this automatically by:
1. Disabling problematic iframe checks (`checkLoginIframe: false`)
2. Providing fallback initialization strategies
3. Graceful error handling that allows the app to continue functioning

**What this means:**
- The app will work normally but may require manual login
- SSO (Single Sign-On) checks may not work automatically
- Users can still authenticate by clicking the login button

This is a common issue with modern browsers' security policies and doesn't affect the core functionality.

## Testing

After migration, verify:
1. Login flow works correctly
2. Protected routes are properly secured
3. User permissions are correctly applied
4. Token refresh works automatically
5. Logout clears all authentication state
6. App handles authentication errors gracefully
