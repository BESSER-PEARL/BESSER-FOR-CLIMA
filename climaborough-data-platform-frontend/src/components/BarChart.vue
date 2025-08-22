<script setup>
import { ref, watch } from "vue";
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

// Function to get consistent color based on label name (same as PieChart)
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

// Function to get unique color from remaining colors (kept for backwards compatibility)
const getUniqueRandomColor = (usedColors) => {
  const remainingColors = availableColors.filter(color => !usedColors.has(color));
  if (remainingColors.length === 0) {
    // If all predefined colors are used, generate a unique pastel color
    const usedCount = usedColors.size;
    const hue = (usedCount * 137.508) % 360; // Golden angle approximation for good distribution
    return `hsl(${hue}, 45%, 85%)`; // Light pastel style
  }
  return remainingColors[Math.floor(Math.random() * remainingColors.length)];
};

const refTitle = ref(props.title);

function getLatestKpiValues(items) {
  const latestValues = {};
  items.forEach(item => {
    // Use the latest KPI value for each category/standing
    latestValues[item.categoryLabel] = item.kpiValue;
  });
  return latestValues;
}

const items = ref([]);
const values = ref([]);
const stands = ref([]);
const mapping = ref({});
const series = ref([]);
const labels = ref([]);
const kpiMetadata = ref(null);

const formatDate = (dateString) => {
  const date = new Date(dateString);
  const day = String(date.getDate()).padStart(2, '0');
  const month = String(date.getMonth() + 1).padStart(2, '0'); // getMonth() is zero-based
  const year = date.getFullYear();
  return `${day}/${month}/${year}`;
};
const lastTimestamp = ref("No updates available");

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

async function fetchKpiMetadata() {
  try {
    const response = await fetch('http://localhost:8000/' + props.city.toLowerCase() + '/kpis');
    const kpisData = await response.json();
    
    // Find the KPI metadata for our tableId
    const kpiMeta = kpisData.find(kpi => kpi.id === props.tableId);
    kpiMetadata.value = kpiMeta;
    console.log('KPI Metadata:', kpiMeta);
  } catch (error) {
    console.warn('Could not fetch KPI metadata:', error);
    kpiMetadata.value = null;
  }
}

async function getItems() {
  try {
    // First fetch KPI metadata
    await fetchKpiMetadata();
    
    const response = await fetch('http://localhost:8000/' + props.city.toLowerCase() + '/kpi/?id=' + props.tableId)
    const data = await response.json();
    console.log(data);

    data.forEach(item => {
      items.value.push(item);
      stands.value.push(item.categoryLabel);
      lastTimestamp.value = formatDate(item.timestamp);
    });
    
    items.value = data
    mapping.value = getLatestKpiValues(data);    
    
    // Calculate total for percentage conversion
    const totalValue = Object.values(mapping.value).reduce((sum, value) => sum + value, 0);
    
    // Clear existing arrays
    labels.value = [];
    series.value = [];
    const colors = [];
    const usedColors = new Set(); // Track used colors

    // Check if we have categoryLabelDictionary for ordered display
    if (kpiMetadata.value?.categoryLabelDictionary) {
      
      // Process in the order defined by categoryLabelDictionary
      Object.entries(kpiMetadata.value.categoryLabelDictionary).forEach(([key, labelName]) => {
        if (mapping.value.hasOwnProperty(labelName)) {
          const value = mapping.value[labelName];
          const formattedLabel = formatLabelName(labelName);
          labels.value.push(formattedLabel);
          
          // Convert to percentage
          const percentage = totalValue > 0 ? (value / totalValue) * 100 : 0;
          series.value.push(Math.round(percentage * 100) / 100); // Round to 2 decimal places
          
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
        
        // Convert to percentage
        const percentage = totalValue > 0 ? (value / totalValue) * 100 : 0;
        series.value.push(Math.round(percentage * 100) / 100);
        
        let color;
        if (categoryColorMap[labelName]) {
          color = categoryColorMap[labelName];
        } else {
          color = getConsistentColorForLabel(labelName, usedColors);
        }
        
        colors.push(color);
        usedColors.add(color);
      });
    } else {
      // Fallback to original behavior when no categoryLabelDictionary (sorted alphabetically)
      console.log('No categoryLabelDictionary found, using alphabetical ordering');
      
      const sortedEntries = getSortedEntries(mapping.value);
      sortedEntries.forEach(([key, value]) => {
        const formattedLabel = formatLabelName(key);
        labels.value.push(formattedLabel);
        // Convert to percentage
        const percentage = totalValue > 0 ? (value / totalValue) * 100 : 0;
        series.value.push(Math.round(percentage * 100) / 100); // Round to 2 decimal places
        
        let color;
        if (categoryColorMap[key]) {
          // Use predefined color for known categories
          color = categoryColorMap[key];
        } else {
          // Get consistent color based on label name for unknown categories
          color = getConsistentColorForLabel(key, usedColors);
        }
        
        colors.push(color);
        usedColors.add(color);
      });
    }

    // Update chart options with consistent colors
    chartOptions.value = {
      ...chartOptions.value,
      colors: colors,
      fill: {
        colors: colors
      },
      xaxis: {
        categories: labels.value,
        title: {
          text: "Categories",
        },
        labels: {
          rotate: -30,
          style: {
            fontSize: '12px'
          },
          maxHeight: 80
        }
      }
    };

    console.log(series.value);
    console.log(labels.value);
  } catch (error) {
    window.alert(error);
  }
}

getItems();

const chartOptions = ref({
  chart: {
    type: 'bar',
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
  fill: {
    colors: []
  },
  legend: {
    show: false
  },
  xaxis: {
    categories: labels.value,
    title: {
      text: "Categories",
    },
    labels: {
      rotate: -45,
      style: {
        fontSize: '12px'
      },
      maxHeight: 80
    }
  },
  yaxis: {
    title: {
      text: "Percentage (%)"
    },
    labels: {
      formatter: function (val) {
        return val.toFixed(1) + "%"
      }
    },
    max: 100
  },
  dataLabels: {
    enabled: true,
    style: {
      fontSize: "14px",
      fontWeight: "bold",
      colors: ['#808080']
    },
    formatter: function (val) {
      return val.toFixed(1) + "%"
    }
  },
  plotOptions: {
    bar: {
      horizontal: false,
      columnWidth: '50%',
      distributed: true
    }
  },
  responsive: [
    {
      breakpoint: 1600,
      options: {
        xaxis: {
          labels: {
            rotate: -45,
            style: {
              fontSize: '10px'
            },
            maxHeight: 60
          }
        },
        dataLabels: {
          enabled: true,
          style: {
            fontSize: "12px",
            fontWeight: "bold",
            colors: ['#000000']
          },
          formatter: function (val) {
            return val.toFixed(1) + "%"
          }
        }
      }
    }
  ]
});

watch(() => [props.title], () => {
  chartOptions.value = {
    ...chartOptions.value,
    title: {
      text: props.title
    },
    xaxis: {
      categories: labels.value,
      title: {
        text: "Categories",
      },
      labels: {
        rotate: -45,
        style: {
          fontSize: '12px'
        },
        maxHeight: 80
      }
    }
  }
});

const alert = ref(false);
const toggleAlert = () => {
  alert.value = !alert.value;
};
</script>

<template>
  <div id="container">
    <div id="chart">
      <VueApexCharts type="bar" height="100%" :options="chartOptions" :series="[ { data: series } ]"></VueApexCharts>
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
