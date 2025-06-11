<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue';
import { RouterLink, useRoute, useRouter } from 'vue-router';
import { useI18n } from 'vue-i18n';
import LoginForm from './forms/LoginForm.vue';
import { authService } from '../services/authService';

const { locale } = useI18n();
const route = useRoute();
const router = useRouter();

locale.value = "en"

const loginBool = ref(false)
const name = ref("")
const city = ref("");
const userType = ref("");
const loggedIn = ref(false)

const checkIfLogged = () => {
  loggedIn.value = authService.isAuthenticated();
  
  if (loggedIn.value) {
    const userInfo = authService.getUserInfo();
    if (userInfo) {
      name.value = userInfo.name || userInfo.preferred_username;
      city.value = authService.getUserCity() || "";
      // Determine user type from group membership
      if (userInfo.group_membership?.includes('/Administrator')) {
        userType.value = "admin";
      } else if (userInfo.group_membership?.some(group => group.startsWith('/City/'))) {
        userType.value = "cityuser";
      } else {
        userType.value = "";
      }
    }
  } else {
    name.value = "";
    city.value = "";
    userType.value = "";
  }
}

// Navigation handler that checks authentication before navigating
const handleNavigation = (path) => {
  const protectedRoutes = ['/projects', '/bot', '/datacatalogue'];
  
  if (protectedRoutes.includes(path) && !authService.isAuthenticated()) {
    // Don't navigate, just show login popup
    loginBool.value = true;
    return;
  }
  
  // If authenticated or route is not protected, navigate normally
  router.push(path);
  closeMobileMenu();
}

const logout = () => {
  authService.logout();
}

const toggleLogin = () => {
  loginBool.value = !loginBool.value
}

const selectedLanguage = ref('en') // Default language
const languages = ref(
  [{
    "iso639": "en",
    "name": "English",
    "flag": "openmoji:flag-england"
  },
  {
    "iso639": "it",
    "name": "Italiano",
    "flag": "openmoji:flag-italy"
  },
  {
    "iso639": "fr",
    "name": "Français",
    "flag": "openmoji:flag-france"
  },
  {
    "iso639": "lb",
    "name": "Lëtzebuergesch",
    "flag": "openmoji:flag-luxembourg"  },
  {
    "iso639": "sl",
    "name": "Slovenščina",
    "flag": "openmoji:flag-slovenia"
  },
  {
    "iso639": "el",
    "name": "Ελληνικά",
    "flag": "openmoji:flag-greece"
  },
  {
    "iso639": "pl",
    "name": "Polski",
    "flag": "openmoji:flag-poland"
  },
  {
    "iso639": "sr",
    "name": "Crnogorski",
    "flag": "openmoji:flag-montenegro"
  },
  {
    "iso639": "cs",
    "name": "Čeština",
    "flag": "openmoji:flag-czechia"
  },
  {
    "iso639": "bs",
    "name": "Bosanski",
    "flag": "openmoji:flag-bosnia-and-herzegovina"
  },
  {
    "iso639": "bg",
    "name": "Български",
    "flag": "openmoji:flag-bulgaria"
  },
  ]
)
function getLanguage() {
  var lang = localStorage.getItem("lang")
  if (lang != null) {
    selectedLanguage.value = lang.toLowerCase()
    locale.value = lang.toLowerCase()
  }
}
getLanguage()

const setLanguage = (language) => {
  selectedLanguage.value = language.toLowerCase();
  localStorage.setItem("lang", selectedLanguage.value)
  locale.value = selectedLanguage.value
}

const closeMobileMenu = () => {
  isMobileMenuOpen.value = false
}

// Login polling and Keycloak redirect check
let loginCheckInterval = null;

const handleKeycloakLoginSuccess = () => {
  // This will be called when the Keycloak login is successful
  checkIfLogged();
};

onMounted(() => {
  checkIfLogged();
  window.addEventListener('storage', handleStorageChange);
  window.addEventListener('keycloak-login-success', handleKeycloakLoginSuccess);
  
  // Check for token on initial load and every few seconds
  const urlParams = new URLSearchParams(window.location.search);
  if (urlParams.has('state') && (urlParams.has('session_state') || urlParams.has('code'))) {
    // This looks like a Keycloak redirect, start polling for token
    startLoginCheck();
  }
});

onUnmounted(() => {
  window.removeEventListener('storage', handleStorageChange);
  window.removeEventListener('keycloak-login-success', handleKeycloakLoginSuccess);
  stopLoginCheck();
});

