<script setup>
import { ref, computed, watch, onMounted } from "vue";
import apiService from '@/services/apiService';
import KPIInfoDialog from './KPIInfoDialog.vue';
import { Icon } from '@iconify/vue';

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
  },
  preferredChartType: {
    type: String,
    default: 'line',
    validator: (value) => ['line', 'bar', 'area'].includes(value)
  }
})

const emit = defineEmits(['update:preferredChartType']);

// Consistent color mapping for categories (same as BarChart and PieChart)
const categoryColorMap = {
  'Low': '#B1E3FF',      // Light Blue
  'Medium': '#A1E3CB',   // Light Green
  'High': '#95A4FC',     // Light Purple
  'Good': '#95A4FC',     // Light Purple
  'Fair': '#A1E3CB',     // Light Green
  'Poor': '#B1E3FF',     // Light Blue
  'Excellent': '#A8C5DA', // Light Blue-Gray
  'Bad': '#69696A'       // Gray
};

// Available colors for random assignment - expanded palette with consistent light/pastel style
const availableColors = [
  '#B1E3FF', // Light Blue
  '#A1E3CB', // Light Green  
  '#95A4FC', // Light Purple
  '#A8C5DA', // Light Blue-Gray
  '#69696A', // Gray
  '#FFB1C1', // Light Pink
  '#B1FFB1', // Light Mint Green
  '#FFE4B1', // Light Peach
  '#E1B1FF', // Light Lavender
  '#B1FFFF', // Light Cyan
  '#FFB1E1', // Light Rose
  '#C1FFB1', // Light Lime
  '#B1E1FF', // Light Sky Blue
  '#FFE1B1', // Light Apricot
  '#D1B1FF', // Light Violet
  '#B1FFC1', // Light Seafoam
  '#FFD1B1', // Light Coral
  '#C1B1FF', // Light Periwinkle
  '#B1FFD1', // Light Mint
  '#FFC1B1'  // Light Salmon
];

// Function to get consistent color based on label name (same as PieChart and BarChart)
const getConsistentColorForLabel = (labelName, usedColors) => {
  // Create a simple hash from the label name
  let hash = 0;
  for (let i = 0; i < labelName.length; i++) {
    const char = labelName.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash; // Convert to 32-bit integer
  }
  
  // Get a consistent index based on the hash
  const colorIndex = Math.abs(hash) % availableColors.length;
  let selectedColor = availableColors[colorIndex];
  
  // If the color is already used, try the next available colors
  let attempts = 0;
  while (usedColors.has(selectedColor) && attempts < availableColors.length) {
    const nextIndex = (colorIndex + attempts + 1) % availableColors.length;
    selectedColor = availableColors[nextIndex];
    attempts++;
  }
  
  // If all available colors are used, generate a unique color in the same light/pastel style
  if (attempts >= availableColors.length) {
    // Generate a unique color based on the number of used colors
    const usedCount = usedColors.size;
    const hue = (usedCount * 137.508) % 360; // Golden angle approximation for good distribution
    selectedColor = `hsl(${hue}, 45%, 85%)`; // Lower saturation and higher lightness for pastel effect
  }
  
  return selectedColor;
};

const chartType = ref(props.preferredChartType); // Reactive chart type

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
  // Calculate yaxis max based on data and thresholds
  let yMax = undefined; // Let ApexCharts auto-scale by default
  let yMin = 0; // Start from 0 by default
  
  // If we have threshold, ensure the y-axis includes it with some padding
  if (effectiveMaxThreshold.value !== null && effectiveMaxThreshold.value !== 'N/A') {
    const maxThresholdNum = parseFloat(effectiveMaxThreshold.value);
    if (!isNaN(maxThresholdNum)) {
      // Add 10% padding above the threshold
      yMax = maxThresholdNum * 1.1;
    }
  }
  
  const options = {
    chart: {
      type: chartType.value,
      zoom: {
        enabled: true
      },
      stacked: supportsStacking.value,
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
      title: { text: props.ytitle },
      min: yMin,
      max: yMax,
      labels: {
        formatter: function(value) {
          if (value === null || value === undefined) return '';
          
          // Format numbers to avoid long decimals
          if (Math.abs(value) < 0.01 && value !== 0) {
            // For very small numbers, use scientific notation or more decimals
            return value.toExponential(2);
          } else if (Math.abs(value) >= 1000) {
            // For large numbers, add commas
            return value.toLocaleString('en-US', { maximumFractionDigits: 2 });
          } else {
            // For normal numbers, limit to 2 decimal places
            return parseFloat(value.toFixed(2));
          }
        }
      }
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
    },
    annotations: {
      yaxis: []
    }
  };

  // Add threshold lines as annotations (only for non-stacked charts)
  if (hasThresholds.value && !supportsStacking.value) {
    if (effectiveMaxThreshold.value !== null && effectiveMaxThreshold.value !== 'N/A') {
      const maxVal = parseFloat(effectiveMaxThreshold.value);
      if (!isNaN(maxVal)) {
        options.annotations.yaxis.push({
          y: maxVal,
          borderColor: '#FF6B6B',
          strokeDashArray: 5,
          label: {
            borderColor: '#FF6B6B',
            style: {
              color: '#fff',
              background: '#FF6B6B',
            },
            text: `Max: ${maxVal}`
          }
        });
      }
    }
    
    if (effectiveMinThreshold.value !== null && effectiveMinThreshold.value !== 'N/A') {
      const minVal = parseFloat(effectiveMinThreshold.value);
      if (!isNaN(minVal)) {
        options.annotations.yaxis.push({
          y: minVal,
          borderColor: '#4ECDC4',
          strokeDashArray: 5,
          label: {
            borderColor: '#4ECDC4',
            style: {
              color: '#fff',
              background: '#4ECDC4',
            },
            text: `Min: ${minVal}`
          }
        });
      }
    }
  }

  return options;
});

