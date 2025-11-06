<script setup>
import Plotly, { get } from "plotly.js-dist"
import MonthFilter from './MonthFilter.vue'
import apiService from '@/services/apiService';

import { ref, onMounted, watch, computed, nextTick } from "vue";

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
    required: false,
    default: () => `chart-${Math.random().toString(36).substr(2, 9)}`
  },
  monthFilter: {
    type: String,
    default: ""
  },
  minThreshold: {
    type: [String, Number],
    required: false,
    default: null
  },
  maxThreshold: {
    type: [String, Number],
    required: false,
    default: null
  }
})

const values = ref([])
const rawData = ref([])
const value = ref(0)
const data = ref({})
const layout = ref({})
const localMonthFilter = ref(props.monthFilter || "")
const isMounted = ref(false)

// Store fetched thresholds if not provided via props
const minThresholdValue = ref(null);
const maxThresholdValue = ref(null);

// Get effective threshold values (use props first, fallback to fetched values)
const effectiveMinThreshold = computed(() => props.minThreshold !== undefined && props.minThreshold !== null ? props.minThreshold : minThresholdValue.value);
const effectiveMaxThreshold = computed(() => props.maxThreshold !== undefined && props.maxThreshold !== null ? props.maxThreshold : maxThresholdValue.value);

// Check if we have actual thresholds to display
const hasThresholds = computed(() => {
  return (effectiveMinThreshold.value !== null && effectiveMinThreshold.value !== 'N/A') || 
         (effectiveMaxThreshold.value !== null && effectiveMaxThreshold.value !== 'N/A');
});

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
    // Only update if we have data
    if (filteredData.value && filteredData.value.length > 0) {
      updateChart();
    }
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
    // Fetch KPI details to get thresholds if not provided
    if (!props.minThreshold || !props.maxThreshold) {
      try {
        const kpiDetails = await apiService.getKPIById(props.tableId);
        if (kpiDetails && !props.minThreshold) {
          minThresholdValue.value = kpiDetails.min_threshold || null;
        }
        if (kpiDetails && !props.maxThreshold) {
          maxThresholdValue.value = kpiDetails.max_threshold || null;
        }
      } catch (e) {
        console.warn('Could not fetch KPI details for thresholds:', e);
      }
    }
    
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
    rawData.value = [];
    updateChart(); // Still call updateChart to show "No data" message
  }
}

function updateChart() {
  const filteredItems = filteredData.value;
  
  if (!filteredItems || filteredItems.length === 0) {
    // Don't render chart if no data
    return;
  }
  
  // Only render if component is mounted
  if (!isMounted.value) {
    return;
  }
  
  // Use nextTick to ensure DOM is updated
  nextTick(() => {
    const element = document.querySelector(`[id='${props.id}mydiv']`);
    if (!element) {
      // Element not in DOM yet (might be showing "No data" message)
      return;
    }
    
    // API returns 'value' not 'kpiValue'
    values.value = filteredItems.map(item => item.value ?? item.kpiValue);
    value.value = currentValue.value;
    
    const prev = previousValue.value;
    
    // Create indicator with real data - show delta only if we have previous value
    const indicator = {
      type: "indicator",
      mode: prev !== null ? "number+delta" : "number",
      value: value.value,
      number: { 
        suffix: " " + props.suffix,
        font: {
          size: 48,
          weight: 'bold',
          color: '#1a1a1a'
        }
      },
      domain: { x: [0, 1.0], y: [0.45, 1] }
    };
    
    if (prev !== null && prev >= 0) {
      indicator.delta = { 
        position: "bottom", 
        reference: prev, 
        relative: true, 
        valueformat: ".2%",
        font: {
          size: 20,
          weight: 'bold'
        },
        increasing: { 
          color: "#2E7D32",
          symbol: "▲"
        },
        decreasing: { 
          color: "#C62828",
          symbol: "▼"
        }
      };
    }
    
    data.value = [indicator];

    // Add threshold indicators if available with better styling
    if (hasThresholds.value) {
      let yPosition = 0.15;
      
      if (effectiveMaxThreshold.value !== null && effectiveMaxThreshold.value !== 'N/A') {
        data.value.push({
          type: "indicator",
          mode: "number",
          value: parseFloat(effectiveMaxThreshold.value),
          number: {
            font: {
              size: 18,
              weight: 'bold',
              color: "#FF6B6B"
            },
            suffix: " " + props.suffix,
            prefix: "Max: "
          },
          domain: { x: [0, 0.48], y: [yPosition, yPosition + 0.15] }
        });
      }
      
      if (effectiveMinThreshold.value !== null && effectiveMinThreshold.value !== 'N/A') {
        data.value.push({
          type: "indicator",
          mode: "number",
          value: parseFloat(effectiveMinThreshold.value),
          number: {
            font: {
              size: 18,
              weight: 'bold',
              color: "#4ECDC4"
            },
            suffix: " " + props.suffix,
            prefix: "Min: "
          },
          domain: { x: [0.52, 1], y: [yPosition, yPosition + 0.15] }
        });
      }
    }
    
    layout.value = {
      font: {
        family: "Metropolis, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
        weight: 'bold'
      },
      paper_bgcolor: "rgba(255, 255, 255, 0.95)",
      plot_bgcolor: "transparent",
      margin: { t: 50, b: 10, l: 20, r: 20 },
      width: element.parentElement?.clientWidth || 400,
      height: element.parentElement?.clientHeight || 300,
      autosize: true,
      title: {
        text: props.title,
        x: 0.03,
        y: 0.97,
        xanchor: 'left',
        yanchor: 'top',
        font: {
          size: 22,
          weight: 'bold',
          color: '#2c3e50',
          family: "Metropolis, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"
        }
      }
    };
    
    try {
      Plotly.newPlot(props.id + "mydiv", data.value, layout.value, { displaylogo: false });
    } catch (error) {
      console.error('Error rendering Plotly chart:', error);
    }
  });
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

// Watch for rawData changes to trigger chart update when mounted
watch(rawData, () => {
  if (isMounted.value && rawData.value && rawData.value.length > 0) {
    updateChart();
  }
})

// No longer need to watch filteredData since we fetch filtered data from server
// watch(filteredData, () => {
//   updateChart();
// })

onMounted(async () => {
  isMounted.value = true;
  
  // Wait for DOM to be fully updated
  await nextTick();
  
  const element = document.querySelector(`[id='${props.id}mydiv']`);
  if (element && element.parentElement) {
    resizeObserver.observe(element.parentElement);
    
    // Trigger initial render if we have data
    if (rawData.value && rawData.value.length > 0) {
      updateChart();
    }
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
  height: calc(95% - 30px);
  justify-content: center;
  align-items: center;
  background: transparent;
  position: relative;
}

.no-data-message {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  width: 100%;
  height: 100%;
  font-size: 20px;
  color: #999;
  font-weight: 600;
  gap: 12px;
  
  &::before {
    content: '📊';
    font-size: 48px;
    opacity: 0.5;
  }
}

#container {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
  background: transparent;
}

#chart {
  height: 98%;
}

.update {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  flex-shrink: 0;
  padding: 8px 12px;
  font-size: 11px;
  font-weight: 500;
  color: #666;
  height: 5%;
  min-height: 24px;
  background: transparent;
  border-top: 1px solid rgba(0, 0, 0, 0.06);
  
  svg {
    cursor: pointer;
    transition: all 0.2s ease;
    
    &:hover {
      transform: scale(1.15);
    }
  }
}
</style>