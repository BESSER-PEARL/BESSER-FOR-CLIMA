<script setup>
import "leaflet/dist/leaflet.css";
import { LMap, LTileLayer, LWmsTileLayer, LGeoJson } from "@vue-leaflet/vue-leaflet";
import { ref, reactive, watch } from "vue";
const props = defineProps({
  city: {
    type: String,
    required: true
  }
})

const zoom = ref(15);
const tileLayerUrl = "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png";
const wmsTileLayerUrl = "https://your-wms-tile-layer-url"; // Set your WMS tile layer URL

const layers = ref([
  /* { label: "None", name: "", url: "", attribution: "" },
   { label: "Solar Potential", name: "1813", url: "https://wms.geoportail.lu/public_map_layers/service", attribution: "Attribution for Layer 1", legend: "https://wms.geoportail.lu/public_map_layers/service?format=image%2Fpng&layer=1813&sld_version=1.1.0&request=GetLegendGraphic&service=WMS&version=1.1.1&styles=" },
   { label: "Solar Potential on large buildings", name: "1818", url: "https://wms.geoportail.lu/public_map_layers/service", attribution: "Attribution for Layer 1", legend: "https://wms.geoportail.lu/public_map_layers/service?format=image%2Fpng&layer=1818&sld_version=1.1.0&request=GetLegendGraphic&service=WMS&version=1.1.1&styles=" }
   // Add more layers as needed*/
])

//const layer = ref({ label: "Solar Potential", name: "1813", url: "https://wms.geoportail.lu/public_map_layers/service", attribution: "Attribution for Layer 1", legend: "https://wms.geoportail.lu/public_map_layers/service?format=image%2Fpng&layer=1813&sld_version=1.1.0&request=GetLegendGraphic&service=WMS&version=1.1.1&styles=" })
const chosen_layers = ref([])

const legend = ref(true)

const center = ref([49.520300, 5.890186])

if (props.city == "Cascais") {
  center.value = [38.696912, -9.422269]
  legend.value = false
} else if (props.city == "Torino") {
  center.value = [45.070602, 7.682152]
  layers.value = reactive([
    { label: "None", name: "", url: "", attribution: "" } // Add more layers as needed
  ])
  legend.value = false
  zoom.value = 12.5
}
const items = ref([])

const isGeojson = ref(false)
const isWMS = ref(false)

async function getItems() {
  try {
    const response = await fetch('http://localhost:8000/' + props.city.toLowerCase() + '/mapdata/')
    const data = await response.json();
    console.log("received response")
    console.log(data)
    // Iterate over the list of strings and log each string
    layers.value = []
    data.forEach(item => {
      console.log(item)
      let layerObject = item
      layerObject.label = item.title
      layerObject.attribution = "Attribution for Layer 1"
      layerObject.legend = ""
      layers.value.push(layerObject)
    });

  } catch (error) {
    window.alert(error)
  }
}

getItems()

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