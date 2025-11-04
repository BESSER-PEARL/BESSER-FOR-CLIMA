<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// City data with flags and information
let cities = [
  { id: 1, name: "Athens", country: "Greece", flag: "/landing_page/FLAGS/FLAG_Greece.jpg", flagOff: "/landing_page/FLAGS/FLAG_Greece_OFF.jpg", code: "athens", hub: 1, description: "Capital city of Greece, combining ancient heritage with modern urban development", features: ["Urban Mobility", "Air Quality", "Smart City"], hasDashboard: true, hasInfo: true },
  { id: 2, name: "Cascais", country: "Portugal", flag: "/landing_page/FLAGS/FLAG_Portugal.jpg", flagOff: "/landing_page/FLAGS/FLAG_Portugal_OFF.jpg", code: "cascais", hub: 1, description: "Coastal municipality known for its sustainability initiatives and smart city projects", features: ["Waste Management", "Green Spaces", "Coastal Protection"], hasDashboard: true, hasInfo: true },
  { id: 5, name: "Ioannina", country: "Greece", flag: "/landing_page/FLAGS/FLAG_Greece.jpg", flagOff: "/landing_page/FLAGS/FLAG_Greece_OFF.jpg", code: "ioannina", hub: 1, description: "Historic city in northwestern Greece with environmental initiatives", features: ["Lake Protection", "Cultural Heritage", "Sustainability"], hasDashboard: true, hasInfo: true },
  { id: 7, name: "Differdange", country: "Luxembourg", flag: "/landing_page/FLAGS/FLAG_Luxembourg.jpg", flagOff: "/landing_page/FLAGS/FLAG_Luxembourg_OFF.jpg", code: "differdange", hub: 1, description: "Industrial heritage city transitioning to sustainable development", features: ["Urban Regeneration", "Air Quality", "Climate Data"], hasDashboard: true, hasInfo: true },
  { id: 8, name: "Maribor", country: "Slovenia", flag: "/landing_page/FLAGS/FLAG_Slovenia.jpg", flagOff: "/landing_page/FLAGS/FLAG_Slovenia_OFF.jpg", code: "maribor", hub: 2, description: "Second largest city in Slovenia with smart city initiatives", features: ["Smart Mobility", "Waste Management", "Green Infrastructure"], hasDashboard: true, hasInfo: true },
  { id: 11, name: "Sofia", country: "Bulgaria", flag: "/landing_page/FLAGS/FLAG_Bulgaria.jpg", flagOff: "/landing_page/FLAGS/FLAG_Bulgaria_OFF.jpg", code: "sofia", hub: 2, description: "Capital city with environmental and digital transformation projects", features: ["Digital Services", "Air Quality", "Urban Mobility"], hasDashboard: true, hasInfo: true },
  { id: 12, name: "Torino", country: "Italy", flag: "/landing_page/FLAGS/FLAG_Italy.jpg", flagOff: "/landing_page/FLAGS/FLAG_Italy_OFF.jpg", code: "torino", hub: 2, description: "Industrial city evolving into a sustainable urban hub", features: ["Innovation", "Circular Economy", "Smart Mobility"], hasDashboard: true, hasInfo: true },
  { id: 3, name: "Issy-les-Moulineaux", country: "France", flag: "/landing_page/FLAGS/FLAG_France.jpg", flagOff: "/landing_page/FLAGS/FLAG_France_OFF.jpg", code: "issy-les-moulineaux", hub: 1, description: "Smart city pioneer in the Paris metropolitan area", features: ["Digital Innovation", "Energy Efficiency", "Smart Buildings"], hasDashboard: false, hasInfo: true },
  { id: 4, name: "Grenoble", country: "France", flag: "/landing_page/FLAGS/FLAG_France.jpg", flagOff: "/landing_page/FLAGS/FLAG_France_OFF.jpg", code: "grenoble", hub: 1, description: "Alpine city with focus on sustainable urban development", features: ["Climate Action", "Public Transport", "Innovation"], hasDashboard: false, hasInfo: true },
  { id: 6, name: "Krk", country: "Croatia", flag: "/landing_page/FLAGS/FLAG_Croatia.jpg", flagOff: "/landing_page/FLAGS/FLAG_Croatia_OFF.jpg", code: "krk", hub: 1, description: "Island city focused on tourism and environmental protection", features: ["Coastal Management", "Tourism", "Biodiversity"], hasDashboard: false, hasInfo: true },
  { id: 9, name: "Katowice", country: "Poland", flag: "/landing_page/FLAGS/FLAG_Poland.jpg", flagOff: "/landing_page/FLAGS/FLAG_Poland_OFF.jpg", code: "katowice", hub: 2, description: "Industrial city transforming into a green urban center", features: ["Post-Industrial Transformation", "Air Quality", "Smart City"], hasDashboard: false, hasInfo: true },
  { id: 10, name: "Pilsen", country: "Czech Republic", flag: "/landing_page/FLAGS/FLAG_CzechRepublic.jpg", flagOff: "/landing_page/FLAGS/FLAG_CzechRepublic_OFF.jpg", code: "pilsen", hub: 2, description: "Historic city with focus on sustainability and innovation", features: ["Smart Solutions", "Cultural Heritage", "Urban Development"], hasDashboard: false, hasInfo: true },
  { id: 13, name: "Podgorica", country: "Montenegro", flag: "/landing_page/FLAGS/FLAG_Montenegro.jpg", flagOff: "/landing_page/FLAGS/FLAG_Montenegro_OFF.jpg", code: "podgorica", hub: 2, description: "Capital city developing sustainable urban solutions", features: ["Urban Planning", "Environmental Protection", "Smart City"], hasDashboard: false, hasInfo: true },
  { id: 14, name: "Prijedor", country: "Bosnia and Herzegovina", flag: "/landing_page/FLAGS/FLAG_BosniaAndHerzegovina.jpg", flagOff: "/landing_page/FLAGS/FLAG_BosniaAndHerzegovina_OFF.jpg", code: "prijedor", hub: 2, description: "City implementing sustainable development strategies", features: ["Environmental Management", "Urban Development", "Climate Action"], hasDashboard: false, hasInfo: true }
];

