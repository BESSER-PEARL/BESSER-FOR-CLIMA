<script setup>
import "leaflet/dist/leaflet.css";
import { LMap, LTileLayer, LWmsTileLayer, LGeoJson } from "@vue-leaflet/vue-leaflet";
import { ref, reactive, watch } from "vue";
import apiService from '../services/apiService';

const props = defineProps({
  city: {
    type: String,
    required: true
  }
});

const zoom = ref(15);
const layers = ref([]);
const chosen_layers = ref([]);
const legend = ref(true);
const center = ref([49.5203, 5.890186]);

// City-specific configuration (lowercase keys for case-insensitive matching)
const cityConfig = {
  cascais: { center: [38.696912, -9.422269], zoom: 15, legend: false },
  torino: { center: [45.070602, 7.682152], zoom: 12.5, legend: false },
  differdange: { center: [49.5244, 5.8932], zoom: 14, legend: true },
  sofia: { center: [42.6977, 23.3219], zoom: 13, legend: true },
  athens: { center: [37.9838, 23.7275], zoom: 13, legend: true },
  grenoble: { center: [45.1885, 5.7245], zoom: 13, legend: true },
  maribor: { center: [46.5547, 15.6459], zoom: 13, legend: true },
  ioannina: { center: [39.6679, 20.8509], zoom: 13, legend: true } 
};

// Apply city-specific config (case-insensitive)
const cityKey = props.city?.toLowerCase();
if (cityKey && cityConfig[cityKey]) {
  center.value = cityConfig[cityKey].center;
  zoom.value = cityConfig[cityKey].zoom;
  legend.value = cityConfig[cityKey].legend;
}

async function getItems() {
  try {
    // Use new API service method instead of legacy endpoint
    const data = await apiService.getMapDataByCityCode(props.city);
    
    // Create a Set to track unique titles
    const uniqueTitles = new Set();
    
    // Filter out layers without names and prevent duplicates
    layers.value = data
      .filter(item => {
        // Skip items without a title or with empty title
        if (!item.title || item.title.trim() === '') {
          return false;
        }
        
        // Skip duplicates by checking if we've seen this title before
        if (uniqueTitles.has(item.title)) {
          return false;
        }
        
        // Add this title to our tracking Set and keep the item
        uniqueTitles.add(item.title);
        return true;
      })
      .map(item => ({
        ...item,
        label: item.title,
        attribution: "Attribution for Layer 1",
        legend: ""
      }));
  } catch (error) {
    console.error("Error fetching map data:", error);
  }
}

getItems();

function getGeoJsonOptions(index) {
  const colors = ['#FF0000', '#00FF00', '#0000FF', '#FFFF00', '#00FFFF'];
  return {
    color: colors[index % colors.length],
    weight: 2,
    opacity: 1
  };
}

function toggleLayer(layer) {
  const index = chosen_layers.value.findIndex(l => l.title === layer.title);
  if (index !== -1) {
    chosen_layers.value.splice(index, 1);
  } else {
    chosen_layers.value.push(layer);
  }
}
</script>

<template>
  <div class="map-body">
    <div class="map-select">
      <v-item-group selected-class="bg-climaboroughBlue" multiple>
        <div class="text-caption mb-2">Select Layers</div>
        <v-item v-for="layer in layers" :key="layer.id" v-slot="{ selectedClass, toggle }">
          <v-chip :class="[selectedClass]" @click="{ toggle(); toggleLayer(layer) }" style="margin: 4px;">
            {{ layer.title }}
          </v-chip>
        </v-item>
      </v-item-group>
    </div>
    <div class="map-body-body">
      <l-map id="test" :useGlobalLeaflet="false" ref="map" v-model:zoom="zoom" :center="center">
        <l-tile-layer url="https://tile.openstreetmap.org/{z}/{x}/{y}.png" layer-type="base" name="OpenStreetMap" />
        <div class="layer" v-for="(layer, index) in chosen_layers" :key="layer.id">
          <l-wms-tile-layer
            v-if="layer.type === 'wms'"
            :url="layer.url"
            :layers="layer.layer_name"
            format="image/png"
            transparent
            :attribution="layer.attribution"
          />
          <l-geo-json
            v-else-if="layer.type === 'geojson'"
            :geojson="layer.data"
            :options-style="getGeoJsonOptions(index)"
          />
        </div>
      </l-map>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.map-body {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.map-select {
  flex-shrink: 0;
  margin-bottom: 10px;
}

.map-body-body {
  flex-grow: 1;
  width: 100%;
  display: flex;
}

.map-body-body > l-map {
  width: 100%;
  height: 100%;
}
</style>