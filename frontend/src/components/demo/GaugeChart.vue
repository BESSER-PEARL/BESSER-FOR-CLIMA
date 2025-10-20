<template>
  <div id="container">
    <div id="chart">
      <VueApexCharts type="radialBar" height="100%" :options="chartOptions" :series="[value]"></VueApexCharts>
    </div>
    <div class="target">
      Target: {{ targetValue }}
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

<script setup>
import { ref, onMounted } from 'vue';
import VueApexCharts from 'vue3-apexcharts';

const props = defineProps({
  title: {
    type: String,
    default: "Gauge Chart"
  },
  target: {
    type: Number,
    default: 75
  }
});

const alert = ref(false);
const toggleAlert = () => {
  alert.value = !alert.value;
};

const lastTimestamp = ref("No updates available");

const value = ref(Math.floor(Math.random() * 101)); // Random value between 0 and 100
const targetValue = ref(props.target); // Store target value

const chartOptions = ref({
  chart: {
    type: 'radialBar',
  },
  plotOptions: {
    radialBar: {
      dataLabels: {
        name: {
          fontSize: '22px',
        },
        value: {
          fontSize: '16px',
          formatter: function (val) {
            return val + "%"; // Display percentage
          }
        },
        total: {
          show: true,
          label: 'Actual',
          formatter: function () {
            return value.value + "%"; // Display actual value
          }
        }
      }
    }
  },
  labels: [props.title],
  title: {
    text: props.title,
    align: 'left',
    style: {
      fontSize: '20px',
      fontWeight: 'bold',
    },
    offsetX: 10,
    offsetY: 0,
  }
});

onMounted(() => {
  lastTimestamp.value = new Date().toLocaleString();
});
</script>

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

.target {
  text-align: center;
  font-size: 16px;
  margin-top: 10px;
}

.update {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  flex-shrink: 0;
  padding: 5px;
}
</style> 