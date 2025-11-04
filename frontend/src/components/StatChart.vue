<script setup>
import Plotly, { get } from "plotly.js-dist"
import MonthFilter from './MonthFilter.vue'
import apiService from '@/services/apiService';

import { ref, onMounted, watch, computed } from "vue";

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
  },
  monthFilter: {
    type: String,
    default: ""
  }
})

const values = ref([])
const rawData = ref([])
const value = ref(0)
const data = ref({})
const layout = ref({})
const localMonthFilter = ref(props.monthFilter || "")

// Computed property to filter data based on selected month
// Computed property - simplified since filtering is now done server-side
const filteredData = computed(() => {
  // Server-side filtering handles the month filter, so just return raw data
  return rawData.value;
});

// Computed property for the current KPI value based on filtered data
const currentValue = computed(() => {
  const data = filteredData.value;
  if (!data.length) return 0;
  
  // API returns 'value' not 'kpiValue'
  const latestValue = data[data.length - 1]?.value ?? data[data.length - 1]?.kpiValue ?? 0;
  if (latestValue === 0) {
    // Find last non-zero value
    for (let i = data.length - 1; i >= 0; i--) {
      const val = data[i].value ?? data[i].kpiValue;
      if (val !== 0) {
        return val;
      }
    }
  }
  return latestValue;
});

// Computed property for the previous value for delta calculation
const previousValue = computed(() => {
  const data = filteredData.value;
  if (data.length < 2) return null;
  // API returns 'value' not 'kpiValue'
  return data[data.length - 2]?.value ?? data[data.length - 2]?.kpiValue;
});

// Computed property for the last timestamp
const lastTimestamp = computed(() => {
  const data = filteredData.value;
  if (!data.length) return "No updates available";
  return formatDate(data[data.length - 1].timestamp);
});
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

async function getItems() {
  try {
    // Use server-side filtering if month filter is active
    const dataf = localMonthFilter.value
      ? await apiService.getKPIValuesByMonth(props.tableId, localMonthFilter.value)
      : await apiService.getKPIValues(props.tableId);
    
    // Store all raw data
    rawData.value = dataf;
    console.log('StatChart raw data for tableId', props.tableId, ':', dataf);
    
    // Process data for visualization
    updateChart();
  } catch (error) {
    console.error('Error fetching KPI data:', error);
    window.alert(error)
  }
}

function updateChart() {
  const filteredItems = filteredData.value;
  // API returns 'value' not 'kpiValue'
  values.value = filteredItems.map(item => item.value ?? item.kpiValue);
  value.value = currentValue.value;
  
  var delta = 3;
  if(value.value > 50 && value.value < 100) {
    delta = 13;
  } else if (value.value > 100 && value.value < 1000) {
    delta = 23;
  } else if (value.value > 1000 && value.value < 10000) {
    delta = 123;
  } else if (value.value > 10000 && value.value < 100000) {
    delta = 1230;
  } else if (value.value > 100000) {
    delta = 12300;
  }
  
  const prev = previousValue.value;
  
  if (prev !== null && prev >= 0) {
    data.value = [
      {
        type: "indicator",
        mode: "number+delta",
        value: value.value,
        number: { suffix: " " + props.suffix },
        delta: { position: "right", reference: prev, relative: true, valueformat: ".2%", suffix: " (comparison to previous period) "},
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
        suffix: " " + props.suffix, 
        prefix: "Target: ", 
        font: {
          weight: "normal",
          size: 30
        }
      },
      domain: { x: [0, 1], y: [0.20, 0.3] }
    });
  }
  
  layout.value = {
    font: {
      family: "Metropolis, sans-serif",
      weight: 'bold'
    },
    paper_bgcolor: "white",
    margin: { t: 40, b: 0, l: 0, r: 0 },
    width: document.querySelector(`[id='${props.id}mydiv']`)?.parentElement?.clientWidth || 400,
    height: document.querySelector(`[id='${props.id}mydiv']`)?.parentElement?.clientHeight || 300,
    autosize: true,
    title: {
      text: props.title,
      x: 0.02,
      y: 0.98,
      xanchor: 'left',
      yanchor: 'top',
      font: {
        size: 20,
        weight: 'bold',
      }
    }
  };
  
  if (document.querySelector(`[id='${props.id}mydiv']`)) {
    Plotly.newPlot(props.id + "mydiv", data.value, layout.value, { displaylogo: false });
  }
}



// Handle month filter changes
const handleMonthChange = (monthValue) => {
  localMonthFilter.value = monthValue;
  updateChart();
};

getItems()

watch(() => [props.title, props.suffix], () => {
  getItems()
})

// Watch for monthFilter changes and re-fetch data with server-side filtering
watch(() => props.monthFilter, (newFilter) => {
  localMonthFilter.value = newFilter;
  getItems(); // Re-fetch data from server with new filter
})

// No longer need to watch filteredData since we fetch filtered data from server
// watch(filteredData, () => {
//   updateChart();
// })

onMounted(() => {
  const element = document.querySelector(`[id='${props.id}mydiv']`);
  if (element && element.parentElement) {
    resizeObserver.observe(element.parentElement);
  } else {
    console.warn(`StatChart: Could not find element with id '${props.id}mydiv'`);
  }
})


</script>

<template>
  <div id="container">
    <!-- <MonthFilter 
      v-if="!monthFilter"
      v-model="localMonthFilter"
      @month-change="handleMonthChange"
      class="month-filter-component"
    /> -->
    <div class="content">
      <div v-if="filteredData.length === 0" class="no-data-message">
        No data
      </div>
      <div v-else :id="id + 'mydiv'"></div>
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
.month-filter-component {
  padding: 5px;
  background: #f8f9fa;
  border-radius: 5px;
  margin-bottom: 5px;
}

.content {
  display: flex;
  height: calc(90% - 30px); // Adjust height to account for month filter
}

#container {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
}

#chart {
  height: 98%;
}

.update {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  flex-shrink: 0;
  padding: 2px 5px;
  font-size: 10px;
  color: #666;
  height: 5%;
  min-height: 20px;
}
</style>