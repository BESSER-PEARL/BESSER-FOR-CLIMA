<script setup>
import { get } from 'plotly.js-dist';
import { ref, defineProps, watch, computed } from 'vue';

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
    columns: {
        type: Array,
        default: []
    }
})



const items = ref([
    // ... more items
])

const timestamps = ref([])

async function getItems() {
    try {

        const response = await fetch('http://localhost:8000/' + props.city.toLowerCase() + '/kpi/?id=' + props.tableId)
        const data = await response.json();
        console.log(data)
        // Iterate over the list of strings and log each string
        if (props.columns.length > 0) {
            console.log("we got some column boys")
            console.log(props.columns)
            items.value = []
            items.value = data.map(obj => {
                const newObj = {}
                Object.keys(obj).forEach(key => {
                    if (props.columns.includes(key)) {
                        newObj[key] = obj[key];
                    }
                });
                timestamps.value.push(newObj["Timestamp"])
                return newObj
            })

            data.forEach(item => {
                items.value.push(item)
                // redundant?
                // Do whatever you want with each item here
            });
        } else {
            items.value = data
            items.value = data.map(obj => {
                const newObj = {}

                
                Object.keys(obj).forEach(key => {
                    if (key.toLowerCase().includes("time")) {
                        timestamps.value.push(obj[key])
                        const date = new Date(obj[key])
                        const year = date.getFullYear();
                        const month = String(date.getMonth() + 1).padStart(2, '0');
                        const day = String(date.getDate()).padStart(2, '0');
                        const hours = String(date.getHours()).padStart(2, '0');
                        const minutes = String(date.getMinutes()).padStart(2, '0');
                        const seconds = String(date.getSeconds()).padStart(2, '0');
                        const humanReadableDate = `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
                        newObj[key] = humanReadableDate
                    } else if (!key.includes("id")) {
                        newObj[key] = obj[key];
                    }
                });
                return newObj
            })

        }
        console.log("tmestmao")
        console.log(timestamps.value)
    } catch (error) {
        window.alert(error)
    }
}

getItems()


watch(() => [props.columns], () => {

    getItems()
})

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

</script>

<template>
    <div>
        <div class="table">
            <h1>{{ title }}</h1>
            <v-data-table :items="items" class="auto-width-table">
            </v-data-table>
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
.table {
    height: 100%
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