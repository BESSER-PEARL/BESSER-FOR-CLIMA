<script setup>

import 'vue3-carousel/dist/carousel.css'
import { Carousel, Slide, Pagination, Navigation } from 'vue3-carousel'
import { RouterLink } from 'vue-router';
import { ref, onMounted } from 'vue'

const slides = [
  { id: 1, image: 'differdange.jpg', title: "Differdange", country: "Luxembourg", description: "t('homeview.carousel_differdange')" },
  { id: 2, image: 'cascais.jpg', title: "Cascais", country: "Portugal", description: "t('homeview.carousel_cascais')" },
  { id: 3, image: 'sofia.jpg', title: "Sofia", country: "Bulgaria", description: "t('homeview.carousel_sofia')" },
  { id: 4, image: 'maribor.jpg', title: "Maribor", country: "Slovenia", description: "t('homeview.carousel_maribor')" },
  { id: 5, image: 'athens.jpg', title: "Athens", country: "Greece", description: "t('homeview.carousel_athens')" },
  { id: 6, image: 'grenoble.jpg', title: "Grenoble-Alpes", country: "France", description: "t('homeview.carousel_grenoble')" },
  { id: 7, image: 'ioannina.jpg', title: "Ioannina", country: "Greece", description: "t('homeview.carousel_ioannina')" },
  { id: 13, image: 'torino.jpg', title: "Torino", country: "Italy", description: "t('homeview.carousel_torino')" },
  { id: 8, image: 'Issy-les-Moulineaux.jpg', title: "Issy-les-Moulineaux", country: "France", description: "t('homeview.carousel_issy')" },
  { id: 9, image: 'krk.jpg', title: "Krk", country: "Croatia", description: "t('homeview.carousel_krk')" },
  { id: 10, image: 'pilsen.jpg', title: "Pilsen", country: "Czech Republic", description: "t('homeview.carousel_pilsen')" },
  { id: 11, image: 'podgorica.jpg', title: "Podgorica", country: "Montenegro", description: "t('homeview.carousel_podgorica')" },
  { id: 12, image: 'prejador.jpg', title: "Prijedor", country: "Bosnia and Herzegovina", description: "t('homeview.carousel_prijedor')" },
  { id: 14, image: 'katowice.jpg', title: "Katowice", country: "Poland", description: "t('homeview.carousel_katowice')" }
]

const isMobile = ref(false)

onMounted(() => {
  checkMobile()
  window.addEventListener('resize', checkMobile)
})

const checkMobile = () => {
  isMobile.value = window.innerWidth <= 768
}

</script>

<template>
  <div class="main">
    <section class="hero">
      <div class="text-container">
        <h1>{{ $t('homeview.hero_title') }}</h1>
        <p>{{ $t('homeview.hero_subtitle') }}</p>
        <RouterLink to="/projects">
          <v-btn> {{ $t('homeview.hero_button') }}</v-btn>
        </RouterLink>

      </div>
    </section>

    <div class="carousel">
      <Carousel :autoplay="10000" pauseAutoplayOnHover wrapAround :transition="1500">
        <Slide v-for="slide in slides" :key="slide.id">
          <div class="carousel__item" :class="{ 'mobile-layout': isMobile }">
            <div class="image-container">
              <img :src="slide.image" :alt="'Slide ' + slide.id" class="slide-image">
            </div>
            <div class="info-box">
              <div class="text-container">
                <h1 class="title">{{ slide.title }}</h1>
                <h2 class="subtitle">{{ slide.country }}</h2>
                <p class="description">{{ $t('homeview.carousel_' + slide.title.toLowerCase() + '') }}</p>
              </div>
            </div>
          </div>
        </Slide>
        <template #addons>
          <Navigation>
            <template #prev>
              <div class="custom-arrow">‹</div>
            </template>
            <template #next>
              <div class="custom-arrow">›</div>
            </template>
          </Navigation>
          <Pagination />
        </template>
      </Carousel>
    </div>
  </div>
</template>



<style scoped lang="scss">
.main {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}
.hero {
  display: flex; // Enable Flexbox
  justify-content: center; // Center horizontally
  align-items: center; // Center vertically
  text-align: center;
  background-image: url('../assets/fake.png');
  height: 30vh;
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  

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