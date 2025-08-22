<template>
  <div class="month-filter">
    <div class="filter-container">
      <label for="month-select" class="filter-label">Filter by Month:</label>
      <select 
        id="month-select" 
        v-model="selectedMonth" 
        @change="onMonthChange"
        class="month-select"
      >
        <option value="">All Months</option>
        <option 
          v-for="month in allMonths" 
          :key="month.value" 
          :value="month.value"
        >
          {{ month.label }}
        </option>
      </select>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue';

const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  }
});

const emit = defineEmits(['update:modelValue', 'monthChange']);

const selectedMonth = ref(props.modelValue);

// Generate all 12 months for the current year and previous year
const allMonths = computed(() => {
  const months = [];
  const currentYear = new Date().getFullYear();
  const monthNames = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
  ];

  // Add current year months
  for (let i = 0; i < 12; i++) {
    const monthValue = `${currentYear}-${String(i + 1).padStart(2, '0')}`;
    const monthLabel = `${monthNames[i]} ${currentYear}`;
    months.push({ value: monthValue, label: monthLabel });
  }

  // Add previous year months
  const previousYear = currentYear - 1;
  for (let i = 0; i < 12; i++) {
    const monthValue = `${previousYear}-${String(i + 1).padStart(2, '0')}`;
    const monthLabel = `${monthNames[i]} ${previousYear}`;
    months.push({ value: monthValue, label: monthLabel });
  }

  // Sort by date (most recent first)
  return months.sort((a, b) => b.value.localeCompare(a.value));
});

const onMonthChange = () => {
  emit('update:modelValue', selectedMonth.value);
  emit('monthChange', selectedMonth.value);
};

// Watch for external changes
watch(() => props.modelValue, (newVal) => {
  selectedMonth.value = newVal;
});
</script>

<style lang="scss" scoped>
.month-filter {
  margin-bottom: 10px;
}

.filter-container {
  display: flex;
  align-items: center;
  gap: 10px;
}

.filter-label {
  font-size: 14px;
  font-weight: 500;
  color: #333;
  min-width: 120px;
}

.month-select {
  padding: 8px 12px;
  border: 2px solid #0177a9;
  border-radius: 5px;
  background-color: white;
  color: #0177a9;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s;
  outline: none;
  min-width: 180px;

  &:hover {
    border-color: #014a6b;
    background-color: #f8f9fa;
  }

  &:focus {
    border-color: #013a52;
    box-shadow: 0 0 0 2px rgba(1, 119, 169, 0.2);
  }
}
</style>
