<script setup>
import { ref, defineEmits, inject } from 'vue';

const emit = defineEmits(["cancel","addElement", "createVisualisation"])

const props = defineProps({
    label: {
        type: String,
        required: true
    },
    city: {
        type: String,
        required: true
    },
    chart: {
        type: String,
        required: true
    }
})


const textValue = ref("")
const error = ref(false)
const addElement = () => {
  error.value = false
  if (textValue.value == ""){
    error.value = true
  } else {
    error.value = false
    emit("addElement", textValue.value)
  }
}

const items = ref([]) 
const itemObjects = ref([])
const table = ref("")

async function getItem(){
    try{
        const response = await fetch('http://localhost:8000/' +props.city.toLowerCase()+'/kpis')
        const data = await response.json();
        
        // Iterate over the list of strings and log each string
        var ll = []
        data.forEach(item => {
            ll.push(item)
            // Do whatever you want with each item here
        });
        items.value = ll
        itemObjects.value = data
    } catch (error) {
        window.alert(error)
    }
}
getItem()


const createVisualisation = () => {    
    emit('createVisualisation', table.value.id, table.value.name, props.chart, table.value)
}

</script>

<template>
  <div class="popup">
    <div class="popup-inner">
      <label style="padding:5px" for="data-source-select">Select the data you want to display</label>
        <v-select
        v-model="table"
        :items="items"
        item-title="name"
        density="comfortable"
        label="Data source"
        style="margin-top:10px"
        menu="true"
        return-object
      ></v-select>
        <p v-if="error" style="color: red;"> Please choose a value! </p>
      <v-btn class="popup-button" @click="$emit('cancel')">Cancel</v-btn>
      <v-btn class="popup-button" @click="createVisualisation">Add Element</v-btn>
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
  z-index: 99;
  background-color: rgba(0, 0, 0, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;

  .popup-inner {
    background: #ffffff;
    padding: 50px;
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

  .popup-button {
    margin: 5px; 
  }

}



</style>