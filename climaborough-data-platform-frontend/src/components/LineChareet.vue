<script setup>
import { ref, reactive, watch, computed } from "vue";
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
const chartOptions = ref({
  chart: {
    type: 'line',
    zoom: {
      enabled: true
    }
  },
  dataLabels: {
    enabled: false
  },
  stroke: {
    curve: 'straight'
  },
  title: {
    text: props.title,
  },
  grid: {
    row: {
      colors: ['#f3f3f3', 'transparent'], // takes an array which will be repeated on columns
      opacity: 0.5
    },
    column: {
      colors: undefined,
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
})
const baseline = ref([])
const values = ref([])
const valuemappedtotime = ref([])
const timestamps = ref([])
const formatDate = (dateString) => {
  const date = new Date(dateString);
  const day = String(date.getDate()).padStart(2, '0');
  const month = String(date.getMonth() + 1).padStart(2, '0'); // getMonth() is zero-based
  const year = date.getFullYear();
  return `${day}/${month}/${year}`;
};

function getRandomInt(min, max) {
    min = Math.ceil(min + max/8);
    max = Math.floor(max-max/8);
    return Math.floor(Math.random() * (max - min + 1)) + min;
}

const lastTimestamp = computed(() => {
  if (timestamps.value.length > 0) {
    const lastTimestamp = timestamps.value[timestamps.value.length - 1];
    return formatDate(lastTimestamp);
  }
  return 'No updates available';
});
async function getItems() {
  try {
    const response = await fetch('http://localhost:8000/' + props.city.toLowerCase() + '/kpi/?id=' + props.tableId)
    const data = await response.json();
    // Iterate over the list of strings and log each string
    data.forEach(item => {
      values.value.push(item.kpiValue)
      timestamps.value.push(item.timestamp)
      valuemappedtotime.value.push({ x: item.timestamp, y: item.kpiValue })
      let baseY = getRandomInt(0,item.kpiValue)
      baseline.value.push({ x: item.timestamp, y: baseY })
    });
    if (valuemappedtotime.value.length == 1) {
      valuemappedtotime.value.push(valuemappedtotime.value[0])
    }

    chartOptions.value = chartOptions.value = {

      chart: {
        type: 'line',
        zoom: {
          enabled: true
        },
        toolbar: {
          offsetY: 20
        }
      },
      dataLabels: {
        enabled: false,
      },
      stroke: {
        curve: 'straight',
        width: 2.2
      },
      markers: {
        size: 3,
        colors: undefined,
        strokeColors: '#fff',
        strokeWidth: 1,
        strokeOpacity: 0.9,
        strokeDashArray: 0,
        fillOpacity: 1,
        discrete: [],
        shape: "circle",
        radius: 2,
        offsetX: 0,
        offsetY: 0,
        onClick: undefined,
        onDblClick: undefined,
        showNullDataPoints: true,
        hover: {
          size: undefined,
          sizeOffset: 3
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
      grid: {
        row: {
          colors: ['#f3f3f3', 'transparent'], // takes an array which will be repeated on columns
          opacity: 0.5
        },
        xaxis: {
          lines: {
            show: true
          }
        },
      },
      xaxis: {
        type: 'datetime',
        title: { text: props.xtitle }
      },
      yaxis: {
        title: { text: props.ytitle }
      }
    }

  } catch (error) {
    window.alert(error)
  }
}

getItems()
console.log(valuemappedtotime.value)

const series = ref([{
  name: "Current Value", data: valuemappedtotime.value, color: props.color,
}, {
  name: "Baseline", data: baseline.value, color: "#FFB800",
}])


watch(() => [props.title, props.xtitle, props.ytitle, props.color], () => {
  series.value = [{
    name: "Current Value", namedata: valuemappedtotime.value, color: props.color
  }]
  chartOptions.value = {
    chart: {
      type: 'line',
      zoom: {
        enabled: true
      }
    },
    dataLabels: {
      enabled: false
    },
    stroke: {
      curve: 'straight',
      width: 2.2
    },
    markers: {
      size: 3,
      colors: undefined,
      strokeColors: '#fff',
      strokeWidth: 1,
      strokeOpacity: 0.9,
      strokeDashArray: 0,
      fillOpacity: 1,
      discrete: [],
      shape: "circle",
      radius: 2,
      offsetX: 0,
      offsetY: 0,
      onClick: undefined,
      onDblClick: undefined,
      showNullDataPoints: true,
      hover: {
        size: undefined,
        sizeOffset: 3
      }
    },
    title: {
      text: props.title
    },
    grid: {
      row: {
        colors: ['#f3f3f3', 'transparent'], // takes an array which will be repeated on columns
        opacity: 0.5
      },
      xaxis: {
        lines: {
          show: true
        }
      },
    },
    xaxis: {
      xaxis: 'datetime',
      title: { text: props.xtitle }
    },
    yaxis: {
      title: { text: props.ytitle }
    }
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
      <VueApexCharts type="line" height="100%" :options="chartOptions" :series="series"></VueApexCharts>
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
  height: 100%;
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