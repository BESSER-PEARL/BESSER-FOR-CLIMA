<script setup>
import { ref, onMounted, onUnmounted, watch, computed } from 'vue';
import { RouterLink, useRoute, useRouter } from 'vue-router';
import { useI18n } from 'vue-i18n';
import LoginForm from './forms/LoginForm.vue';
import { useAuth } from '../composables/useAuth';

const { locale } = useI18n();
const route = useRoute();
const router = useRouter();

// Use authentication composable
const auth = useAuth();

locale.value = "en"

const loginBool = ref(false)
const menu = ref(false)

// Enhanced admin check - same logic as router
const isAdmin = computed(() => {
  // First check if user is authenticated and auth is initialized
  if (!auth.isAuthenticated.value || !auth.isInitialized.value) return false;
  
  // Check for admin roles
  const hasAdminRole = auth.hasRole('admin') || 
                      auth.hasRole('realm-admin') || 
                      auth.hasRole('climaborough-admin');
  
  // Check for specific admin groups (be more strict)
  const userInfo = auth.userInfo.value;
  const hasAdminGroup = userInfo?.group_membership?.some(group => 
    group === '/Administrator' || 
    group === '/admin' || 
    group === '/Admin' ||
    group.endsWith('/Administrator') ||
    group.endsWith('/admin') ||
    group.endsWith('/Admin')
  );
  
  // Only check userType if it's specifically 'admin' (not 'cityuser')
  const isAdminType = auth.userType?.value === 'admin';
  
  return hasAdminRole || hasAdminGroup || isAdminType;
});

// Navigation handler that checks authentication before navigating
const handleNavigation = (path) => {
  const protectedRoutes = [ '/bot', '/datacatalogue', '/admin/kpis'];
  
  if (protectedRoutes.includes(path) && !auth.isAuthenticated.value) {
    // Don't navigate, just show login popup
    loginBool.value = true;
    return;
  }
  
  // If authenticated or route is not protected, navigate normally
  router.push(path);
  closeMobileMenu();
}

