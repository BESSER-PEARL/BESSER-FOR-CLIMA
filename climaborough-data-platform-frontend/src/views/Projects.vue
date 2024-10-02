<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue';
import LoginForm from '../components/forms/LoginForm.vue'

import { useI18n } from 'vue-i18n';
const { locale } = useI18n();
const loggedIn = ref(false)

const checkIfLogged = () => {
  var userName = localStorage.getItem("login")
  if (userName) {
    loggedIn.value = true
  }
}
checkIfLogged()

function updateCSSVariable() {
  const screenWidth = window.innerWidth - 20;
  const numIcons = Math.floor(screenWidth / 240);
  const startingPosition = (screenWidth - numIcons * 240) / 2;
  document.documentElement.style.setProperty('--starting-position', `${startingPosition}px`);
  document.documentElement.style.setProperty('--starting-position', `140px`);
  document.documentElement.style.setProperty('--margin-right', `140px`);
}

onMounted(() => {
  updateCSSVariable();
  window.addEventListener('resize', updateCSSVariable);
});

onBeforeUnmount(() => {
  window.removeEventListener('resize', updateCSSVariable);
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
  <div v-if=loggedIn class="body">
    <a style="margin-left: 15px; margin-top: 60px; font-weight: bolder; font-size: 50px; color: #0177a9;">{{$t('projectview.title')}}</a>
    <div class="hub">
      <h1 style="margin-left: 80px; margin-top: 30px">{{$t('projectview.hub1')}}</h1>
      <div class="icon-container">

        <div v-for="project in projects" :key="project.id">
          <div v-if="project.hub == 1" class="icon">
            <RouterLink :to='"Dashboard/" + project.title'>
              <div>
                <img class="imagebutton" :src=project.image><br>
              </div>
            </RouterLink>
            <div class="info">
              <img :src=project.imageball>
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
      <h1 style="margin-left: 80px; margin-top: 30px;">{{$t('projectview.hub2')}}</h1>
      <div class="icon-container">
        <div v-for="project in projects" :key="project.id">
          <div v-if="project.hub == 2" class="icon">
            <RouterLink :to='"Dashboard/" + project.title'>
              <div>
                <img class="imagebutton" :src=project.image><br>
              </div>
            </RouterLink>
            <div class="info">
              <img :src=project.imageball>
              {{ project.title }}
            </div>
            <div class="grey">
              {{ project.type }}
            </div>
          </div>
        </div>

      </div>
    </div>


  </div>
  <div v-else class="login-warning">

    <p>{{ $t('denied_subheader') }}</p>
    <div class="login" style="padding: 40px;">
      <LoginForm />
    </div>

  </div>
</template>

<style lang="scss" scoped>



.body {
  margin: 10px;
  min-height: 90vh;
}

.icon-container {
  display: flex;
  margin-left: var(--starting-position);
  flex-wrap: wrap;
  // Add margin to the top of the container
  /* Center content horizontally */
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
  align-self: flex-start; // Align the image to the start of the container
}

.imagebutton:hover {
  cursor: pointer;
  /* Cursor on hover */
  box-shadow: 1px 1px 5px 5px rgba(0, 0, 0, 0.5);
}

.info {
  /* You can adjust the width as needed */
  flex: 1;
  /* Allow containers to grow and fill available space */
  display: flex;
  justify-content: left;
  align-items: center;
  /* Center items horizontally within each container */
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

.login-warning {
  width: 100%;
  height: calc(100vh - 40px);
  display: flex;
  justify-content: center;
  align-items: center;
  flex-direction: column;
  text-align: center;
  background-color: #f8f9fa;

  h2 {
    color: #dc3545;
    margin-bottom: 25px;
  }

  p {
    font-size: 1.2em;
    line-height: 1.5em;
    color: #343a40;

    .login-link {
      color: #0177a9;
      text-decoration: none;
    }
  }
}
</style>