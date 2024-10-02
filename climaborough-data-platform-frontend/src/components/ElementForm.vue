<script setup>
import { ref, defineEmits } from 'vue';

const emit = defineEmits(["cancel","addElement"])

const props = defineProps({
    label: {
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
    console.log("erm herrro")
  } else {
    error.value = false
    emit("addElement", textValue.value)
  }
}



</script>

<template>
  <div class="popup">
    <div class="popup-inner">
        <label id="label" for="inputField">{{ label }}</label>
        <input type="text" id="inputField" v-model="textValue">
        <p v-if="error" style="color: red;"> Please enter a value! </p>
      <v-btn class="popup-button" @click="$emit('cancel')">Cancel</v-btn>
      <v-btn class="popup-button" @click="addElement">Add Element</v-btn>
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