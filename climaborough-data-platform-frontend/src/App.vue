<script setup>
import ClimaboroughHeader from "./components/ClimaboroughHeader.vue"
import Footer from "./components/Footer.vue"
import { RouterView } from 'vue-router'
import { Icon } from "@iconify/vue";

</script>

<template>
  <div class="app-container">
    <ClimaboroughHeader />
    <router-view></router-view>
    <Footer />
  </div>
</template>

<style>
.app-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

body {
  margin: 0;
  padding: 0;
  overflow-x: hidden;
}
</style>