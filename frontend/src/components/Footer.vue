<script setup>
import { ref, onMounted } from 'vue'

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
  <div class="footer" :class="{ 'mobile': isMobile }">
    <div class="image-wrapper">
      <div class="first-level">
        <div class="column">
          <img src="/climaborough-logo-white-300x84.png" alt="Your Image" class="footer-image">
        </div>
        <div class="column">
          <img src="/EN_Co-fundedbytheEU_RGB_POS.png" alt="Alt" class="eu-logo">
        </div>
      </div>
    </div>

    <div class="second-level">
      <div class="column">
        <p>{{ $t('footer.column1', ['**', '**']) }}</p>
      </div>
      <div class="column">
        <p>{{ $t('footer.column2') }}</p>
      </div>
    </div>

    <div class="third-level">
      <div class="links-container">
        <router-link to="/tos">
          <span class="footer-text">{{ $t('footer.tos') }}</span>
        </router-link>
        <span class="separator"></span>
        <span class="footer-text">{{ $t('footer.socialMedia') }}</span>
      </div>
      <div class="social-icons">
        <a href="https://www.linkedin.com/company/climaborough/" target="_blank">
          <Icon icon="fa-brands:linkedin" width="30" height="30" style="color: white" />
        </a>
        <a href="https://www.facebook.com/climaborough" target="_blank">
          <Icon icon="fa6-brands:facebook-f" width="30" height="30"
            href="https://www.linkedin.com/company/climaborough/" style="color: white" />
        </a>
        <a href="https://www.instagram.com/climaborough/" target="_blank">
          <Icon icon="fa-brands:instagram" width="30" height="30" style="color: white" />
        </a>
        <a href="https://twitter.com/Climaborough" target="_blank">
          <Icon icon="fa6-brands:x-twitter" width="30" height="30" style="color: white" />
        </a>
        <a href="https://www.youtube.com/@Climaborough" target="_blank">
          <Icon icon="fa6-brands:youtube" width="30" height="30" style="color: white" />
        </a>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.footer {
  background-color: #aec326;
  width: 100%;
  margin-top: auto;

  &.mobile {
    .first-level {
      flex-direction: column;
      margin: 10px;
      gap: 20px;
      align-items: center;

      .column {
        padding: 0;
        text-align: center;
      }
    }

    .second-level {
      flex-direction: column;
      margin: 10px;
      gap: 20px;

      .column {
        padding: 10px;
        text-align: center;

        p {
          font-size: 14px;
        }
      }
    }

    .third-level {
      flex-direction: column;
      gap: 15px;
      padding: 15px;

      .links-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 10px;
      }

      .separator {
        display: none;
      }

      .social-icons {
        display: flex;
        justify-content: center;
        gap: 15px;
        
        a {
          padding: 5px;
        }
      }
    }

    .footer-image {
      width: 200px;
    }

    .eu-logo {
      width: 250px;
    }
  }
}

.first-level {
  height: 10%;
  display: flex;
  padding-top: 20px;
  margin: 20px 100px 10px 60px
}

.image-wrapper {
  padding: 5px;
  /* Adjust the padding as needed */
}

.footer-image {
  width: 230px;
}

.second-level {
  height: 85%;
  display: flex;
  padding-bottom: 15px;
  margin: 0px 100px 10px 60px
}

.third-level {
  height: 5%;
  display: flex;
  border-top: 4px solid rgba(255, 255, 255, 0.3);
  padding-top: 10px;
  text-align: right;
  justify-content: right;
  padding: 10px;
  align-items: center;
}

.column {
  flex: 1;
  padding-left: 60px;
  padding-right: 60px;
}

.column p {
  font-weight: normal;
  
  strong {
    font-weight: bold;
  }
}

a {
  padding: 7px;
}

.footer {
  background-color: #aec326;
  width: 100%;
  margin-top: auto;
}

.footer-text {
  font-weight: bold;
  color: white;
  font-size: large;
}

// Make links more touch-friendly on mobile
@media (max-width: 768px) {
  a {
    padding: 8px;
    margin: 2px;
    display: inline-block;

    &:active {
      opacity: 0.7;
    }
  }

  .social-icons {
    a {
      padding: 10px;
    }
  }
}

// Add smooth transitions
.first-level,
.second-level,
.third-level {
  transition: all 0.3s ease;
}

// Add hardware acceleration for smoother performance
.footer {
  transform: translateZ(0);
  -webkit-transform: translateZ(0);
}

.eu-logo {
  width: 250px; // Default size for mobile
  @media (min-width: 769px) {
    width: 250px;
  }
}
</style>
