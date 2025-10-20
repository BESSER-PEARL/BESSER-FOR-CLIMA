<script setup>

import 'vue3-carousel/dist/carousel.css'
import { Carousel, Slide, Pagination, Navigation } from 'vue3-carousel'
import { RouterLink } from 'vue-router';


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

</script>

<template>
  <div class="main">
    <section class="hero">
      <div class="hero-content">
        <h1>{{ $t('home.title') }}</h1>
        <p class="subtitle">{{ $t('home.subtitle') }}</p>
        <div class="hero-buttons">
          <router-link to="/projects" class="cta-button">
            {{ $t('home.explore') }}
          </router-link>
          <router-link to="/about" class="secondary-button">
            {{ $t('home.learn_more') }}
          </router-link>
        </div>
      </div>
    </section>

    <section class="carousel-section">
      <h2>{{ $t('home.carousel_title') }}</h2>
      <div class="carousel">
        <Carousel :items-to-show="1" :wrap-around="true" :autoplay="3000">
          <Slide v-for="slide in slides" :key="slide.id">
            <div class="carousel-slide">
              <img :src="slide.image" :alt="slide.title">
              <div class="slide-content">
                <h3>{{ slide.title }}</h3>
                <p>{{ slide.description }}</p>
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
    </section>

    <section class="features">
      <div class="feature-card">
        <Icon icon="mdi:city" width="48" height="48" />
        <h3>{{ $t('home.feature1_title') }}</h3>
        <p>{{ $t('home.feature1_desc') }}</p>
      </div>
      <div class="feature-card">
        <Icon icon="mdi:earth" width="48" height="48" />
        <h3>{{ $t('home.feature2_title') }}</h3>
        <p>{{ $t('home.feature2_desc') }}</p>
      </div>
      <div class="feature-card">
        <Icon icon="mdi:chart-line" width="48" height="48" />
        <h3>{{ $t('home.feature3_title') }}</h3>
        <p>{{ $t('home.feature3_desc') }}</p>
      </div>
    </section>
  </div>
</template>

<style scoped lang="scss">
.main {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.hero {
  height: 60vh;
  background: linear-gradient(rgba(0, 0, 0, 0.5), rgba(0, 0, 0, 0.5)), url('/path-to-your-hero-image.jpg');
  background-size: cover;
  background-position: center;
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  color: white;

  .hero-content {
    max-width: 800px;
    padding: 0 20px;

    h1 {
      font-size: 3.5rem;
      margin-bottom: 1rem;
      font-weight: bold;
    }

    .subtitle {
      font-size: 1.5rem;
      margin-bottom: 2rem;
      line-height: 1.6;
    }

    .hero-buttons {
      display: flex;
      gap: 20px;
      justify-content: center;

      a {
        padding: 15px 30px;
        border-radius: 30px;
        font-weight: bold;
        text-decoration: none;
        transition: all 0.3s ease;
      }

      .cta-button {
        background-color: #aec326;
        color: white;

        &:hover {
          background-color: darken(#aec326, 10%);
          transform: translateY(-2px);
        }
      }

      .secondary-button {
        background-color: transparent;
        border: 2px solid white;
        color: white;

        &:hover {
          background-color: white;
          color: #2c3e50;
        }
      }
    }
  }
}

.carousel-section {
  padding: 4rem 2rem;
  background-color: #f8f9fa;

  h2 {
    text-align: center;
    font-size: 2.5rem;
    color: #2c3e50;
    margin-bottom: 2rem;
  }
}

.carousel-slide {
  position: relative;
  height: 400px;
  
  img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    border-radius: 10px;
  }

  .slide-content {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    padding: 2rem;
    background: linear-gradient(transparent, rgba(0,0,0,0.8));
    color: white;
    border-radius: 0 0 10px 10px;

    h3 {
      font-size: 1.8rem;
      margin-bottom: 0.5rem;
    }

    p {
      font-size: 1.1rem;
      line-height: 1.6;
    }
  }
}

.custom-arrow {
  font-size: 60px;
  font-weight: bold;
  color: white;
  cursor: pointer;
  padding: 10px;
  user-select: none;
  text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
  transition: transform 0.3s ease;

  &:hover {
    transform: scale(1.1);
  }
}

.features {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
  padding: 4rem 2rem;
  background-color: white;

  .feature-card {
    text-align: center;
    padding: 2rem;
    border-radius: 10px;
    background-color: white;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    transition: transform 0.3s ease;

    &:hover {
      transform: translateY(-5px);
    }

    .icon {
      color: #aec326;
      margin-bottom: 1rem;
    }

    h3 {
      font-size: 1.5rem;
      color: #2c3e50;
      margin-bottom: 1rem;
    }

    p {
      color: #666;
      line-height: 1.6;
    }
  }
}

@media (max-width: 768px) {
  .hero {
    height: 70vh;

    .hero-content {
      h1 {
        font-size: 2.5rem;
      }

      .subtitle {
        font-size: 1.2rem;
      }
    }
  }

  .hero-buttons {
    flex-direction: column;
    gap: 10px;
  }

  .carousel-slide {
    height: 300px;
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