<script setup>
import ClimaboroughHeader from "./components/ClimaboroughHeader.vue"
import Footer from "./components/Footer.vue"
import { RouterView } from 'vue-router'
import { Icon } from "@iconify/vue";

</script>

<template>

  <body class="container">
    <div class="visible">
      <div class="top">
        <ClimaboroughHeader />
      </div>
  
      <div class="middle">
        <RouterView />
      </div>
    </div>

    <div class="bottom">
      <Footer />
    </div>

  </body>



</template>
<style lang="scss">

body {
  margin: 0;
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.visible {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.top {
  border-bottom: 3px solid #aec326;
}

.middle {
  flex: 1;
  overflow: auto; /* Allows scrolling within the middle content */
}

.bottom {
  background-color: #aec326;
 /* Adjust as needed */
  flex-shrink: 0; /* Ensures footer does not shrink */
}
</style>