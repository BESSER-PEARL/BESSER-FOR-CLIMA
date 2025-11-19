<script setup>
import { ref, watch, computed } from "vue";
import apiService from '@/services/apiService';
import KPIInfoDialog from './KPIInfoDialog.vue';
import { Icon } from '@iconify/vue';

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
  monthFilter: {
    type: String,
    default: ""
  }
})

// Consistent color mapping for categories
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

// Function to get consistent color based on label name
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

const refTitle = ref(props.title)

// Function to transform snake_case labels to Title Case
const formatLabelName = (labelName) => {
  if (typeof labelName !== 'string') return labelName;
  
  // Check if the label contains underscores (snake_case)
  if (labelName.includes('_')) {
    return labelName
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
      .join(' ');
  }
  
  // If no underscores, just capitalize first letter
  return labelName.charAt(0).toUpperCase() + labelName.slice(1).toLowerCase();
}

// Function to sort labels consistently across charts
const getSortedEntries = (mapping) => {
  return Object.entries(mapping).sort(([keyA], [keyB]) => {
    // Sort alphabetically by label name for consistent ordering
    return keyA.toLowerCase().localeCompare(keyB.toLowerCase());
  });
}

function getLatestKpiValues(items) {
  const latestValues = {};
  items.forEach(item => {
    // Backend returns: value (not kpiValue) and category_label (not categoryLabel)
    const categoryLabel = item.category_label || item.categoryLabel; // Support both
    const kpiValue = item.value !== undefined ? item.value : item.kpiValue; // Support both
    
    if (categoryLabel !== undefined && categoryLabel !== null) {
      latestValues[categoryLabel] = kpiValue;
    }
  });
  console.log('PieChart - Latest KPI values mapping:', latestValues);
  return latestValues;
}

const items = ref([])
const values = ref([])
const stands = ref([])
const mapping = ref({})
const series = ref([])
const labels = ref([])
const kpiMetadata = ref(null)
const rawData = ref([])
const localMonthFilter = ref(props.monthFilter || "")

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
const lastTimestamp = ref("No updates available");

async function fetchKpiMetadata() {
  if (!props.tableId) return;
  
  try {
    // Use new API endpoint to get KPI metadata
    const kpiMeta = await apiService.getKPIById(props.tableId);
    kpiMetadata.value = kpiMeta;
    //console.log('KPI Metadata:', kpiMeta);
  } catch (error) {
    console.warn('Could not fetch KPI metadata:', error);
    kpiMetadata.value = null;
  }
}

async function getItems() {
  try {
    // First fetch KPI metadata
    await fetchKpiMetadata();
    
    // Use server-side filtering if month filter is active
    const data = localMonthFilter.value
      ? await apiService.getKPIValuesByMonth(props.tableId, localMonthFilter.value)
      : await apiService.getKPIValues(props.tableId);
    
    console.log('PieChart - Raw data from API:', data.slice(0, 3)); // Log first 3 items
    rawData.value = data; // Store raw data
    updateChart(); // Process filtered data
  } catch (error) {
    console.error('Error fetching KPI data:', error);
    window.alert(error);
  }
}

