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

const refTitle = ref(props.title)

function countOccurrences(arr) {
  const occurrences = {};
  arr.forEach(item => {
    if (occurrences[item]) {
      occurrences[item]++;
    } else {
      occurrences[item] = 1;
    }
  });
  return occurrences;
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
    console.log(data)
    // Iterate over the list of strings and log each string
    data.forEach(item => {
      items.value.push(item)
      stands.value.push(item.currentStanding)
      lastTimestamp.value = formatDate(item.timestamp)
      // Do whatever you want with each item here
    });
    items.value = data
    mapping.value = countOccurrences(stands.value)
    console.log(mapping.value)
    for (const [key, value] of Object.entries(mapping.value)) {
      labels.value.push(key)
      series.value.push(value)
    }
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
  colors: ['#B1E3FF', '#A1E3CB', '#A8C5DA', '#69696A', '#95A4FC'],
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
    chart: {
      type: 'pie'
    },
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