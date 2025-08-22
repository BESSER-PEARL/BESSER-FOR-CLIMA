<script setup>
import { ref, defineEmits } from 'vue';

const emit = defineEmits(["cancel", "updateChart"])

const props = defineProps({
  label: {
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
  }
})

const title = ref(props.title)
const error = ref(false)
const xtitle = ref(props.xtitle)
const ytitle = ref(props.ytitle)
const color = ref(props.color)
const colorPicker = ref(false)
const updateChart = () => {
  const obj = {}
  if (title.value != "") {
    obj["title"] = title.value
  }
  if (xtitle.value != "") {
    obj["xtitle"] = xtitle.value
  }
  if (ytitle.value != "") {
    obj["ytitle"] = ytitle.value
  }
  if (color.value != "") {
  //console.log(color.value)
    obj["color"] = color.value
  }
  emit("updateChart", obj)

}

const toggleColorPicker = () => {
  colorPicker.value = !colorPicker.value
}




</script>

<template>
  <div class="popup">
    <div class="popup-inner">
      <label id="label" for="inputField">Title</label>
      <input type="text" id="inputField" v-model="title">
      <label id="label" for="inputField">x-Title</label>
      <input type="text" id="inputField" v-model="xtitle">
      <label id="label" for="inputField">y-Title</label>
      <input type="text" id="inputField" v-model="ytitle">
      <label id="label" for="colorPicker">Line color</label>
      <div class="colorPicker">
        <input type="text" id="inputFieldColor" v-model="color">
        <v-btn class="color-button" :style="{'background-color': color}" @click="toggleColorPicker"></v-btn>
        <v-color-picker v-if=colorPicker hide-inputs v-model="color"></v-color-picker>
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