function updateChart() {
  const data = filteredData.value;
  
  // Clear existing data
  items.value = [];
  stands.value = [];
  labels.value = [];
  series.value = [];
  
  if (data.length === 0) {
    return; // No data to process
  }

  data.forEach(item => {
    items.value.push(item);
    const categoryLabel = item.category_label || item.categoryLabel; // Support both naming conventions
    if (categoryLabel) {
      stands.value.push(categoryLabel);
    }
    lastTimestamp.value = formatDate(item.timestamp);
  });
  
  items.value = data
  mapping.value = getLatestKpiValues(data);    // Clear existing arrays
    labels.value = [];
    series.value = [];
    const colors = [];
    const usedColors = new Set(); // Track used colors

    // Check if we have category_label_dictionary for ordered display
    if (kpiMetadata.value?.category_label_dictionary) {
      //console.log('Using category_label_dictionary for ordering:', kpiMetadata.value.category_label_dictionary);
      
      // Process in the order defined by category_label_dictionary
      Object.entries(kpiMetadata.value.category_label_dictionary).forEach(([key, labelName]) => {
        if (mapping.value.hasOwnProperty(labelName)) {
          const value = mapping.value[labelName];
          const formattedLabel = formatLabelName(labelName);
          labels.value.push(formattedLabel);
          series.value.push(value);
          
          let color;
          if (categoryColorMap[labelName]) {
            // Use predefined color for known categories
            color = categoryColorMap[labelName];
          } else {
            // Get consistent color based on label name for unknown categories
            color = getConsistentColorForLabel(labelName, usedColors);
          }
          
          colors.push(color);
          usedColors.add(color);
        }
      });
      
      // Add any remaining categories that aren't in the dictionary (sorted)
      const sortedRemainingEntries = getSortedEntries(mapping.value).filter(([labelName]) => {
        const formattedLabel = formatLabelName(labelName);
        return !labels.value.includes(formattedLabel);
      });
      
      sortedRemainingEntries.forEach(([labelName, value]) => {
        const formattedLabel = formatLabelName(labelName);
        labels.value.push(formattedLabel);
        series.value.push(value);
        
        let color;
        if (categoryColorMap[labelName]) {
          color = categoryColorMap[labelName];
        } else {
          color = getConsistentColorForLabel(labelName, usedColors);
        }
        
        // Ensure color is unique
        while (usedColors.has(color)) {
          const usedCount = usedColors.size;
          const hue = (usedCount * 137.508) % 360;
          color = `hsl(${hue}, 45%, 85%)`; // Light pastel style
        }
        
        colors.push(color);
        usedColors.add(color);
      });
    } else {
      // Fallback to original behavior when no category_label_dictionary (sorted alphabetically)
      //console.log('No category_label_dictionary found, using alphabetical ordering');
      
      const sortedEntries = getSortedEntries(mapping.value);
      sortedEntries.forEach(([key, value]) => {
        const formattedLabel = formatLabelName(key);
        labels.value.push(formattedLabel);
        series.value.push(value);
        
        let color;
        if (categoryColorMap[key]) {
          // Use predefined color for known categories
          color = categoryColorMap[key];
        } else {
          // Get consistent color based on label name for unknown categories
          color = getConsistentColorForLabel(key, usedColors);
        }
        
        // Ensure color is unique
        while (usedColors.has(color)) {
          const usedCount = usedColors.size;
          const hue = (usedCount * 137.508) % 360;
          color = `hsl(${hue}, 45%, 85%)`; // Light pastel style
        }
        
        colors.push(color);
        usedColors.add(color);
      });
    }
    
    // Update chart options with consistent colors
    chartOptions.value = {
      ...chartOptions.value,
      colors: colors,
      labels: labels.value
    };
    
    //console.log(series.value)
    //console.log(labels.value)
}

getItems()

const chartOptions = ref({
  chart: {
    type: 'pie',
    toolbar: {
      offsetY: 20
    }
  },
  title: {
    text: props.title,
    style: {
      fontSize: '20px',
      fontWeight: 'bold'
    },
    offsetY: -8,
  },
  labels: labels.value,
  dataLabels: {
    enabled: true,
    style: {
      fontSize: "16px",
      fontWeight: "bold",
    },

  },

  plotOptions: {
    pie: {
      dataLabels: {
        offset: -15
      },
    },

  },
  responsive: [
    {
      breakpoint: 1600,
      options: {
        dataLabels: {
          enabled: true,
          style: {
            fontSize: "10px",
            fontWeight: "bold",
          },

        }, plotOptions: {
          pie: {
            dataLabels: {
              offset: -10
            },
          },
        }
      }
    }
  ]


})


watch(() => [props.title], () => {
  chartOptions.value = {
    ...chartOptions.value,
    title: {
      text: props.title
    },
    labels: labels.value
  }
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

const alert = ref(false)
const showKPIInfo = ref(false);

const toggleAlert = () => {
  alert.value = !alert.value
}
</script>

<template>
  <div id="container">
    <div id="chart">
      <div v-if="filteredData.length === 0" class="no-data-message">
        No data
      </div>
      <VueApexCharts v-else type="pie" height="100%" :options="chartOptions" :series="series"></VueApexCharts>
    </div>
    <div class="update">
      Last Update: {{ lastTimestamp }}
      <Icon icon="mdi:information" width="20" height="20" @click="showKPIInfo = true"
        style="margin-left: 5px; color: #086494; cursor: pointer;" title="View KPI Information" />
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
  gap: 8px;
}

.update-text {
  margin-right: auto;
}

.info-button {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border: 1.5px solid #086494;
  border-radius: 4px;
  background-color: white;
  color: #086494;
  cursor: pointer;
  transition: all 0.3s;
  outline: none;
  padding: 0;

  &:hover {
    border-color: #064d6a;
    background-color: #f8f9fa;
    transform: scale(1.05);
  }

  &:active {
    transform: scale(0.95);
  }

  svg {
    font-size: 16px;
  }
}

.no-data-message {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  color: #666;
  font-size: 16px;
  font-weight: 500;
}
</style>