// Sort cities so those with dashboard come first
cities = cities.slice().sort((a, b) => {
  if (a.hasDashboard === b.hasDashboard) return 0;
  return a.hasDashboard ? -1 : 1;
});

// State for hover effects
const hoveredCity = ref(null)
const hoveredInfoButton = ref(null)
const hoveredDashboardButton = ref(null)

// Dialog state
const showInfoDialog = ref(false)
const selectedCity = ref(null)

// Show city information dialog
const showCityInfo = (city) => {
  selectedCity.value = city
  showInfoDialog.value = true
}

// Navigate to city dashboard
const goToDashboard = (city) => {
  if (city.hasDashboard) {
    router.push(`/Dashboard/${city.code}`)
  }
}

</script>

<template>
  <div class="home">
    <!-- Hero Section -->
    <section class="hero">
      <div class="hero-overlay">
        <div class="hero-content">
          <div class="logo-section">
            <v-icon size="64" color="white">mdi-earth</v-icon>
          </div>
          <h1>CLIMABOROUGH DATA PLATFORM</h1>
          <p class="hero-subtitle">A comprehensive data platform for climate adaptation and urban resilience.</p>
          <p class="hero-description">Empowering European cities with real-time environmental data and analytics to drive sustainable development.</p>
        </div>
      </div>
    </section>

    <!-- Cities Grid Section -->
    <section class="cities-section">
      <v-container>
        <h2 class="section-title">Participating Cities</h2>
        <p class="section-subtitle">Click on a city to view information or access the dashboard</p>

        <v-row class="cities-grid">
          <v-col
            v-for="city in cities"
            :key="city.id"
            cols="12"
            sm="6"
            md="4"
            lg="3"
          >
            <v-card 
              class="city-card" 
              elevation="2"
              :class="{ 'has-dashboard': city.hasDashboard }"
              @click="city.hasDashboard ? goToDashboard(city) : null"
              @mouseenter="hoveredCity = city.id"
              @mouseleave="hoveredCity = null"
            >
              <div class="city-card-content">
                <!-- Flag -->
                <div class="city-flag">
                  <img 
                    :src="hoveredCity === city.id ? city.flag : city.flagOff" 
                    :alt="`${city.country} flag`"
                    class="flag-image"
                  />
                </div>

                <!-- City Info -->
                <div class="city-info">
                  <h3 class="city-name">{{ city.name }}</h3>
                  <p class="city-country">{{ city.country }}</p>
                </div>

                <!-- Action Buttons -->
                <div class="city-actions">
                  <!-- Hub Badge -->
                  <div class="hub-badge">
                    <img 
                      :src="hoveredCity === city.id ? `/landing_page/ICONS/ICON_Hub${city.hub}.jpg` : `/landing_page/ICONS/ICON_Hub${city.hub}_OFF.jpg`" 
                      :alt="`Hub ${city.hub}`"
                      class="hub-icon"
                    />
                  </div>

                  <!-- Info Button -->
                  <div 
                    class="action-icon-wrapper"
                    @click.stop="showCityInfo(city)"
                    @mouseenter="hoveredInfoButton = city.id"
                    @mouseleave="hoveredInfoButton = null"
                  >
                    <img 
                      :src="hoveredInfoButton === city.id ? '/landing_page/ICONS/ICON_Info.jpg' : '/landing_page/ICONS/ICON_Info_OFF.jpg'" 
                      alt="Info"
                      class="action-icon"
                    />
                    <v-tooltip activator="parent" location="bottom">
                      View Information
                    </v-tooltip>
                  </div>

                  <!-- Dashboard Button -->
                  <div 
                    v-if="city.hasDashboard"
                    class="action-icon-wrapper"
                    @click.stop="goToDashboard(city)"
                    @mouseenter="hoveredDashboardButton = city.id"
                    @mouseleave="hoveredDashboardButton = null"
                  >
                    <img 
                      :src="hoveredDashboardButton === city.id ? '/landing_page/ICONS/ICON_Dashboard.jpg' : '/landing_page/ICONS/ICON_Dashboard_OFF.jpg'" 
                      alt="Dashboard"
                      class="action-icon"
                    />
                    <v-tooltip activator="parent" location="bottom">
                      View Dashboard
                    </v-tooltip>
                  </div>
                  
                  <v-chip
                    v-else
                    size="x-small"
                    color="grey"
                    variant="outlined"
                  >
                    Coming Soon
                  </v-chip>
                </div>
              </div>
            </v-card>
          </v-col>
        </v-row>
      </v-container>
    </section>

    <!-- City Information Dialog -->
    <v-dialog v-model="showInfoDialog" max-width="600">
      <v-card v-if="selectedCity">
        <v-card-title class="d-flex justify-space-between align-center">
          <div class="d-flex align-center">
            <img 
              :src="selectedCity.flag" 
              :alt="`${selectedCity.country} flag`"
              class="flag-image-large"
            />
            <span class="ml-3">{{ selectedCity.name }}</span>
          </div>
          <v-btn
            icon
            size="small"
            variant="text"
            @click="showInfoDialog = false"
          >
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </v-card-title>

        <v-card-subtitle>
          {{ selectedCity.country }}
        </v-card-subtitle>

        <v-divider></v-divider>

        <v-card-text>
          <div class="mb-3 d-flex align-center">
            <img 
              :src="`/landing_page/ICONS/ICON_Hub${selectedCity.hub}.jpg`" 
              :alt="`Hub ${selectedCity.hub}`"
              class="hub-icon-dialog"
            />
            <span class="ml-2 text-h6">Hub {{ selectedCity.hub }}</span>
          </div>

          <p class="mb-4">{{ selectedCity.description }}</p>

          <h4 class="mb-2">Key Focus Areas:</h4>
          <v-chip-group column>
            <v-chip
              v-for="feature in selectedCity.features"
              :key="feature"
              size="small"
              color="primary"
              variant="outlined"
            >
              {{ feature }}
            </v-chip>
          </v-chip-group>
        </v-card-text>

        <v-divider></v-divider>

        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            v-if="selectedCity.hasDashboard"
            color="primary"
            variant="elevated"
            @click="goToDashboard(selectedCity); showInfoDialog = false"
          >
            <v-icon start>mdi-view-dashboard</v-icon>
            View Dashboard
          </v-btn>
          <v-btn
            v-else
            color="grey"
            variant="outlined"
            disabled
          >
            Dashboard Coming Soon
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<style scoped lang="scss">
.home {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background-color: #f5f5f5;
}

