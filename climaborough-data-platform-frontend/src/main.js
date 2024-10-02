
import { createApp } from 'vue'
import App from './App.vue'
import './assets/main.css'
import './assets/global.css';  // Import your global CSS
import router from './router'
import 'vuetify/styles'
import { createVuetify } from 'vuetify'

import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'

import '@mdi/font/css/materialdesignicons.css'

import VueApexCharts from 'vue3-apexcharts';

import { Icon } from '@iconify/vue';

import i18n from './assets/lang/i18n.js'

const myCustomLightTheme = {
  dark: false,
  colors: {
    climaboroughBlue: "#0177a9",
    climaboroughGreen: "#aec326"
  },
  variables: {

  }
}

const app = createApp(App)
app.provide('apiUrl', 'http://localhost:8000')

const vuetify = createVuetify({
  components,
  directives,
  iconfont: 'md',
  theme: {
    defaultTheme: 'myCustomLightTheme',
    themes: {
      myCustomLightTheme,
    },
  }
})

app.use(router).use(vuetify).use(i18n)
app.component('VueApexCharts', VueApexCharts)
window.Apex.chart = { fontFamily: "Metropolis, sans-serif" };
app.component('Icon', Icon)
app.mount('#app')
