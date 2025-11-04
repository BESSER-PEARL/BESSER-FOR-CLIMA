<script setup>
import { ref, defineEmits } from 'vue';

const emit = defineEmits(["cancel", "updateChart"])

const props = defineProps({
  title: {
    type: String,
    default: "Title"
  },
  suffix: {
    type: String,
    default: ""
  }
})

const title = ref(props.title)
const suffix = ref(props.suffix)
const error = ref(false)
const updateChart = () => {
  const obj = {}
  if (title.value != "") {
    obj["title"] = title.value
  }
  if (suffix.value != "") {
    obj["suffix"] = suffix.value
  }
  emit("updateChart", obj)

}

</script>

<template>
  <div class="popup">
    <div class="popup-inner">
      <label id="label" for="inputField">Title</label>
      <input type="text" id="inputField" v-model="title">
      <label id="label" for="inputField">Unit of Value</label>
      <input type="text" id="inputField" v-model="suffix">
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
    display: flex; /* Use flexbox */
    align-items: center; /* Center items vertically */
  }
  
  #inputFieldColor {

    margin-right: 10px; /* Add some spacing between the input field and button */
    border: 3px solid #555;
    padding: 8px;
    font-size: 14px;
    width: 30%
  }

  .color-button {
    margin: 5px;
  }

  .popup-button {
    margin: 5px;
  }

}
</style>