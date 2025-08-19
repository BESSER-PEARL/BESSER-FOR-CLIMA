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

// Function to get unique random color from remaining colors
const getUniqueRandomColor = (usedColors) => {
  const remainingColors = availableColors.filter(color => !usedColors.has(color));
  if (remainingColors.length === 0) {
    // If all colors are used, start cycling through them again
    return availableColors[Math.floor(Math.random() * availableColors.length)];
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
      stands.value.push(item.categoryLabel);
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
        // Get unique random color for unknown categories
        color = getUniqueRandomColor(usedColors);
      }
      
      colors.push(color);
      usedColors.add(color);
    }

    // Update chart options with consistent colors
    chartOptions.value = {
      ...chartOptions.value,
      colors: colors,
      xaxis: {
        categories: labels.value,
        title: {
          text: "Categories",
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
  xaxis: {
    categories: labels.value,
    title: {
      text: "Categories",
    }
  },
  dataLabels: {
    enabled: true,
    style: {
      fontSize: "16px",
      fontWeight: "bold",
    },
  },
  plotOptions: {
    bar: {
      horizontal: false,
      columnWidth: '50%',
    }
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
      categories: labels.value
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
  height: 90%;
}

.update {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  flex-shrink: 0;
  padding: 5px;
}
</style>
