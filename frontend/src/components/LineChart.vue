<script setup>
import { ref, computed, watch } from "vue";
import apiService from '@/services/apiService';

const props = defineProps({
  tableId: {
    type: Number,
    required: false,
    default: null
  },
  city: {
    type: String,
    required: true
  },
  title: {
    type: String,
    default: "Title"
  },
  xtitle: {
    type: String,
    default: "Date"
  },
  ytitle: {
    type: String,
    default: "Values"
  },
  color: {
    type: String,
    default: '#086494'
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

const chartType = ref('line'); // Reactive chart type

// Store fetched thresholds if not provided via props
const minThresholdValue = ref(null);
const maxThresholdValue = ref(null);

// Track if data has categories
const hasCategories = ref(false);
const categoryColors = ref({});

// Get effective threshold values (use props first, fallback to fetched values)
const effectiveMinThreshold = computed(() => props.minThreshold !== undefined && props.minThreshold !== null ? props.minThreshold : minThresholdValue.value);
const effectiveMaxThreshold = computed(() => props.maxThreshold !== undefined && props.maxThreshold !== null ? props.maxThreshold : maxThresholdValue.value);

// Check if we have actual thresholds to display
const hasThresholds = computed(() => {
  return (effectiveMinThreshold.value !== null && effectiveMinThreshold.value !== 'N/A') || 
         (effectiveMaxThreshold.value !== null && effectiveMaxThreshold.value !== 'N/A');
});

// Determine if current chart type supports stacking
const supportsStacking = computed(() => {
  return hasCategories.value && (chartType.value === 'bar' || chartType.value === 'area');
});

const chartOptions = computed(() => {
  const options = {
    chart: {
      type: chartType.value, // Use the reactive chartType
      zoom: {
        enabled: true
      },
      stacked: supportsStacking.value, // Enable stacking for bar and area charts with categories
    },
    dataLabels: {
      enabled: false
    },
    stroke: {
      curve: chartType.value === 'area' ? 'smooth' : 'straight',
      width: chartType.value === 'area' ? 2 : (supportsStacking.value ? 0 : 2.2)
    },
    title: {
      text: props.title,
      style: {
        fontSize: '20px',
        fontWeight: 'bold'
      },
      offsetY: -8,
    },
    grid: {
      row: {
        colors: ['#f3f3f3', 'transparent'],
        opacity: 0.5
      },
    },
    xaxis: {
      type: 'datetime',
      title: { text: props.xtitle }
    },
    yaxis: {
      title: { text: props.ytitle }
    },
    fill: {
      opacity: chartType.value === 'area' && supportsStacking.value ? 0.8 : 1
    },
    legend: {
      position: 'top',
      horizontalAlign: 'left'
    },
    plotOptions: {
      bar: {
        horizontal: false,
        columnWidth: '70%',
      }
    }
  };

  return options;
});

const values = ref([]);
const valuemappedtotime = ref([]);
const timestamps = ref([]);
const rawData = ref([]);
const localMonthFilter = ref(props.monthFilter || "");

// Initialize series ref BEFORE processFilteredData uses it
const series = ref([
  {
    name: "KPI Values",
    data: [],
    color: props.color,
  }
]);

// Color palette for categories
const categoryColorPalette = [
  '#086494', '#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', 
  '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E2', '#F8B739'
];

// Helper function to generate color for a category
function getCategoryColor(category, index) {
  if (!categoryColors.value[category]) {
    categoryColors.value[category] = categoryColorPalette[index % categoryColorPalette.length];
  }
  return categoryColors.value[category];
}

// Computed property - simplified since filtering is now done server-side
const filteredData = computed(() => {
  // Server-side filtering handles the month filter, so just return raw data
  return rawData.value;
});

const formatDate = (dateString) => {
  const date = new Date(dateString);
  const day = String(date.getDate()).padStart(2, '0');
  const month = String(date.getMonth() + 1).padStart(2, '0'); // getMonth() is zero-based
  const year = date.getFullYear();
  return `${day}/${month}/${year}`;
};

const lastTimestamp = computed(() => {
  if (timestamps.value.length > 0) {
    const lastTimestamp = timestamps.value[timestamps.value.length - 1];
    return formatDate(lastTimestamp);
  }
  return 'No updates available';
});

async function getItems() {
  try {
    if (!props.tableId) {
      console.warn('LineChart: No tableId (kpi_id) provided');
      rawData.value = [];
      processFilteredData();
      return;
    }
    
    // console.log('LineChart getItems - localMonthFilter:', localMonthFilter.value);
    
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
    const data = localMonthFilter.value 
      ? await apiService.getKPIValuesByMonth(props.tableId, localMonthFilter.value)
      : await apiService.getKPIValues(props.tableId);
    
    console.log('LineChart fetched data count:', data.length);
    rawData.value = data; // Store raw data
    processFilteredData();
  } catch (error) {
    console.error('Error fetching KPI values:', error);
    rawData.value = [];
    processFilteredData();
  }
}

function processFilteredData() {
  values.value = [];
  timestamps.value = [];
  valuemappedtotime.value = [];
  
  if (!filteredData.value || !Array.isArray(filteredData.value)) {
    return;
  }
  
  // Check if data has categories
  hasCategories.value = filteredData.value.some(item => item.category_label);
  
  if (hasCategories.value && (chartType.value === 'bar' || chartType.value === 'area')) {
    // Process data with categories for stacked charts
    processStackedData();
  } else if (hasCategories.value && chartType.value === 'line') {
    // Process data with categories for line chart (multiple lines)
    processMultiLineData();
  } else {
    // Process data without categories (standard single series)
    processSingleSeriesData();
  }
  
  // Add threshold lines if applicable (only for non-stacked charts)
  if (hasThresholds.value && !supportsStacking.value) {
    addThresholdLines();
  }
}

function processSingleSeriesData() {
  filteredData.value.forEach(item => {
    const val = item.value ?? item.kpiValue ?? 0;
    values.value.push(val);
    timestamps.value.push(item.timestamp);
    valuemappedtotime.value.push({ x: item.timestamp, y: val });
  });
  
  series.value = [
    {
      name: "KPI Values",
      data: valuemappedtotime.value,
      color: props.color,
    }
  ];
}

function processMultiLineData() {
  // Group data by category
  const categoryData = {};
  
  filteredData.value.forEach(item => {
    const val = item.value ?? item.kpiValue ?? 0;
    const category = item.category_label || 'Uncategorized';
    
    if (!categoryData[category]) {
      categoryData[category] = [];
    }
    
    categoryData[category].push({ x: item.timestamp, y: val });
    timestamps.value.push(item.timestamp);
  });
  
  // Create series for each category
  series.value = Object.keys(categoryData).map((category, index) => ({
    name: category,
    data: categoryData[category],
    color: getCategoryColor(category, index)
  }));
}

function processStackedData() {
  // Group data by timestamp and category for stacking
  const timeSeriesMap = {};
  const categories = new Set();
  
  filteredData.value.forEach(item => {
    const val = item.value ?? item.kpiValue ?? 0;
    const timestamp = item.timestamp;
    const category = item.category_label || 'Uncategorized';
    
    categories.add(category);
    
    if (!timeSeriesMap[timestamp]) {
      timeSeriesMap[timestamp] = {};
    }
    
    // Aggregate values for same timestamp and category
    if (!timeSeriesMap[timestamp][category]) {
      timeSeriesMap[timestamp][category] = 0;
    }
    timeSeriesMap[timestamp][category] += val;
  });
  
  // Convert to series format
  const categoriesArray = Array.from(categories);
  series.value = categoriesArray.map((category, index) => {
    const data = Object.keys(timeSeriesMap).map(timestamp => ({
      x: timestamp,
      y: timeSeriesMap[timestamp][category] || 0
    }));
    
    return {
      name: category,
      data: data,
      color: getCategoryColor(category, index)
    };
  });
  
  // Update timestamps for display
  timestamps.value = Object.keys(timeSeriesMap);
}

function addThresholdLines() {
  const timeRange = valuemappedtotime.value.map(point => point.x);
  
  if (effectiveMaxThreshold.value !== null && effectiveMaxThreshold.value !== 'N/A') {
    const maxVal = parseFloat(effectiveMaxThreshold.value);
    series.value.push({
      name: `Max Threshold: ${effectiveMaxThreshold.value}`,
      data: timeRange.map(time => ({ x: time, y: maxVal })),
      color: '#FF6B6B',
      type: 'line',
      strokeWidth: [2],
      strokeDashArray: 5
    });
  }
  
  if (effectiveMinThreshold.value !== null && effectiveMinThreshold.value !== 'N/A') {
    const minVal = parseFloat(effectiveMinThreshold.value);
    series.value.push({
      name: `Min Threshold: ${effectiveMinThreshold.value}`,
      data: timeRange.map(time => ({ x: time, y: minVal })),
      color: '#4ECDC4',
      type: 'line',
      strokeWidth: [2],
      strokeDashArray: 5
    });
  }
}

getItems();

watch(() => [props.title, props.xtitle, props.ytitle, props.color], () => {
  processFilteredData();
});

// Watch for chartType changes to re-process data (for switching between stacked/unstacked)
watch(chartType, () => {
  processFilteredData();
});

// Watch for monthFilter changes and re-fetch data with server-side filtering
watch(() => props.monthFilter, (newFilter) => {
  console.log('LineChart watch triggered - monthFilter changed to:', newFilter);
  localMonthFilter.value = newFilter;
  getItems(); // Re-fetch data from server with new filter
});

// Remove the filteredData watcher as we now fetch filtered data from server
// watch(filteredData, () => {
//   processFilteredData();
// });
</script>

<template>
  <div id="container">
    <div id="chart">
      <VueApexCharts type="line" height="100%" :options="chartOptions" :series="series"></VueApexCharts>
    </div>
    <div class="bottom-controls">
      <select v-model="chartType" class="chart-select">
        <option value="line">Lines</option>
        <option value="bar">Bars</option>
        <option value="area">Areas</option>
      </select>
      <div class="update">
        Last Update: {{ lastTimestamp }}
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
#container {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
}

#controls {
  margin-bottom: 10px;
}

#chart {
  height: 100%;
}

.chart-select {
  padding: 8px 12px;
  border: 2px solid #086494;
  border-radius: 5px;
  background-color: white;
  color: #086494;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s;
  outline: none;
  min-width: 120px;

  &:hover {
    border-color: #064d6a;
    background-color: #f8f9fa;
  }

  &:focus {
    border-color: #043a52;
    box-shadow: 0 0 0 2px rgba(8, 100, 148, 0.2);
  }
}

.bottom-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 5px;
  gap: 10px;
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
  margin-left: auto;
}
</style>
