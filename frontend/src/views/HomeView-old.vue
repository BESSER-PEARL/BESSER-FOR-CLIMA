<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { Icon } from '@iconify/vue'

const router = useRouter()

// City data with flags and information
const cities = [
  { 
    id: 1, 
    name: "Athens", 
    country: "Greece", 
    flag: "🇬🇷",
    code: "athens",
    description: "Capital city of Greece, combining ancient heritage with modern urban development",
    features: ["Urban Mobility", "Air Quality", "Smart City"],
    hasDashboard: true,
    hasInfo: true
  },
  { 
    id: 2, 
    name: "Cascais", 
    country: "Portugal", 
    flag: "🇵🇹",
    code: "cascais",
    description: "Coastal municipality known for its sustainability initiatives and smart city projects",
    features: ["Waste Management", "Green Spaces", "Coastal Protection"],
    hasDashboard: true,
    hasInfo: true
  },
  { 
    id: 3, 
    name: "Issy-les-Moulineaux", 
    country: "France", 
    flag: "🇫🇷",
    code: "issy-les-moulineaux",
    description: "Smart city pioneer in the Paris metropolitan area",
    features: ["Digital Innovation", "Energy Efficiency", "Smart Buildings"],
    hasDashboard: true,
    hasInfo: true
  },
  { 
    id: 4, 
    name: "Grenoble", 
    country: "France", 
    flag: "🇫🇷",
    code: "grenoble",
    description: "Alpine city with focus on sustainable urban development",
    features: ["Climate Action", "Public Transport", "Innovation"],
    hasDashboard: true,
    hasInfo: true
  },
  { 
    id: 5, 
    name: "Ioannina", 
    country: "Greece", 
    flag: "🇬🇷",
    code: "ioannina",
    description: "Historic city in northwestern Greece with environmental initiatives",
    features: ["Lake Protection", "Cultural Heritage", "Sustainability"],
    hasDashboard: true,
    hasInfo: true
  },
  { 
    id: 6, 
    name: "Krk", 
    country: "Croatia", 
    flag: "🇭🇷",
    code: "krk",
    description: "Island city focused on tourism and environmental protection",
    features: ["Coastal Management", "Tourism", "Biodiversity"],
    hasDashboard: true,
    hasInfo: true
  },
  { 
    id: 7, 
    name: "Differdange", 
    country: "Luxembourg", 
    flag: "🇱🇺",
    code: "differdange",
    description: "Industrial heritage city transitioning to sustainable development",
    features: ["Urban Regeneration", "Air Quality", "Climate Data"],
    hasDashboard: true,
    hasInfo: true
  },
  { 
    id: 8, 
    name: "Maribor", 
    country: "Slovenia", 
    flag: "🇸🇮",
    code: "maribor",
    description: "Second largest city in Slovenia with smart city initiatives",
    features: ["Smart Mobility", "Waste Management", "Green Infrastructure"],
    hasDashboard: true,
    hasInfo: true
  },
  { 
    id: 9, 
    name: "Katowice", 
    country: "Poland", 
    flag: "🇵🇱",
    code: "katowice",
    description: "Industrial city transforming into a green urban center",
    features: ["Post-Industrial Transformation", "Air Quality", "Smart City"],
    hasDashboard: true,
    hasInfo: true
  },
  { 
    id: 10, 
    name: "Pilsen", 
    country: "Czech Republic", 
    flag: "🇨🇿",
    code: "pilsen",
    description: "Historic city with focus on sustainability and innovation",
    features: ["Smart Solutions", "Cultural Heritage", "Urban Development"],
    hasDashboard: false,
    hasInfo: true
  },
  { 
    id: 11, 
    name: "Sofia", 
    country: "Bulgaria", 
    flag: "🇧🇬",
    code: "sofia",
    description: "Capital city with environmental and digital transformation projects",
    features: ["Digital Services", "Air Quality", "Urban Mobility"],
    hasDashboard: false,
    hasInfo: true
  },
  { 
    id: 12, 
    name: "Torino", 
    country: "Italy", 
    flag: "🇮🇹",
    code: "torino",
    description: "Industrial city evolving into a sustainable urban hub",
    features: ["Innovation", "Circular Economy", "Smart Mobility"],
    hasDashboard: false,
    hasInfo: true
  },
  { 
    id: 13, 
    name: "Podgorica", 
    country: "Montenegro", 
    flag: "🇲🇪",
    code: "podgorica",
    description: "Capital city developing sustainable urban solutions",
    features: ["Urban Planning", "Environmental Protection", "Smart City"],
    hasDashboard: false,
    hasInfo: true
  },
  { 
    id: 14, 
    name: "Prijedor", 
    country: "Bosnia and Herzegovina", 
    flag: "🇧🇦",
    code: "prijedor",
    description: "City implementing sustainable development strategies",
    features: ["Environmental Management", "Urban Development", "Climate Action"],
    hasDashboard: false,
    hasInfo: true
  }
]

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
      <div class="hero-content">
        <h1>CLIMABOROUGH DATA PLATFORM</h1>
        <p>Explore climate and urban data from participating cities</p>
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
            >
              <div class="city-card-content">
                <!-- Flag -->
                <div class="city-flag">{{ city.flag }}</div>

                <!-- City Name and Country -->
                <h3 class="city-name">{{ city.name }}</h3>
                <p class="city-country">{{ city.country }}</p>

                <!-- Action Buttons -->
                <div class="city-actions">
                  <v-btn
                    icon
                    size="small"
                    color="primary"
                    variant="text"
                    @click.stop="showCityInfo(city)"
                  >
                    <v-icon>mdi-information-outline</v-icon>
                    <v-tooltip activator="parent" location="bottom">
                      View Information
                    </v-tooltip>
                  </v-btn>

                  <v-btn
                    v-if="city.hasDashboard"
                    icon
                    size="small"
                    color="success"
                    variant="text"
                    @click.stop="goToDashboard(city)"
                  >
                    <v-icon>mdi-view-dashboard-outline</v-icon>
                    <v-tooltip activator="parent" location="bottom">
                      View Dashboard
                    </v-tooltip>
                  </v-btn>
                  
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
          <div>
            <span class="city-flag-large">{{ selectedCity.flag }}</span>
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
  display: flex;
  justify-content: center;
  align-items: center;
  text-align: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  height: 40vh;
  color: white;
  position: relative;
  
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-image: url('../assets/fake.png');
    background-size: cover;
    background-position: center;
    opacity: 0.2;
  }

  .hero-content {
    position: relative;
    z-index: 1;
    padding: 20px;

    h1 {
      font-size: 3rem;
      font-weight: bold;
      margin-bottom: 1rem;
      text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }

    p {
      font-size: 1.5rem;
      opacity: 0.95;
    }
  }

  @media (max-width: 768px) {
    height: 30vh;
    
    .hero-content {
      h1 {
        font-size: 2rem;
      }
      
      p {
        font-size: 1.1rem;
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

/* City Card */
.city-card {
  height: 100%;
  transition: all 0.3s ease;
  border-radius: 12px;
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
    padding: 2rem;
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    min-height: 200px;
  }

  .city-flag {
    font-size: 4rem;
    margin-bottom: 1rem;
    filter: drop-shadow(0 2px 4px rgba(0,0,0,0.1));
  }

  .city-name {
    font-size: 1.5rem;
    font-weight: 600;
    color: #333;
    margin-bottom: 0.5rem;
  }

  .city-country {
    font-size: 1rem;
    color: #666;
    margin-bottom: 1.5rem;
  }

  .city-actions {
    display: flex;
    gap: 0.5rem;
    align-items: center;
    justify-content: center;
    margin-top: auto;
  }
}

/* Dialog Styles */
.city-flag-large {
  font-size: 3rem;
  vertical-align: middle;
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
      padding: 1.5rem;
      min-height: 180px;
    }
    
    .city-flag {
      font-size: 3rem;
    }
    
    .city-name {
      font-size: 1.3rem;
    }
  }
}