const values = ref([]);
const valuemappedtotime = ref([]);
const timestamps = ref([]);
const rawData = ref([]);
const localMonthFilter = ref(props.monthFilter || "");

// KPI Info Dialog
const showKPIInfo = ref(false);

// Initialize series ref BEFORE processFilteredData uses it
const series = ref([
  {
    name: "KPI Values",
    data: [],
    color: props.color,
  }
]);

// Computed property - simplified since filtering is now done server-side
const filteredData = computed(() => {
  return rawData.value;
});

const formatDate = (dateString) => {
  const date = new Date(dateString);
  const day = String(date.getDate()).padStart(2, '0');
  const month = String(date.getMonth() + 1).padStart(2, '0');
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
      console.warn('TimeChart: No tableId (kpi_id) provided');
      rawData.value = [];
      processFilteredData();
      return;
    }
    
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
    
    console.log('TimeChart fetched data count:', data.length);
    rawData.value = data;
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
    processStackedData();
  } else if (hasCategories.value && chartType.value === 'line') {
    processMultiLineData();
  } else {
    processSingleSeriesData();
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
  const usedColors = new Set();
  
  filteredData.value.forEach(item => {
    const val = item.value ?? item.kpiValue ?? 0;
    const category = item.category_label || 'Uncategorized';
    
    if (!categoryData[category]) {
      categoryData[category] = [];
    }
    
    categoryData[category].push({ x: item.timestamp, y: val });
    timestamps.value.push(item.timestamp);
  });
  
  // Create series for each category with consistent colors
  series.value = Object.keys(categoryData).map((category) => {
    let color;
    if (categoryColorMap[category]) {
      color = categoryColorMap[category];
    } else {
      color = getConsistentColorForLabel(category, usedColors);
    }
    usedColors.add(color);
    
    return {
      name: category,
      data: categoryData[category],
      color: color
    };
  });
}

function processStackedData() {
  // Group data by timestamp and category for stacking
  const timeSeriesMap = {};
  const categories = new Set();
  const usedColors = new Set();
  
  filteredData.value.forEach(item => {
    const val = item.value ?? item.kpiValue ?? 0;
    const timestamp = item.timestamp;
    const category = item.category_label || 'Uncategorized';
    
    categories.add(category);
    
    if (!timeSeriesMap[timestamp]) {
      timeSeriesMap[timestamp] = {};
    }
    
    if (!timeSeriesMap[timestamp][category]) {
      timeSeriesMap[timestamp][category] = 0;
    }
    timeSeriesMap[timestamp][category] += val;
  });
  
  // Convert to series format with consistent colors
  const categoriesArray = Array.from(categories);
  series.value = categoriesArray.map((category) => {
    const data = Object.keys(timeSeriesMap).map(timestamp => ({
      x: timestamp,
      y: timeSeriesMap[timestamp][category] || 0
    }));
    
    let color;
    if (categoryColorMap[category]) {
      color = categoryColorMap[category];
    } else {
      color = getConsistentColorForLabel(category, usedColors);
    }
    usedColors.add(color);
    
    return {
      name: category,
      data: data,
      color: color
    };
  });
  
  timestamps.value = Object.keys(timeSeriesMap);
}

getItems();

watch(() => [props.title, props.xtitle, props.ytitle, props.color], () => {
  processFilteredData();
});

// Watch for chartType changes and emit to parent
watch(chartType, (newType) => {
  processFilteredData();
  emit('update:preferredChartType', newType);
});

// Watch for monthFilter changes and re-fetch data with server-side filtering
watch(() => props.monthFilter, (newFilter) => {
  console.log('TimeChart watch triggered - monthFilter changed to:', newFilter);
  localMonthFilter.value = newFilter;
  getItems();
});

// Watch for preferred chart type changes from parent
watch(() => props.preferredChartType, (newType) => {
  if (newType && newType !== chartType.value) {
    chartType.value = newType;
  }
});
</script>

<template>
  <div id="container">
    <div id="chart">
      <VueApexCharts type="line" height="100%" :options="chartOptions" :series="series"></VueApexCharts>
    </div>
    <div class="bottom-controls">
      <div class="left-spacer"></div>
      <div class="update">
        <select v-model="chartType" class="chart-type-selector" @mousedown.stop @click.stop>
          <option value="line">📈 Line</option>
          <option value="bar">📊 Bar</option>
          <option value="area">📉 Area</option>
        </select>
        <span class="separator">|</span>
        <span class="last-update">Last Update: {{ lastTimestamp }}</span>
        <Icon icon="mdi:information" width="20" height="20" @click="showKPIInfo = true"
          style="margin-left: 8px; color: #086494; cursor: pointer;" title="View KPI Information" />
      </div>
    </div>

    <!-- KPI Info Dialog -->
    <KPIInfoDialog v-model="showKPIInfo" :kpi-id="tableId" />
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

.chart-type-selector {
  padding: 4px 8px;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  background-color: #f8f9fa;
  color: #333;
  font-size: 11px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  outline: none;

  &:hover {
    background-color: #e9ecef;
    border-color: #086494;
  }

  &:focus {
    border-color: #086494;
    background-color: white;
    box-shadow: 0 0 0 2px rgba(8, 100, 148, 0.1);
  }

  option {
    padding: 4px;
  }
}

.bottom-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  border-top: 1px solid rgba(0, 0, 0, 0.06);
  background: transparent;
}

.left-spacer {
  flex: 1;
}

.update {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 8px;
  font-size: 11px;
  color: #666;
  font-weight: 500;
}

.separator {
  color: #ddd;
  margin: 0 4px;
}

.last-update {
  color: #666;
}
</style>
