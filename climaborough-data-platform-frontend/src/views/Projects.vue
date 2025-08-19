<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue';
import { useRouter } from 'vue-router';
import AuthRequired from '../components/AuthRequired.vue';
import { useAuth } from '../composables/useAuth';

const router = useRouter();

// Use authentication composable
const auth = useAuth();

const isAdmin = computed(() => {
  return auth.userType.value === 'admin';
});

const isCityUser = computed(() => {
  if (!auth.userInfo.value) return false;
  const isCityGroup = auth.userInfo.value.group_membership?.some(group => group.startsWith('/City/'));
  return isCityGroup && projects.some(project => project.title === auth.userCity.value);
});

const isMobile = ref(false)

const checkMobile = () => {
  isMobile.value = window.innerWidth <= 768
}

const keycloakLoginSuccessHandler = () => {
  if (auth.isAuthenticated.value && isCityUser.value) {
    console.log('City user logged in:', auth.userCity.value);
  }
  
  // Debug information
  // console.log('Authentication state:', {
  //   isAuthenticated: auth.isAuthenticated.value,
  //   userInfo: auth.userInfo.value,
  //   userType: auth.userType.value,
  //   userCity: auth.userCity.value,
  //   isAdmin: isAdmin.value,
  //   isCityUser: isCityUser.value
  // });
};

function updateCSSVariable() {
  if (isMobile.value) {
    document.documentElement.style.setProperty('--starting-position', '20px');
    document.documentElement.style.setProperty('--margin-right', '20px');
  } else {
    const screenWidth = window.innerWidth - 20;
    const numIcons = Math.floor(screenWidth / 240);
    const startingPosition = (screenWidth - numIcons * 240) / 2;
    document.documentElement.style.setProperty('--starting-position', `${startingPosition}px`);
    document.documentElement.style.setProperty('--margin-right', '140px');
  }
}

onMounted(() => {
  checkMobile()
  window.addEventListener('resize', checkMobile)
  updateCSSVariable()
  
  // Listen for authentication changes
  window.addEventListener('keycloak-login-success', keycloakLoginSuccessHandler);
  
  // Watch for authentication changes
  watch(() => auth.isAuthenticated.value, (newVal) => {
    // console.log('Auth state changed:', newVal);
    keycloakLoginSuccessHandler();
  }, { immediate: true });
  
  watch(() => auth.userCity.value, (newVal) => {
    // console.log('User city changed:', newVal);
  }, { immediate: true });
});

onBeforeUnmount(() => {
  window.removeEventListener('resize', updateCSSVariable);
  window.removeEventListener('keycloak-login-success', keycloakLoginSuccessHandler);
});

const projects = [
  { id: 1, image: 'diff.svg', title: "Differdange", country: "Luxembourg", imageball: "luxembourgball.svg", type: "Sustainable energy production", hub: 1 },
  { id: 2, image: 'casc.svg', title: "Cascais", country: "Portugal", imageball: "portugalball.svg", type: "Textile Waste", hub: 2 },
  { id: 3, image: 'sofi.svg', title: "Sofia", country: "Bulgaria", imageball: "bulgariaball.svg", type: "Parking", hub: 1 },
  { id: 4, image: 'mari.svg', title: "Maribor", country: "Slovenia", imageball: "sloveniaball.svg", type: "Bio-waste", hub: 2 },
  { id: 5, image: 'Athen.svg', title: "Athens", country: "Greece", imageball: "greeceball.svg", type: "Energy Community", hub: 1 },
  { id: 6, image: 'mari.svg', title: "Ioannina", country: "Greece", imageball: "greeceball.svg", type: "Waste", hub: 2 },
  { id: 7, image: 'Grenoble.svg', title: "Grenoble-Alpes", country: "France", imageball: "franceball.svg", type: "Public building simulation", hub: 1 },
  { id: 8, image: 'torino.svg', title: "Torino", country: "Italy", imageball: "italyball.svg", type: "Waste", hub: 2 }
]
</script>

