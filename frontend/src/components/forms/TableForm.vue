<script setup>
import { ref, defineEmits } from 'vue';
import apiService from '../../services/apiService';

const emit = defineEmits(["cancel", "updateChart"])

const props = defineProps({
  title: {
    type: String,
    default: "Title"
  },
  columns: {
    type: Array,
    default: []
  },
  city: {
    type: String,
    required: true
  },
  tableId: {
    type: String,
    required: true
  }
})

const title = ref(props.title)
const refColumns = ref(props.columns)
//console.log("lklkslklsklsk")
//console.log(refColumns.value)
const error = ref(false)
const updateChart = () => {
  const obj = {}
  if (title.value != "") {
    obj["title"] = title.value
  }
  if (refColumns.value != "") {
    obj["columns"] = refColumns.value
  }
  emit("updateChart", obj)

}
const items = ref([])
async function getItems() {
  try {
    // Use API service to get KPI values
    const data = await apiService.getKPIValues(props.tableId);
    
    //console.log(props.columns)
    // Iterate over the list of strings and log each string
    if (props.columns.length > 0) {
      if (data != []) {
        for (const [key, value] of Object.entries(data[0])) {
          items.value.push(key)

        }
      }
    } else {
      if (data != []) {
        for (const [key, value] of Object.entries(data[0])) {
          items.value.push(key)

        }
      }
      refColumns.value = items.value


    }

    //console.log(items.value)
    //console.log(refColumns.value)
  } catch (error) {
    window.alert(error)
  }
}

getItems()

const selected = ref([])

const printt = () => {
  //console.log(items.value)
  //console.log(refColumns.value)
}

</script>

<template>
  <div class="popup">
    <div class="popup-inner">
      <label id="label" for="inputField">Title</label>
      <input type="text" id="inputField" v-model="title">
      <div class="checklist-container">
        <div class="checklist" v-for="value in items" :key="value">
          <input type="checkbox" :value="value" v-model="refColumns" @click="printt">
          <label>{{ value }}</label>
        </div>
      </div>
      <p v-if="error" style="color: red;"> Please enter a value! </p>
      <v-btn class="popup-button" @click="$emit('cancel')">Cancel</v-btn>
      <v-btn class="popup-button" @click="updateChart">Add Changes</v-btn>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.popup {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 98;
  background-color: rgba(0, 0, 0, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;

  .popup-inner {
    background: #ffffff;
    padding: 50px;
    max-height: 80vh;
    overflow-y: auto;
    min-width: 400px;
  }

  #label {
    font-weight: bold;
  }

  .label {
    font-weight: bold;
    margin-bottom: 5px;
  }

  #inputField {
    border: 3px solid #555;
    padding: 8px;
    font-size: 14px;
    display: flex;
  }

  .colorPicker {
    display: flex;
    /* Use flexbox */
    align-items: center;
    /* Center items vertically */
  }


  .popup-button {
    margin: 5px;
  }

  .checklist-container {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    margin: 15px 0;
  }

  .checklist {
    display: flex;
    align-items: center;
    gap: 5px;
    white-space: nowrap;
  }

}
</style>