@media (max-width: 600px) {
  .cities-section {
    padding: 30px 0;
  }
  
  .city-card {
    .city-card-content {
      padding: 1.25rem;
      min-height: 160px;
    }
    
    .city-flag {
      font-size: 2.5rem;
    }
    
    .city-name {
      font-size: 1.2rem;
    }
    
    .city-country {
      font-size: 0.9rem;
    }
  }
}
</style>
  

  .text-container {
    background-color: rgba(255, 255, 255, 0.8); // Semi-transparent white
    display: inline-block; // Adjust size to content
    padding: 20px; // Add some padding around the text
    border-radius: 8px; // Optional: adds rounded corners
    margin: 20px; // Optional: adds margin around the text container
    font-size: 1vw;
  }

  @media (max-width: 768px) {
    height: 40vh;
    
    .text-container {
      width: 90%;
      margin: 10px;
      padding: 15px;
      font-size: 16px;
      
      h1 {
        font-size: 24px;
        margin-bottom: 10px;
      }
      
      p {
        font-size: 16px;
        margin-bottom: 15px;
      }
    }
  }

}

.carousel {
  flex-grow: 1;
  min-height: 70vh;

  .text-container {
    position: relative;
    font-size: 16px;
    max-height: 330px; // Adjust based on your design
    overflow-y: auto; // Adds a vertical scrollbar if content exceeds max-height
    text-align: left; // Align text to the left
    padding: 20px; // Padding inside the text container
    box-sizing: border-box; // Ensure padding is included in the max-height
  }

  @media (max-width: 768px) {
    min-height: 60vh;

    .carousel__item {
      padding: 10px;
      flex-direction: column;
      
      &.mobile-layout {
        .image-container {
          flex: 0 0 100%;
          margin-bottom: 20px;
          
          img {
            width: 100%;
            max-width: 300px;
          }
        }
        
        .info-box {
          flex: 0 0 100%;
          margin-right: 0;
          width: 100%;
          
          .text-container {
            padding: 15px;
            max-height: 250px;
          }
        }
      }
    }

    .title {
      font-size: 24px;
    }

    .subtitle {
      font-size: 18px;
    }

    .description {
      font-size: 14px;
    }
  }
}


