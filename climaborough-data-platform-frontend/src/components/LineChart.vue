<script setup>
import { ref, computed, watch } from "vue";
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
})

const chartType = ref('line'); // Reactive chart type

const chartOptions = computed(() => ({
  chart: {
    type: chartType.value, // Use the reactive chartType
    zoom: {
      enabled: true
    }
  },
  dataLabels: {
    enabled: false
  },
  stroke: {
    curve: chartType.value === 'area' ? 'smooth' : 'straight',
    width: 2.2
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
  }
}));

const values = ref([]);
const baseline = ref([]);
const valuemappedtotime = ref([]);
const timestamps = ref([]);

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
    const response = await fetch('http://localhost:8000/' + props.city.toLowerCase() + '/kpi/?id=' + props.tableId);
    const data = await response.json();
    data.forEach(item => {
      values.value.push(item.kpiValue);
      timestamps.value.push(item.timestamp);
      valuemappedtotime.value.push({ x: item.timestamp, y: item.kpiValue });
      baseline.value.push({ x: item.timestamp, y: Math.max(0, item.kpiValue - 10) }); // Example baseline
    });
  } catch (error) {
    window.alert(error);
  }
}

getItems();

const series = ref([
  {
    name: "KPI Values",
    data: valuemappedtotime.value,
    color: props.color,
  },
  {
    name: "Baseline",
    data: baseline.value,
    color: "#FFB800",
  }
]);

watch(() => [props.title, props.xtitle, props.ytitle, props.color], () => {
  series.value = [
    {
      name: "KPI Values",
      data: valuemappedtotime.value,
      color: props.color
    }
  ];
});
</script>

<template>
  <div id="container">
    <div id="controls">
      <button @click="chartType = 'line'">Line Chart</button>
      <button @click="chartType = 'bar'">Bar Chart</button>
      <button @click="chartType = 'area'">Area Chart</button>
    </div>
    <div id="chart">
      <VueApexCharts type="line" height="100%" :options="chartOptions" :series="series"></VueApexCharts>
    </div>
    <div class="update">
      Last Update: {{ lastTimestamp }}
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

.update {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  flex-shrink: 0;
  padding: 5px;
}
</style>