<template>
  <AuthRequired>
    <div class="body" :class="{ 'mobile': isMobile }">
      <a class="main-title">{{ $t('projectview.title') }}</a>
      
      <!-- Display for administrators - global view -->
      <template v-if="isAdmin">
        <div class="hub">
          <h1 style="margin-left: 80px; margin-top: 30px">{{ $t('projectview.hub1') }}</h1>
          <div class="icon-container">
            <div v-for="project in projects" :key="project.id">
              <div v-if="project.hub == 1" class="icon">
                <RouterLink :to='"Dashboard/" + project.title'>
                  <div>
                    <img class="imagebutton" :src="project.image"><br>
                  </div>
                </RouterLink>
                <div class="info">
                  <img :src="project.imageball">
                  {{ project.title }}
                </div>
                <div class="grey">
                  {{ project.type }}
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="hub">
          <h1 style="margin-left: 80px; margin-top: 30px">{{ $t('projectview.hub2') }}</h1>
          <div class="icon-container">
            <div v-for="project in projects" :key="project.id">
              <div v-if="project.hub == 2" class="icon">
                <RouterLink :to='"Dashboard/" + project.title'>
                  <div>
                    <img class="imagebutton" :src="project.image"><br>
                  </div>
                </RouterLink>
                <div class="info">
                  <img :src="project.imageball">
                  {{ project.title }}
                </div>
                <div class="grey">
                  {{ project.type }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </template>
      
      <!-- Display for city accounts -->
      <template v-else-if="isCityUser">
        <!-- Debug information for city users -->
        <!-- <div style="background: #f0f0f0; padding: 10px; margin: 10px; border-radius: 5px;" v-if="auth.userInfo.value">
          <h4>Debug Info:</h4>
          <p>User City: {{ auth.userCity.value }}</p>
          <p>Available Projects: {{ projects.map(p => p.title).join(', ') }}</p>
          <p>Matching Project: {{ projects.find(p => p.title === auth.userCity.value)?.title || 'None found' }}</p>
        </div> -->
        
        <div class="hub">
          <h1>My Project</h1>
          <div class="icon-container">
            <div v-for="project in projects" :key="project.id">
              <div v-if="project.title === auth.userCity.value" class="icon">
                <RouterLink :to='"Dashboard/" + project.title'>
                  <div>
                    <img class="imagebutton" :src="project.image"><br>
                  </div>
                </RouterLink>
                <div class="info">
                  <img :src="project.imageball">
                  {{ project.title }}
                </div>
                <div class="grey">
                  {{ project.type }}
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="hub">
          <h1 style="margin-left: 80px; margin-top: 30px">Other Projects</h1>
          <div class="icon-container">
            <div v-for="project in projects" :key="project.id">
              <div v-if="project.title !== auth.userCity.value" class="icon">
                <RouterLink :to='"Dashboard/" + project.title'>
                  <div>
                    <img class="imagebutton" :src="project.image"><br>
                  </div>
                </RouterLink>
                <div class="info">
                  <img :src="project.imageball">
                  {{ project.title }}
                </div>
                <div class="grey">
                  {{ project.type }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </template>

      <!-- Default display for other account types -->
      <template v-else>
        <div class="hub">
          <h1 style="margin-left: 80px; margin-top: 30px">{{ $t('projectview.hub1') }}</h1>
          <div class="icon-container">
            <div v-for="project in projects" :key="project.id">
              <div v-if="project.hub == 1" class="icon">
                <RouterLink :to='"Dashboard/" + project.title'>
                  <div>
                    <img class="imagebutton" :src="project.image"><br>
                  </div>
                </RouterLink>
                <div class="info">
                  <img :src="project.imageball">
                  {{ project.title }}
                </div>
                <div class="grey">
                  {{ project.type }}
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="hub">
          <h1 style="margin-left: 80px; margin-top: 30px">{{ $t('projectview.hub2') }}</h1>
          <div class="icon-container">
            <div v-for="project in projects" :key="project.id">
              <div v-if="project.hub == 2" class="icon">
                <RouterLink :to='"Dashboard/" + project.title'>
                  <div>
                    <img class="imagebutton" :src="project.image"><br>
                  </div>
                </RouterLink>
                <div class="info">
                  <img :src="project.imageball">
                  {{ project.title }}
                </div>
                <div class="grey">
                  {{ project.type }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </template>
    </div>
  </AuthRequired>
</template>

<style lang="scss" scoped>
.body {
  margin: 10px;
  min-height: 90vh;

  &.mobile {
    margin: 5px;

    .main-title {
      margin-left: 10px;
      margin-top: 30px;
      font-size: 30px;
      display: block;
    }

    .hub h1 {
      margin-left: 15px;
      font-size: 24px;
    }

    .icon-container {
      justify-content: center;
      margin-left: 0;
      padding: 0 10px;
    }

    .icon {
      margin-right: 20px;
      margin-top: 20px;
      margin-bottom: 20px;
      width: 140px;

      .imagebutton {
        width: 140px;
        height: auto;
      }

      .info {
        font-size: 14px;
        
        img {
          width: 20px;
          height: auto;
        }
      }

      .grey {
        font-size: 12px;
      }
    }
  }
}

.main-title {
  margin-left: 15px;
  margin-top: 60px;
  font-weight: bolder;
  font-size: 50px;
  color: #0177a9;
}

.hub h1 {
  margin-left: 80px;
  margin-top: 30px;
  padding-left: 15px;
  border-left: 4px solid #aec326;;
}

.icon-container {
  display: flex;
  margin-left: var(--starting-position);
  flex-wrap: wrap;
}

.icon {
  font-weight: bold;
  text-align: left;
  margin-right: 80px;
  margin-top: 40px;
  margin-bottom: 40px;
  width: 180px;
}

.imagebutton {
  transition: box-shadow 0.1s ease;
  align-self: flex-start;
}

.imagebutton:hover {
  cursor: pointer;
  box-shadow: 1px 1px 5px 5px rgba(0, 0, 0, 0.5);
}

.info {
  flex: 1;
  display: flex;
  justify-content: left;
  align-items: center;
  color: #575757;
}

.info img {
  margin-right: 5px;
  margin-bottom: 5px
}

.grey {
  font-weight: 100;
  opacity: 70%;
}

// Add touch-friendly interactions for mobile
@media (max-width: 768px) {
  .imagebutton {
    &:active {
      box-shadow: 0 0 10px rgba(0, 0, 0, 0.3);
      transform: scale(0.98);
    }
  }
}

// Smooth transitions
.icon, .imagebutton {
  transition: all 0.2s ease;
  will-change: transform;
  transform: translateZ(0);
}
</style>