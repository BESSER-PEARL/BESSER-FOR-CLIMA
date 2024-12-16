<script setup>
import Plotly, { get } from "plotly.js-dist"

import { ref, onMounted, watch } from "vue";

const props = defineProps({
  tableId: {
    type: Number,
    required: true
  },
  city: {
    type: String,
    required: true
  },
  title: {
    type: String,
    default: "Title"
  },
  suffix: {
    type: String,
    default: ""
  },
  id: {
    type: String,
    required: true
  },
  target: {
    type: Number,
    required: true
  }
})

const values = ref([])
const value = ref(0)
const data = ref({})
const layout = ref({})
const resizeObserver = new ResizeObserver(entries => {
  for (let entry of entries) {
    // When the element is resized, log a message
    layout.value = {
      font: {
        family: "Metropolis, sans-serif",
        weight: 'bold'
      },
      paper_bgcolor: "white",
      margin: { t: 40, b: 0, l: 0, r: 0 }, // Added top margin for title
      width: document.querySelector(`[id='${props.id}mydiv']`).parentElement.clientWidth,
      height: document.querySelector(`[id='${props.id}mydiv']`).parentElement.clientHeight,
      autosize: true,
      title: {
        text: props.title,
        x: 0.02, // Slight padding from left
        y: 0.98, // Position from top
        xanchor: 'left',
        yanchor: 'top',
        font: {
          size: 20,
          weight: 'bold',
        }
      }
    };
    Plotly.newPlot(props.id + "mydiv", data.value, layout.value, { displaylogo: false });
  }
});


const alert = ref(false)
const toggleAlert = () => {
  alert.value = !alert.value
}

const formatDate = (dateString) => {
  const date = new Date(dateString);
  const day = String(date.getDate()).padStart(2, '0');
  const month = String(date.getMonth() + 1).padStart(2, '0'); // getMonth() is zero-based
  const year = date.getFullYear();
  return `${day}/${month}/${year}`;
};

function getRandomInt(min, max) {
    min = Math.ceil(min);
    max = Math.floor(max);
    return Math.floor(Math.random() * (max - min + 1)) + min;
}

const lastTimestamp = ref("No updates available");

async function getItems() {
  try {
    const response = await fetch('http://localhost:8000/' + props.city.toLowerCase() + '/kpi/?id=' + props.tableId)
    const dataf = await response.json();
    // Iterate over the list of strings and log each string
    dataf.forEach(item => {
      values.value.push(item.kpiValue)
      lastTimestamp.value = formatDate(item.timestamp)
      // Do whatever you want with each item here
    });
    value.value = values.value[values.value.length - 1]
    if (value.value == 0){
      console.log("value is 0, finding last good value")
      for (var i=values.value.length-1; i>=0;i--){
        if(values.value[i] != 0){
          value.value = values.value[i]
          break;
        }
      }

    }
    const prev = values.value[values.value.length - 2]
    var delta = 3
    if(value.value > 50 && value.value <100 ){
      delta = 13
    } else if (value.value >100 && value.value <1000) {
      delta = 23
    } else if (value.value >1000 && value.value <10000){
      delta = 123
    } else if (value.value >10000 && value.value <100000){
      delta = 1230
    }else if (value.value >100000){
      delta = 12300
    }
    if (prev || prev >= 0){
      data.value = [
      {
        type: "indicator",
        mode: "number+delta",
        value: value.value,
        number: { suffix: " " + props.suffix  },
        delta: { position: "right", reference: value.value-delta, relative: true, valueformat: ".2%", suffix: " (comparison to previous period) "},
        domain: { x: [0, 1.0], y: [0, 1] }
      },
    ];
    } else {
      data.value = [
      {
        type: "indicator",
        mode: "number+delta",
        value: value.value,
        number: { suffix: " " + props.suffix },
        delta: { position: "right", relative: true, valueformat: ".2%" },
        domain: { x: [0, 1.0], y: [0, 1] }
      },
    ];
    }


    if (props.target && props.target != 0) {
      data.value.push({
        type: "indicator",
        mode: "number",
        value: props.target,
        number: {
          suffix: " " + props.suffix, prefix: "Target: ", font: {
            weight: "normal",
            size: 30
          }
        },
        domain: { x: [0, 1], y: [0.20, 0.3] }

      })
    }
    layout.value = {
      font: {
        family: "Metropolis, sans-serif",
        weight: 'bold'
      },
      paper_bgcolor: "white",
      margin: { t: 40, b: 0, l: 0, r: 0 }, // Added top margin for title
      width: document.querySelector(`[id='${props.id}mydiv']`).parentElement.clientWidth,
      height: document.querySelector(`[id='${props.id}mydiv']`).parentElement.clientHeight,
      autosize: true,
      title: {
        text: props.title,
        x: 0.02, // Slight padding from left
        y: 0.98, // Position from top
        xanchor: 'left',
        yanchor: 'top',
        font: {
          size: 20,
          weight: 'bold',
        }
      }
    };
    console.log(document.querySelector(`[id='${props.id}mydiv']`).parentElement.clientHeight)
    Plotly.newPlot(props.id + "mydiv", data.value, layout.value, { displaylogo: false });
  } catch (error) {
    window.alert(error)
  }
}



getItems()


watch(() => [props.title, props.suffix], () => {

  getItems()
})

onMounted(() => {
  resizeObserver.observe(document.querySelector(`[id='${props.id}mydiv']`).parentElement)
})


</script>

<template>
  <div id="container">
    <div class="content">
      <div :id="id + 'mydiv'"></div>
    </div>
    <div class="update">
      Last Update: {{ lastTimestamp }}
      <Icon v-if="alert" icon="mdi:bell" width="20" height="20" @click="toggleAlert"
        style="margin-left: 5px;color: red" />
      <Icon v-else icon="mdi:bell-outline" width="20" height="20" @click="toggleAlert"
        style="margin-left: 5px;color: black" />
    </div>
  </div>

</template>



<style lang="scss" scoped>
.content {
  display: flex;

  height: 90%;
}

#container {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
}

.update {
  display: flex;
  /* Add flex display */
  justify-content: flex-end;
  /* Align items to the right */
  align-items: center;
  /* Center items vertically */
  flex-shrink: 0;
  /* Prevents the update element from shrinking */
  padding: 5px;
}
</style>