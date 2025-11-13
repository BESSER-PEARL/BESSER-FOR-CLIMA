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
      format="dd/MM/yyyy"
      preview-format="dd/MM/yyyy"
      hide-offset-dates
      auto-apply
      :text-input="textInputOptions"
    >
      <template #dp-input="{ value }">
        <v-btn
          variant="outlined"
          color="primary"
          prepend-icon="mdi-calendar-range"
          class="filter-btn"
        >
          <span class="filter-text">
            {{ formatDisplayDate(date) || 'Select date' }}
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

const formatDisplayDate = (dateArray) => {
  if (!dateArray || !Array.isArray(dateArray)) return '';
  
  const formatSingle = (d) => {
    if (!d) return '';
    const day = String(d.getDate()).padStart(2, '0');
    const month = String(d.getMonth() + 1).padStart(2, '0');
    const year = d.getFullYear();
    return `${day}/${month}/${year}`;
  };
  
  return `${formatSingle(dateArray[0])} - ${formatSingle(dateArray[1])}`;
};

onMounted(() => {
  const endDate = new Date();
  const startDate = new Date();
  startDate.setDate(endDate.getDate() - 7);
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
    value: (() => {
      const end = new Date();
      const start = new Date();
      start.setDate(end.getDate() - 7);
      return [start, end];
    })(),
  },
  {
    label: 'Last 30 Days',
    value: (() => {
      const end = new Date();
      const start = new Date();
      start.setDate(end.getDate() - 30);
      return [start, end];
    })(),
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