/* Hero Section */
.hero {
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
  text-align: center;
  height: 35vh;
  min-height: 320px;
  background: linear-gradient(135deg, rgba(30, 60, 114, 0.8) 0%, rgba(42, 82, 152, 0.8) 50%, rgba(184, 212, 232, 0.8) 100%),
              url('/landing_page/IMG_Header_770x340px.jpg') center/cover no-repeat;
  color: white;
  overflow: hidden;
  
  // Animated background pattern
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-image: 
      radial-gradient(circle at 20% 50%, rgba(255, 255, 255, 0.1) 0%, transparent 50%),
      radial-gradient(circle at 80% 80%, rgba(255, 255, 255, 0.08) 0%, transparent 50%),
      radial-gradient(circle at 40% 20%, rgba(255, 255, 255, 0.06) 0%, transparent 50%);
    animation: float 20s ease-in-out infinite;
  }

  @keyframes float {
    0%, 100% {
      transform: translate(0, 0);
    }
    50% {
      transform: translate(20px, 20px);
    }
  }
  
  .hero-overlay {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: transparent;
    display: flex;
    justify-content: center;
    align-items: center;
  }

  .hero-content {
    position: relative;
    z-index: 1;
    max-width: 900px;
    padding: 40px 20px;

    .logo-section {
      margin-bottom: 1.5rem;
      
      .v-icon {
        filter: drop-shadow(0 4px 6px rgba(0,0,0,0.2));
        animation: pulse 3s ease-in-out infinite;
      }

      @keyframes pulse {
        0%, 100% {
          transform: scale(1);
        }
        50% {
          transform: scale(1.05);
        }
      }
    }

    h1 {
      font-size: 3.5rem;
      font-weight: 700;
      margin-bottom: 1.5rem;
      text-shadow: 2px 2px 8px rgba(0,0,0,0.3);
      letter-spacing: 1px;
    }

    .hero-subtitle {
      font-size: 1.4rem;
      font-weight: 500;
      margin-bottom: 0.8rem;
      line-height: 1.6;
      text-shadow: 1px 1px 4px rgba(0,0,0,0.2);
    }

    .hero-description {
      font-size: 1.1rem;
      font-weight: 300;
      opacity: 0.95;
      line-height: 1.6;
      max-width: 800px;
      margin: 0 auto;
      text-shadow: 1px 1px 3px rgba(0,0,0,0.2);
    }
  }

  @media (max-width: 960px) {
    height: 30vh;
    min-height: 280px;
    
    .hero-content {
      padding: 30px 15px;
      
      h1 {
        font-size: 2.5rem;
      }
      
      .hero-subtitle {
        font-size: 1.2rem;
      }
      
      .hero-description {
        font-size: 1rem;
      }
    }
  }

  @media (max-width: 600px) {
    height: 28vh;
    min-height: 260px;
    
    .hero-content {
      padding: 20px 15px;
      
      .logo-section .v-icon {
        font-size: 48px !important;
      }
      
      h1 {
        font-size: 2rem;
        margin-bottom: 1rem;
      }
      
      .hero-subtitle {
        font-size: 1rem;
        margin-bottom: 0.6rem;
      }
      
      .hero-description {
        font-size: 0.9rem;
      }
    }
  }
}

