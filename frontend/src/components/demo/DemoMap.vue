<script setup>
import "leaflet/dist/leaflet.css";
import { LMap, LTileLayer, LWmsTileLayer, LGeoJson } from "@vue-leaflet/vue-leaflet";
import { ref, reactive, watch } from "vue";
const props = defineProps({
  title: {
    type: String,
    default: "Map"
  }
})

const zoom = ref(15);
const center = ref([48.8566, 2.3522]); // Default center coordinates
const layers = ref([]);
const chosen_layers = ref([]);
const legend = ref(false);

function getItems() {
  // Mock layer data
  const mockLayers = [
    {
      title: "Population Density",
      type_spec: "wms",
      url: "https://demo.mapserver.org/population",
      name: "population_density",
      attribution: "Demo Data"
    },
    {
      title: "Temperature Zones",
      type_spec: "geojson",
      data: {
        type: "FeatureCollection",
        features: [
          {
            type: "Feature",
            geometry: {
              type: "Polygon",
              coordinates: [[[2.3, 48.8], [2.4, 48.8], [2.4, 48.9], [2.3, 48.9]]]
            }
          }
        ]
      },
      attribution: "Demo Data"
    }
  ];

  layers.value = mockLayers;
}

getItems();

function getGeoJsonOptions(index) {
  var colors = ['#FF0000', '#00FF00', '#0000FF', '#FFFF00', '#00FFFF']
  return {

    color: colors[index % colors.length],
    weight: 2,
    opacity: 1,

  };
}

function toggleLayer(layer) {
  let layer_contained = false
  for (var i = 0; i < chosen_layers.value.length; i++) {
    if (layer.title == chosen_layers.value[i].title) {
      layer_contained = true
    }
  }
  if (layer_contained) {
    chosen_layers.value.splice(chosen_layers.value.indexOf(layer), 1)
  } else {
    chosen_layers.value.push(layer)
  }
}

</script>


<template>

  <div class="map-body" @click="height">
    <div class="map-select">
      <v-item-group selected-class="bg-climaboroughBlue" multiple>
        <div class="text-caption mb-2">Select Layers</div>
        <v-item v-for="layer in layers" :key="layer.id" v-slot="{ selectedClass, toggle }">
          <v-chip :class="[selectedClass]" @click="{ toggle(); toggleLayer(layer) }" style="margin: 4px;">
            {{ layer.title }}
          </v-chip>
        </v-item>
      </v-item-group>

      <!--<v-select v-model="chosen_layers" :items="layers" item-title="label" label="Select Layer" return-object chips
        multiple></v-select>-->
    </div>
    <div class="map-body-body">
      <!--<div class="map">-->
      <l-map id="test" :useGlobalLeaflet=false ref="map" v-model:zoom="zoom" :center="center">
        <l-tile-layer url="https://tile.openstreetmap.org/{z}/{x}/{y}.png" layer-type="base" name="OpenStreetMap">
        </l-tile-layer>
        <div class="layer" v-for="(layer, index) in chosen_layers">
          <l-wms-tile-layer v-if="layer.type_spec == 'wms'" :key="layer.name" :url="layer.url" :layers="layer.name"
            :format="'image/png'" :transparent="true" :attribution="layer.attribution"></l-wms-tile-layer>
          <l-geo-json v-else-if="layer.type_spec == 'geojson'" :geojson="layer.data"
            :options-style="getGeoJsonOptions(index)"></l-geo-json>
        </div>
      </l-map>
    </div>
    <!-- <div v-if="legend" class="legend">
       <img v-if="legend" :src="layer.legend" style="width:250%" />

      </div>
    </div>-->

    <!-- Dropdown menu -->

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
  /* Ensure the select box only takes the space it needs */
  margin-bottom: 10px
}

.map-body-body {
  flex-grow: 1;
  /* Make this section take up the remaining space */
  width: 100%;
  display: flex;
}

.map-body-body>l-map {
  width: 100%;
  height: 100%;
}

.map {
  width: 100%;
  height: 100%;
}

.legend {
  width: 40%;
  height: 100%;
}
</style>