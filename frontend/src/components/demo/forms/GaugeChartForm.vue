<template>
  <div class="popup">
    <div class="popup-inner">
      <label id="label" for="inputField">Title</label>
      <input type="text" id="inputField" v-model="title">
      <label id="label" for="inputField">Value</label>
      <input type="number" id="inputField" v-model="value">
      <p v-if="error" style="color: red;"> Please enter a value! </p>
      <v-btn class="popup-button" @click="$emit('cancel')">Cancel</v-btn>
      <v-btn class="popup-button" @click="updateChart">Add Changes</v-btn>
    </div>
  </div>
</template>

<script setup>
import { ref, defineEmits } from 'vue';

const emit = defineEmits(["cancel", "updateChart"]);

const props = defineProps({
  title: {
    type: String,
    default: "Gauge Chart"
  },
  value: {
    type: Number,
    default: 50
  }
});

const title = ref(props.title);
const value = ref(props.value);
const error = ref(false);

const updateChart = () => {
  const obj = {};
  if (title.value != "") {
    obj["title"] = title.value;
  }
  if (value.value != null) {
    obj["value"] = value.value;
  }
  emit("updateChart", obj);
};
</script>

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

  .popup-button {
    margin: 5px;
  }
}
</style> 