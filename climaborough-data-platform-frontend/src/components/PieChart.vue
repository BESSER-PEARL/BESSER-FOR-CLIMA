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

// Available colors for random assignment
const availableColors = ['#B1E3FF', '#A1E3CB', '#95A4FC', '#A8C5DA', '#69696A'];

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
  
  // If all colors are used, still return the hash-based color for consistency
  if (attempts >= availableColors.length) {
    selectedColor = availableColors[colorIndex];
  }
  
  return selectedColor;
};

const refTitle = ref(props.title)

function getLatestKpiValues(items) {
  const latestValues = {};
  items.forEach(item => {
    // Use the latest KPI value for each category/standing
    latestValues[item.currentStanding] = item.kpiValue;
  });
  return latestValues;
}

const items = ref([])
const values = ref([])
const stands = ref([])
const mapping = ref({})
const series = ref([])
const labels = ref([])

const formatDate = (dateString) => {
  const date = new Date(dateString);
  const day = String(date.getDate()).padStart(2, '0');
  const month = String(date.getMonth() + 1).padStart(2, '0'); // getMonth() is zero-based
  const year = date.getFullYear();
  return `${day}/${month}/${year}`;
};
const lastTimestamp = ref("No updates available");

async function getItems() {
  try {
    const response = await fetch('http://localhost:8000/' + props.city.toLowerCase() + '/kpi/?id=' + props.tableId)
    const data = await response.json();
    console.log(data);

    data.forEach(item => {
      items.value.push(item);
      stands.value.push(item.currentStanding);
      lastTimestamp.value = formatDate(item.timestamp);
    });
    
    items.value = data
    mapping.value = getLatestKpiValues(data);    // Clear existing arrays
    labels.value = [];
    series.value = [];
    const colors = [];
    const usedColors = new Set(); // Track used colors

    for (const [key, value] of Object.entries(mapping.value)) {
      labels.value.push(key);
      series.value.push(value);
      
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
    }
    
    // Update chart options with consistent colors
    chartOptions.value = {
      ...chartOptions.value,
      colors: colors,
      labels: labels.value
    };
    
    console.log(series.value)
    console.log(labels.value)

  } catch (error) {
    window.alert(error)
  }
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

const alert = ref(false)
const toggleAlert = () => {
  alert.value = !alert.value
}
</script>

<template>
  <div id="container">
    <div id="chart">
      <VueApexCharts type="pie" height="100%" :options="chartOptions" :series="series"></VueApexCharts>
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
  height: 90%;
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