const logout = () => {
  auth.logout();
  // Emit logout event
  window.dispatchEvent(new CustomEvent('keycloak-logout'));
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

// Manually refresh user info when LoginForm completes
const handleLoginComplete = () => {
  auth.updateAuthState();
  loginBool.value = false;
};

const isMobileMenuOpen = ref(false)

const toggleMobileMenu = () => {
  isMobileMenuOpen.value = !isMobileMenuOpen.value
}

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
          <RouterLink @click="closeMobileMenu" to="/" class="nav-link">
            <Icon icon="mdi:home" width="20" height="20" />
            <span>{{ $t('header.home') }}</span>
          </RouterLink>
          
          
          <a @click="handleNavigation('/datacatalogue')" class="nav-link">
            <Icon icon="mdi:database" width="20" height="20" />
            <span>Data Catalogue</span>
          </a>
          <a @click="handleNavigation('/bot')" class="nav-link">
            <Icon icon="mdi:robot" width="20" height="20" />
            <span>Clima Agent</span>
          </a>
          
          <RouterLink @click="closeMobileMenu" to="/about" class="nav-link">
            <Icon icon="mdi:information" width="20" height="20" />
            <span>{{ $t('header.About') }}</span>
          </RouterLink>
          
          <li class="separator"></li>
          
          <div class="user" @click="toggleLogin">
            <div v-if="!auth.isAuthenticated.value" class="unauthenticated">
              <Icon icon="mingcute:user-4-fill" width="28" height="28" style="color: #aec326;" />
              <span class="login-text">{{ $t('header.Login') }}</span>
            </div>
            <div v-else class="authenticated">
              <v-menu v-model="menu" :close-on-content-click="false" location="bottom end" offset="8">
                <template v-slot:activator="{ props }">
                  <div class="user-info" v-bind="props">
                    <Icon icon="mingcute:user-4-fill" width="28" height="28" style="color: #0177a9;" />
                    <span class="username">{{ auth.userInfo.value?.name || auth.userInfo.value?.preferred_username }}</span>
                    <Icon icon="mdi:chevron-down" width="20" height="20" style="color: #0177a9;" />
                  </div>
                </template>

                <v-card min-width="300">
                  <v-list>
                    <v-list-item class="user-menu-header">
                      <div class="user-details">
                        <Icon icon="mingcute:user-4-fill" width="40" height="40" style="color: #0177a9;"/>
                        <div class="user-text">
                          <p class="user-name">{{ auth.userInfo.value?.name || auth.userInfo.value?.preferred_username }}</p>
                          <p class="user-email">{{ auth.userInfo.value?.email }}</p>
                        </div>
                      </div>
                    </v-list-item>
                  </v-list>

                  <v-divider></v-divider>

                  <!-- Admin Panel Link (only for admins) -->
                  <v-list v-if="isAdmin">
                    <v-list-item @click="handleNavigation('/admin/kpis')" class="admin-menu-item">
                      <template v-slot:prepend>
                        <Icon icon="mdi:shield-account" width="24" height="24" style="color: #ff6b35;" />
                      </template>
                      <v-list-item-title class="admin-title">
                        Admin Panel
                      </v-list-item-title>
                    </v-list-item>
                    <v-divider></v-divider>
                  </v-list>

                  <v-list>
                    <v-list-item>
                      <v-btn color="error" variant="flat" block @click="logout" prepend-icon="mdi:logout">
                        Log out
                      </v-btn>
                    </v-list-item>
                  </v-list>
                </v-card>
              </v-menu>
            </div>
          </div>
          
          <li class="separator"></li>
          
          <v-menu>
            <template v-slot:activator="{ props }">
              <div class="language-selector" v-bind="props" @click="closeMobileMenu">
                <Icon icon="mdi:web" width="20" height="20" />
                <span class="language-text">{{ selectedLanguage.toUpperCase() }}</span>
                <Icon icon="mdi:chevron-down" width="18" height="18" />
              </div>
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
  background-color: #ffffff;
  color: #086494;
  position: sticky;
  top: 0;
  z-index: 100;
  border-bottom: 3px solid #aec326;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  
  nav {
    display: flex;
    align-items: center;
    padding: 10px 10px;
    max-width: 1400px;
    margin: 0 auto;

    .branding {
      display: flex;
      align-items: center;
      gap: 8px;

      img {
        max-width: 200px;
        transition: transform 0.3s ease;
        
        &:hover {
          transform: scale(1.05);
        }
      }
    }

    .nav-routes {
      display: flex;
      flex: 1;
      justify-content: flex-end;
      gap: 8px;
      list-style: none;
      margin: 0;
      align-items: center;

      a, .nav-link {
        display: flex;
        align-items: center;
        gap: 6px;
        text-decoration: none;
        color: #086494;
        font-weight: 600;
        font-size: 16px;
        padding: 10px 16px;
        border-radius: 8px;
        cursor: pointer;
        transition: all 0.3s ease;
        white-space: nowrap;

        &:hover {
          background-color: rgba(174, 195, 38, 0.15);
          transform: translateY(-2px);
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }

        &.router-link-active {
          background-color: rgba(174, 195, 38, 0.2);
          color: #086494;
        }

        span {
          font-size: 16px;
        }
      }

      .user {
        cursor: pointer;
        
        .unauthenticated {
          display: flex;
          align-items: center;
          gap: 8px;
          padding: 8px 16px;
          border-radius: 8px;
          transition: all 0.3s ease;
          
          &:hover {
            background-color: rgba(174, 195, 38, 0.15);
          }
          
          .login-text {
            font-weight: 600;
            font-size: 16px;
            color: #086494;
          }
        }

        .authenticated {
          display: flex;
          align-items: center;
          
          .user-info {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 8px 16px;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s ease;
            
            &:hover {
              background-color: rgba(1, 119, 169, 0.1);
            }
            
            .username {
              font-weight: 600;
              font-size: 16px;
              color: #086494;
              max-width: 150px;
              overflow: hidden;
              text-overflow: ellipsis;
              white-space: nowrap;
            }
          }
        }
      }

      .separator {
        width: 2px;
        height: 32px;
        background: linear-gradient(180deg, transparent, #0177a9, transparent);
        margin: 0 8px;
        flex-shrink: 0;
      }

      .language-selector {
        display: flex;
        align-items: center;
        gap: 6px;
        padding: 8px 12px;
        border-radius: 8px;
        cursor: pointer;
        transition: all 0.3s ease;
        color: #086494;
        
        &:hover {
          background-color: rgba(174, 195, 38, 0.15);
        }
        
        .language-text {
          font-weight: 600;
          font-size: 16px;
        }
      }
    }

    .mobile-menu-button {
      display: none;
      cursor: pointer;
      margin-left: auto;
      color: #086494;
      padding: 8px;
      border-radius: 8px;
      transition: all 0.3s ease;
      
      &:hover {
        background-color: rgba(174, 195, 38, 0.15);
      }
    }

    @media (max-width: 1024px) {
      nav {
        padding: 16px 20px;
      }
      
      .nav-routes {
        gap: 4px;
        
        a, .nav-link {
          padding: 8px 12px;
          font-size: 15px;
          
          span {
            font-size: 15px;
          }
        }
      }
    }

    @media (max-width: 768px) {
      nav {
        padding: 12px 16px;
      }
      
      .mobile-menu-button {
        display: flex;
      }

      .nav-routes {
        display: none;
        position: fixed;
        top: 72px;
        left: 0;
        right: 0;
        background: white;
        flex-direction: column;
        padding: 20px;
        gap: 12px;
        border-bottom: 3px solid #aec326;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        max-height: calc(100vh - 72px);
        overflow-y: auto;
        
        &.mobile-menu-active {
          display: flex;
        }

        a, .nav-link {
          width: 100%;
          justify-content: flex-start;
          padding: 12px 16px;
          font-size: 16px;
          
          span {
            font-size: 16px;
          }
        }

        .separator {
          width: 100%;
          height: 2px;
          margin: 8px 0;
        }

        .user {
          width: 100%;
          
          .unauthenticated,
          .authenticated {
            width: 100%;
            justify-content: flex-start;
            padding: 12px 16px;
          }
          
          .authenticated .user-info {
            width: 100%;
            justify-content: flex-start;
          }
        }
        
        .language-selector {
          width: 100%;
          justify-content: flex-start;
          padding: 12px 16px;
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
  background-color: rgba(0, 0, 0, 0.6);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
}

.login-popup-container {
  background: white;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  max-width: 420px;
  width: 90%;
  animation: popup-fade-in 0.3s ease;
}

@keyframes popup-fade-in {
  from {
    opacity: 0;
    transform: translateY(-30px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

/* User menu styling */
.user-menu-header {
  padding: 16px !important;
  
  .user-details {
    display: flex;
    align-items: center;
    gap: 12px;
    
    .user-text {
      display: flex;
      flex-direction: column;
      gap: 4px;
      
      .user-name {
        margin: 0;
        font-weight: 600;
        font-size: 16px;
        color: #086494;
      }
      
      .user-email {
        margin: 0;
        font-size: 13px;
        color: #666;
      }
    }
  }
}

/* Admin menu item styling */
.admin-menu-item {
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:hover {
    background: linear-gradient(90deg, rgba(255, 107, 53, 0.1) 0%, transparent 100%) !important;
  }
  
  .admin-title {
    color: #ff6b35;
    font-weight: 600;
    font-size: 15px;
  }
}

/* Admin link styling - keeping for backward compatibility */
.admin-link {
  background: linear-gradient(135deg, #ff6b35 0%, #ff8e53 100%) !important;
  color: white !important;
  font-weight: 600 !important;
  box-shadow: 0 2px 8px rgba(255, 107, 53, 0.3) !important;
  
  &:hover {
    background: linear-gradient(135deg, #ff5722 0%, #ff7744 100%) !important;
    box-shadow: 0 4px 12px rgba(255, 107, 53, 0.4) !important;
    transform: translateY(-2px) !important;
  }
}

/* Login popup styling */
</style>