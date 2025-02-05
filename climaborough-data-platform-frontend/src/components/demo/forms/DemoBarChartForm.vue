<script setup>
import { ref, defineEmits } from 'vue';

const emit = defineEmits(["cancel", "updateChart"])

const props = defineProps({
  title: {
    type: String,
    default: "Title"
  },
  series: {
    type: Array,
    default: () => []
  },
  labels: {
    type: Array,
    default: () => []
  }
})

const title = ref(props.title)
const chartValues = ref(props.series.map((value, index) => ({
  label: props.labels[index] || `Category ${index + 1}`,
  value: value
})))

const error = ref(false)

const addCategory = () => {
  chartValues.value.push({
    label: `Category ${chartValues.value.length + 1}`,
    value: 0
  })
}

const removeCategory = (index) => {
  chartValues.value.splice(index, 1)
}

const updateChart = () => {
  const obj = {}
  if (title.value != "") {
    obj["title"] = title.value
  }
  obj["series"] = chartValues.value.map(item => item.value)
  obj["labels"] = chartValues.value.map(item => item.label)
  emit("updateChart", obj)
}
</script>

<template>
  <div class="popup">
    <div class="popup-inner">
      <div class="form-group">
        <label id="label" for="inputField">Title</label>
        <input type="text" id="inputField" v-model="title">
      </div>

      <div class="categories-section">
        <h3>Categories</h3>
        <div v-for="(category, index) in chartValues" :key="index" class="category-input">
          <div class="input-group">
            <input type="text" v-model="category.label" placeholder="Category name">
            <input type="number" v-model.number="category.value" placeholder="Value">
            <v-btn icon="mdi-delete" color="error" @click="removeCategory(index)" class="remove-btn">
              <Icon icon="material-symbols-light:delete-outline" width="20" height="20" />
            </v-btn>
          </div>
        </div>
        <v-btn class="add-category-btn" @click="addCategory">Add Category</v-btn>
      </div>

      <p v-if="error" style="color: red;">Please enter a value!</p>
      
      <div class="button-group">
        <v-btn class="popup-button" @click="$emit('cancel')">Cancel</v-btn>
        <v-btn class="popup-button" @click="updateChart">Add Changes</v-btn>
      </div>
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
    min-width: 500px;
    max-height: 80vh;
    overflow-y: auto;
  }

  .form-group {
    margin-bottom: 20px;
  }

  #label {
    font-weight: bold;
    display: block;
    margin-bottom: 8px;
  }

  #inputField {
    border: 2px solid #555;
    padding: 8px;
    font-size: 14px;
    width: 100%;
    margin-bottom: 20px;
  }

  .categories-section {
    margin-top: 20px;

    h3 {
      margin-bottom: 15px;
    }
  }

  .category-input {
    margin-bottom: 10px;

    .input-group {
      display: flex;
      gap: 10px;
      align-items: center;

      input {
        border: 2px solid #555;
        padding: 8px;
        font-size: 14px;

        &[type="text"] {
          flex: 2;
        }

        &[type="number"] {
          flex: 1;
        }
      }
    }
  }

  .add-category-btn {
    margin-top: 10px;
    width: 100%;
  }

  .button-group {
    margin-top: 20px;
    display: flex;
    justify-content: flex-end;
    gap: 10px;
  }
}
</style>