.carousel__item {
  background-color: rgb(255, 255, 255);
  color: black; // Changed from white to black to match text visibility
  min-height: 300px;
  width: 100%;
  font-size: 10px;
  border-radius: 8px;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px 80px;
  box-sizing: border-box; // Ensure padding is included in the width and height
}

.carousel__slide {
  padding: 10px;
}

.carousel__prev,
.carousel__next {
  background-color: transparent;
  border: none;
}

.image-container {
  flex: 0 0 25%; // Takes up 25% of the slide's width
  text-align: center; // Center the image horizontally
}

.slide-image {
  width: 70%;
  height: auto; // Maintain aspect ratio
}

.info-box {
  flex: 0 0 60%;
  margin-right: 40px;
  background-color: #ffffff;
  color: rgb(0, 0, 0);
  position: relative;
  transition: all 0.3s ease;
  border-radius: 8px;
  
  &:hover {
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
    transform: translateY(-2px);
  }
}



.title {
  font-size: 30px;
}

.subtitle {
  margin-top: 10px; // Adds margin between title and subtitle
  opacity: 60%;
}

.description {
  margin-top: 10px; // Adds margin between subtitle and description
  margin-bottom: 10px; // Adds margin between description and button
}

.button-city {
  display: block;
  margin: 0 auto; // Center the button horizontally
}

.custom-arrow {
  font-size: 60px;
  font-weight: bold;
  color: black;
  cursor: pointer;
  padding: 10px;
  user-select: none;
}

.carousel__prev,
.carousel__next {
  background-color: transparent;
  border: none;
}

@media (max-width: 768px) {
  .custom-arrow {
    font-size: 40px;
    padding: 5px;
  }
}

// Optimize carousel controls for mobile
:deep(.carousel__pagination) {
  @media (max-width: 768px) {
    bottom: 0;
    padding: 10px 0;
    
    .carousel__pagination-button {
      width: 10px;
      height: 10px;
      margin: 0 4px;
    }
  }
}

:deep(.carousel__nav) {
  @media (max-width: 768px) {
    .carousel__prev,
    .carousel__next {
      width: 40px;
      height: 40px;
    }
  }
}
</style>


<style>
:root {
  --vc-nav-width: 60px;
  --vc-nav-height: 60px;
  --vc-pgn-width: 15px;
  --vc-pgn-height: 15px;
  --vc-pgn-margin: 5px;
  --vc-pgn-border-radius: 100%;
}
</style>