// Start polling for token after potential login
const startLoginCheck = () => {
  // First check immediately
  checkIfLogged();
  
  // Then check every 1 second for 10 seconds
  stopLoginCheck(); // Clear any existing interval
  
  loginCheckInterval = setInterval(() => {
    // Check if user is now authenticated (using cookies)
    if (authService.isAuthenticated()) {
      checkIfLogged();
      stopLoginCheck();
    }
  }, 1000);
  
  // Stop checking after 10 seconds regardless
  setTimeout(stopLoginCheck, 10000);
};

const stopLoginCheck = () => {
  if (loginCheckInterval) {
    clearInterval(loginCheckInterval);
    loginCheckInterval = null;
  }
};

// Manually refresh user info when LoginForm completes
const handleLoginComplete = () => {
  checkIfLogged();
  loginBool.value = false;
};

// Re-check login status when route changes
watch(() => route.path, () => {
  checkIfLogged();
});

const menu = ref(false)
const isMobileMenuOpen = ref(false)

const toggleMobileMenu = () => {
  isMobileMenuOpen.value = !isMobileMenuOpen.value
}

const handleStorageChange = (event) => {
  // Since we're using cookies now, we don't need to listen for localStorage changes
  // But we can listen for cookie changes indirectly through periodic checks
  if (event.key === 'keycloak_token') {
    checkIfLogged();
  }
};

</script>

<template>
  <div>
    <header>
      <nav class="container">
        <div class="branding">
          <RouterLink to="/"><img class="logo" src="../assets/clima.png" alt=""> </RouterLink>
        </div>
        
        <!-- Add hamburger menu button -->
        <div class="mobile-menu-button" @click="toggleMobileMenu">
          <Icon :icon="isMobileMenuOpen ? 'mdi:close' : 'mdi:menu'" width="30" height="30" />
        </div>

        <ul class="nav-routes" :class="{ 'mobile-menu-active': isMobileMenuOpen }">
          <RouterLink @click="closeMobileMenu" to="/">{{ $t('header.home') }}</RouterLink>
          <!-- <RouterLink @click="closeMobileMenu" to="/demo">DEMO Dashboard</RouterLink> -->
          <a @click="handleNavigation('/projects')" class="nav-link">Dashboard</a>
          <a @click="handleNavigation('/bot')" class="nav-link">ClimaBot</a>
          <a @click="handleNavigation('/datacatalogue')" class="nav-link">Data Catalogue</a>
          <RouterLink @click="closeMobileMenu" to="/about">{{ $t('header.About') }}</RouterLink>
          <div class="user" @click="toggleLogin">
            <div v-if=!loggedIn class="unauthenticated">
              <Icon icon="mingcute:user-4-fill" width="30" height="30" style="color: #aec326; margin-right: 5px" />
              <p id="login">{{ $t('header.Login') }}</p>
            </div>
            <div v-else class="authenticated">
              <v-menu v-model="menu" :close-on-content-click="false" location="end">
                <template v-slot:activator="{ props }">
                  <Icon icon="mingcute:user-4-fill" width="30" height="30" style="color: #0177a9; margin-right: 5px"
                    v-bind="props" />
                  <p id="login" v-bind="props">{{ name }}</p>
                </template>

                <v-card min-width="300">
                  <v-list>
                    <v-list-item>
                      <div style="display: flex; align-items: center;">
                        <Icon icon="mingcute:user-4-fill" width="30" height="30"/>
                        <p style="margin: 0; margin-left: 8px;">{{ name }}</p>
                      </div>
                    </v-list-item>
                  </v-list>

                  <v-divider></v-divider>

                  <v-list>
                    <v-list-item>
                      <v-btn color="primary" variant="text" @click="logout">
                        Log out
                      </v-btn>
                    </v-list-item>

                  </v-list>
                </v-card>
              </v-menu>
            </div>


          </div>
          <li class="separator"></li> <!-- Separator line -->
          <v-menu>            <template v-slot:activator="{ props }">
              <p id="language" v-bind="props" @click="closeMobileMenu">
                {{ selectedLanguage.toUpperCase() }}</p>
            </template>
            <v-list>
              <v-list-item v-for="(item, index) in languages" :key="index" :value="index"
                @click="setLanguage(item.iso639)">
                <v-list-item-title style="display: flex; align-items: center;">
                  <Icon :icon="item.flag" width='30' height='30'
                    style="display: flex; align-items: center; margin-right: 8px;" />
                  {{ item.name }}
                </v-list-item-title>
              </v-list-item>
            </v-list>
          </v-menu>
        </ul>
      </nav>
    </header>
    <div v-if="loginBool" class="login-popup-overlay">
      <div class="login-popup-container">
        <LoginForm @login-complete="handleLoginComplete" @login-cancel="toggleLogin" />
      </div>
    </div>
  </div>