/* Cities Section */
.cities-section {
  padding: 60px 0;
  background-color: #fafafa;

  .section-title {
    text-align: center;
    font-size: 2.5rem;
    font-weight: bold;
    color: #333;
    margin-bottom: 1rem;
  }

  .section-subtitle {
    text-align: center;
    font-size: 1.2rem;
    color: #666;
    margin-bottom: 3rem;
  }

  .cities-grid {
    margin-top: 2rem;
  }
}

/* City Card - More Rectangular */
.city-card {
  height: 100%;
  transition: all 0.3s ease;
  border-radius: 8px;
  overflow: hidden;
  cursor: default;
  
  &.has-dashboard {
    cursor: pointer;
    
    &:hover {
      transform: translateY(-8px);
      box-shadow: 0 12px 24px rgba(0,0,0,0.15) !important;
    }
  }

  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 16px rgba(0,0,0,0.12) !important;
  }

  .city-card-content {
    padding: 1.25rem;
    display: flex;
    flex-direction: row;
    align-items: center;
    text-align: left;
    gap: 1rem;
    min-height: 110px;
    max-height: 110px;
  }

  .city-flag {
    flex-shrink: 0;
    width: 50px;
    height: 50px;
    display: flex;
    align-items: center;
    justify-content: center;
    
    .flag-image {
      width: 100%;
      height: 100%;
      object-fit: contain;
      transition: all 0.3s ease;
      filter: drop-shadow(0 2px 4px rgba(0,0,0,0.1));
    }
  }

  .city-info {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
    min-width: 0;
    overflow: hidden;
  }

  .city-name {
    font-size: 1.15rem;
    font-weight: 600;
    color: #333;
    line-height: 1.3;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .city-country {
    font-size: 0.9rem;
    color: #666;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .city-actions {
    display: flex;
    flex-direction: column;
    gap: 0.3rem;
    align-items: center;
    flex-shrink: 0;
    width: 40px;
  }

  .hub-badge {
    width: 28px;
    height: 28px;
    display: flex;
    align-items: center;
    justify-content: center;
    
    .hub-icon {
      width: 100%;
      height: 100%;
      object-fit: contain;
      transition: all 0.3s ease;
    }
  }

  .action-icon-wrapper {
    width: 32px;
    height: 32px;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: transform 0.2s ease;

    &:hover {
      transform: scale(1.1);
    }

    .action-icon {
      width: 100%;
      height: 100%;
      object-fit: contain;
      transition: all 0.3s ease;
    }
  }
}

