<template>
  <div class="date-filter">
    <VueDatePicker
      v-model="date"
      range
      :preset-dates="presetDates"
      :enable-time-picker="false"
      placeholder="Select a date range"
      @update:model-value="handleDateChange"
      :max-date="new Date()"
      teleport-center
      :text-input="textInputOptions"
    >
      <template #dp-input="{ value, onInput, onEnter, onBlur }">
        <v-btn
          variant="outlined"
          color="primary"
          prepend-icon="mdi-calendar-range"
          class="filter-btn"
          @click="onEnter"
        >
          <span class="filter-text">
            {{ value || 'Select date' }}
          </span>
          <v-icon class="ml-2">mdi-chevron-down</v-icon>
        </v-btn>
      </template>

      <template #preset-date-range-picker="{ label, value, isSelected, updateValue }">
        <span
          class="custom-preset-button"
          :class="{ 'selected': isSelected }"
          @click="updateValue(value)"
          >{{ label }}</span
        >
      </template>
    </VueDatePicker>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { VueDatePicker } from '@vuepic/vue-datepicker';
import '@vuepic/vue-datepicker/dist/main.css';

const emit = defineEmits(['update:modelValue', 'monthChange']);

const date = ref();

const textInputOptions = ref({
  format: 'dd/MM/yyyy'
});

onMounted(() => {
  const endDate = new Date();
  const startDate = new Date(new Date().setDate(endDate.getDate() - 7));
  date.value = [startDate, endDate];
  handleDateChange(date.value);
});

const handleDateChange = (newDate) => {
  if (newDate && newDate.length === 2) {
    const startStr = newDate[0].toISOString().split('T')[0];
    const endStr = newDate[1].toISOString().split('T')[0];
    const filterValue = `${startStr}|${endStr}`;
    emit('update:modelValue', filterValue);
    emit('monthChange', filterValue);
  } else if (!newDate) {
    emit('update:modelValue', '');
    emit('monthChange', '');
  }
};

const presetDates = ref([
  { label: 'Today', value: [new Date(), new Date()] },
  {
    label: 'Last 7 Days',
    value: [new Date(new Date().setDate(new Date().getDate() - 7)), new Date()],
  },
  {
    label: 'Last 30 Days',
    value: [new Date(new Date().setDate(new Date().getDate() - 30)), new Date()],
  },
  {
    label: 'This Month',
    value: [new Date(new Date().getFullYear(), new Date().getMonth(), 1), new Date(new Date().getFullYear(), new Date().getMonth() + 1, 0)],
  },
  {
    label: 'Last Month',
    value: [
      new Date(new Date().getFullYear(), new Date().getMonth() - 1, 1),
      new Date(new Date().getFullYear(), new Date().getMonth(), 0),
    ],
  },
]);
</script>

<style lang="scss">
.date-filter {
  width: 250px;
}
.custom-preset-button {
  padding: 5px 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
  margin: 5px;
  display: inline-block;
}
.custom-preset-button.selected {
  background-color: #007bff;
  color: white;
}
</style>