</template>



<style lang="scss" scoped>
header {
  background-color: hsl(0, 0%, 100%);
  color: #086494;
  position: sticky;
  top: 0;
  z-index: 100;
  max-height: 100vh;
  border-bottom: 2px solid #aec326;
  nav {
    display: flex;
    align-items: center;
    padding: 20px 16px;
    overflow-x: auto;

    .branding {
      display: flex;
      align-items: center;
      gap: 8px;

      img {
        max-width: 200px;
      }

      h1 {
        font-size: 24px;
      }
    }

    .nav-routes {
      display: flex;
      flex: 1;
      justify-content: flex-end;
      gap: 40px;
      list-style: none;
      margin: 0 15px 0 10px;
      align-items: center;


      .user:hover {
        cursor: pointer;
      }

      a, .nav-link {
        text-decoration: none;
        color: inherit;
        font-weight: bold;
        font-size: 20px;
        transition: all 0.3s ease;
        padding: 5px 10px;
        border-radius: 4px;
        cursor: pointer;

        &:hover {
          background-color: rgba(0, 0, 0, 0.1);
          transform: translateY(-2px);
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
      }

      #login, a{
        text-decoration: none;
        color: inherit;
        font-weight: bold;
        font-size: 20px;
      }

      #language {
        text-decoration: none;
        font-weight: bold;
        font-size: 20px;
        margin-left: -25px;
        margin-right: -15px;
        align-self: center;
      }

      #language:hover {
        cursor: pointer;
      }

      .user {
        padding-right: 5px;


        .unauthenticated {
          display: flex;
          padding-right: 5px;
          align-items: center;
        }

        .authenticated {
          display: flex;
          padding-right: 5px;
          align-items: center;
        }
      }

      .separator {
        width: 2px;
        /* Thin line */
        height: 30px;
        /* Adjust height as needed */
        background-color: #0177a9;
        /* Adjust color as needed */
        margin-left: -25px;
        /* Adjust spacing as needed */
      }

    }

    .mobile-menu-button {
      display: none;
      cursor: pointer;
      margin-left: auto;
      color: #086494;
    }

    @media (max-width: 768px) {
      .mobile-menu-button {
        display: block;
      }

      .nav-routes {
        display: none;
        position: fixed;
        top: 80px;
        left: 0;
        right: 0;
        background: white;
        flex-direction: column;
        padding: 20px;
        gap: 20px;
        border-bottom: 2px solid #aec326;
        
        &.mobile-menu-active {
          display: flex;
        }

        a {
          width: 100%;
          text-align: center;
          padding: 10px;
        }

        .separator {
          width: 100%;
          height: 2px;
          margin: 10px 0;
        }

        .user {
          width: 100%;
          justify-content: center;
          
          .unauthenticated, .authenticated {
            justify-content: center;
          }
        }
      }
    }
  }
}

.branding {
  @media (max-width: 768px) {
    img {
      max-width: 150px !important;
    }
  }
}

.popup {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 99;
  background-color: rgba(0, 0, 0, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;

  .popup-inner {
    background: #ffffff;
    padding: 50px;
  }

  #label {
    font-weight: bold;
  }

  .label {
    font-weight: bold;
    margin-bottom: 5px;
  }

  @media (max-width: 768px) {
    .popup-inner {
      width: 90%;
      padding: 20px;
    }
  }
}

.language-dropdown {
  background-color: #fff;
  border: 1px solid #ccc;
  border-top: none;
  list-style-type: none;
  padding: 0;
  margin: 0;
  cursor: pointer;
  background-color: #f0f0f0;
}

.language-dropdown ul {
  padding: 0;
  margin: 0;
}

.language-dropdown li {
  cursor: pointer;
  padding: 10px;
}

.language-dropdown li:hover {
  background-color: #f0f0f0;
}

.login-popup-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.login-popup-container {
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
  max-width: 400px;
  width: 90%;
  animation: popup-fade-in 0.3s ease;
}

@keyframes popup-fade-in {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>