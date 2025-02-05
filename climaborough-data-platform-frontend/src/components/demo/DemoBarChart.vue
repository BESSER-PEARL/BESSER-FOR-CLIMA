<script setup>
import { ref, watch } from "vue";

const props = defineProps({
  tableId: {
    type: Number,
    required: true
  },
  title: {
    type: String,
    default: "Title"
  },
  series: {
    type: Array,
    default: () => []
  },
  labels: {
    type: Array,
    default: () => []
  },
  colors: {
    type: Array,
    default: () => ['#B1E3FF', '#A1E3CB', '#A8C5DA', '#69696A', '#95A4FC']
  }
})

const chartSeries = ref(props.series.length ? props.series : [25, 15, 44, 55, 41])
const chartLabels = ref(props.labels.length ? props.labels : ['Category A', 'Category B', 'Category C', 'Category D', 'Category E'])

const lastTimestamp = ref(new Date().toLocaleDateString())

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
    categories: chartLabels.value,
    title: {
      text: "Categories",
    }
  },
  colors: ['B1E3FF', 'A1E3CB', 'A8C5DA', '69696A', '95A4FC'],
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

watch(() => [props.title, props.series, props.labels], () => {
  if (props.series.length) chartSeries.value = props.series;
  if (props.labels.length) chartLabels.value = props.labels;
  
  chartOptions.value = {
    ...chartOptions.value,
    title: {
      text: props.title,
      style: {
        fontSize: '20px',
        fontWeight: 'bold'
      },
      offsetY: -8,
    },
    xaxis: {
      categories: chartLabels.value,
      title: {
        text: "Categories",
      }
    },
    colors: ['B1E3FF', 'A1E3CB', 'A8C5DA', '69696A', '95A4FC']
  }
}, { deep: true });

const alert = ref(false);
const toggleAlert = () => {
  alert.value = !alert.value;
};
</script>

<template>
  <div id="container">
    <div id="chart">
      <VueApexCharts type="bar" height="100%" :options="chartOptions" :series="[{ data: chartSeries }]"></VueApexCharts>
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