/* Dialog Styles */
.flag-image-large {
  width: 60px;
  height: 60px;
  object-fit: contain;
  vertical-align: middle;
}

.hub-icon-dialog {
  width: 40px;
  height: 40px;
  object-fit: contain;
}

.v-card-title {
  font-size: 1.5rem;
  font-weight: 600;
  padding: 1.5rem !important;
}

.v-card-subtitle {
  font-size: 1.1rem;
  opacity: 0.7;
  padding: 0 1.5rem 1rem !important;
}

.v-card-text {
  padding: 1.5rem !important;
  font-size: 1rem;
  line-height: 1.6;

  h4 {
    font-weight: 600;
    color: #333;
  }
}

.v-card-actions {
  padding: 1rem 1.5rem 1.5rem !important;
}

/* Responsive Design */
@media (max-width: 960px) {
  .cities-section {
    padding: 40px 0;
    
    .section-title {
      font-size: 2rem;
    }
    
    .section-subtitle {
      font-size: 1rem;
    }
  }
  
  .city-card {
    .city-card-content {
      padding: 1rem;
      gap: 0.75rem;
      min-height: 100px;
      max-height: 100px;
    }
    
    .city-flag {
      width: 45px;
      height: 45px;
    }
    
    .city-name {
      font-size: 1.05rem;
    }

    .city-country {
      font-size: 0.85rem;
    }

    .city-actions {
      width: 36px;
      gap: 0.25rem;
    }

    .hub-badge {
      width: 24px;
      height: 24px;
    }

    .action-icon-wrapper {
      width: 28px;
      height: 28px;
    }
  }
}

@media (max-width: 600px) {
  .cities-section {
    padding: 30px 0;
  }
  
  .city-card {
    .city-card-content {
      padding: 1rem;
      gap: 0.75rem;
      min-height: 90px;
      max-height: 90px;
    }
    
    .city-flag {
      width: 40px;
      height: 40px;
    }
    
    .city-name {
      font-size: 1rem;
    }
    
    .city-country {
      font-size: 0.8rem;
    }

    .city-actions {
      flex-direction: row;
      gap: 0.3rem;
      width: auto;
    }

    .hub-badge {
      width: 22px;
      height: 22px;
    }

    .action-icon-wrapper {
      width: 26px;
      height: 26px;
    }
  }
}
</style>

