<template>
  <div class="date-filter">
    <v-menu
      v-model="menu"
      :close-on-content-click="false"
      transition="scale-transition"
      offset-y
      min-width="auto"
    >
      <template v-slot:activator="{ props: menuProps }">
        <v-btn
          v-bind="menuProps"
          variant="outlined"
          color="primary"
          prepend-icon="mdi-calendar-range"
          class="filter-btn"
        >
          <span class="filter-text">
            {{ selectedDateLabel }}
          </span>
          <v-icon class="ml-2">mdi-chevron-down</v-icon>
        </v-btn>
      </template>
      
      <v-card class="date-picker-card">
        <v-card-title class="picker-header">
          <v-icon size="20">mdi-calendar-range</v-icon>
          <span>Filter by Date</span>
        </v-card-title>
        
        <v-divider></v-divider>
        
        <v-card-text class="pa-0">
          <!-- Quick Presets -->
          <div class="quick-presets">
            <v-chip
              v-for="preset in quickPresets"
              :key="preset.label"
              @click="applyPreset(preset)"
              :color="isPresetActive(preset) ? 'primary' : 'default'"
              :variant="isPresetActive(preset) ? 'flat' : 'outlined'"
              size="small"
              class="preset-chip"
            >
              {{ preset.label }}
            </v-chip>
          </div>

          <v-divider></v-divider>

          <!-- Date Picker -->
          <v-date-picker
            v-model="selectedDates"
            :max="maxDate"
            :min="minDate"
            color="primary"
            elevation="0"
            multiple="range"
            show-adjacent-months
          ></v-date-picker>
        </v-card-text>

        <v-divider></v-divider>

        <v-card-actions class="picker-actions">
          <v-btn
            variant="text"
            color="error"
            @click="clearFilter"
            prepend-icon="mdi-close-circle"
          >
            Clear
          </v-btn>
          <v-spacer />
          <v-btn
            variant="text"
            @click="menu = false"
          >
            Cancel
          </v-btn>
          <v-btn
            variant="flat"
            color="primary"
            @click="applyFilter"
            prepend-icon="mdi-check"
          >
            Apply
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-menu>
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

const menu = ref(false);
const selectedDates = ref([]);
const activeFilter = ref(null);

// Set max date to today and min date to 3 years ago
const maxDate = computed(() => new Date());

const minDate = computed(() => {
  const now = new Date();
  return new Date(now.getFullYear() - 3, 0, 1);
});

// Quick preset options
const quickPresets = computed(() => {
  const now = new Date();
  
  return [
    {
      label: 'This Month',
      type: 'month',
      start: new Date(now.getFullYear(), now.getMonth(), 1),
      end: new Date(now.getFullYear(), now.getMonth() + 1, 0)
    },
    {
      label: 'Last Month',
      type: 'month',
      start: new Date(now.getFullYear(), now.getMonth() - 1, 1),
      end: new Date(now.getFullYear(), now.getMonth(), 0)
    },
    {
      label: 'Last 7 Days',
      type: 'range',
      start: new Date(now.getFullYear(), now.getMonth(), now.getDate() - 6),
      end: new Date(now.getFullYear(), now.getMonth(), now.getDate())
    },
    {
      label: 'Last 30 Days',
      type: 'range',
      start: new Date(now.getFullYear(), now.getMonth(), now.getDate() - 29),
      end: new Date(now.getFullYear(), now.getMonth(), now.getDate())
    },
    {
      label: 'This Year',
      type: 'range',
      start: new Date(now.getFullYear(), 0, 1),
      end: new Date(now.getFullYear(), 11, 31)
    }
  ];
});

// Format date for display
const formatDate = (date) => {
  if (!date) return 'Select date';
  return new Date(date).toLocaleDateString('en-US', { 
    year: 'numeric', 
    month: 'short', 
    day: 'numeric' 
  });
};

// Format selected period label
const selectedDateLabel = computed(() => {
  if (!activeFilter.value) {
    return 'All Time';
  }
  
  // Check if it's a month filter (backend format YYYY-MM)
  if (activeFilter.value.match(/^\d{4}-\d{2}$/)) {
    const [year, month] = activeFilter.value.split('-');
    const monthNames = [
      'January', 'February', 'March', 'April', 'May', 'June',
      'July', 'August', 'September', 'October', 'November', 'December'
    ];
    return `${monthNames[parseInt(month) - 1]} ${year}`;
  }
  
  // Check if it's a date range (format: start|end)
  if (activeFilter.value.includes('|')) {
    const [start, end] = activeFilter.value.split('|');
    const startDate = formatDate(start);
    const endDate = formatDate(end);
    
    // Check if it matches a preset
    const preset = quickPresets.value.find(p => {
      const pStart = p.start.toISOString().split('T')[0];
      const pEnd = p.end.toISOString().split('T')[0];
      return pStart === start && pEnd === end;
    });
    
    if (preset) {
      return preset.label;
    }
    
    return `${startDate} - ${endDate}`;
  }
  
  return 'All Time';
});

// Check if a preset is currently active
const isPresetActive = (preset) => {
  if (!activeFilter.value) return false;
  
  const pStart = preset.start.toISOString().split('T')[0];
  const pEnd = preset.end.toISOString().split('T')[0];
  
  // For month presets, check if it matches YYYY-MM format
  if (preset.type === 'month') {
    const year = preset.start.getFullYear();
    const month = String(preset.start.getMonth() + 1).padStart(2, '0');
    return activeFilter.value === `${year}-${month}`;
  }
  
  // For range presets, check if it matches start|end format
  if (activeFilter.value.includes('|')) {
    const [start, end] = activeFilter.value.split('|');
    return pStart === start && pEnd === end;
  }
  
  return false;
};

// Apply a preset
const applyPreset = (preset) => {
  const start = preset.start;
  const end = preset.end;
  
  selectedDates.value = [start, end];
  
  // If it's a full month preset, send in YYYY-MM format for backend compatibility
  if (preset.type === 'month') {
    const year = start.getFullYear();
    const month = String(start.getMonth() + 1).padStart(2, '0');
    activeFilter.value = `${year}-${month}`;
  } else {
    // For date ranges, send as start|end
    const startStr = start.toISOString().split('T')[0];
    const endStr = end.toISOString().split('T')[0];
    activeFilter.value = `${startStr}|${endStr}`;
  }
  
  emit('update:modelValue', activeFilter.value);
  emit('monthChange', activeFilter.value);
  menu.value = false;
};

// Apply the selected filter
const applyFilter = () => {
  console.log('Apply filter - selectedDates:', selectedDates.value);
  
  if (!selectedDates.value || selectedDates.value.length === 0) {
    console.log('No dates selected, clearing filter');
    clearFilter();
    return;
  }
  
  // Handle array of dates (range selection)
  if (Array.isArray(selectedDates.value) && selectedDates.value.length >= 2) {
    const start = new Date(selectedDates.value[0]);
    const end = new Date(selectedDates.value[1]);
    
    // Ensure start is before end
    const [startDate, endDate] = start <= end ? [start, end] : [end, start];
    
    console.log('Date range selected:', startDate, 'to', endDate);
    
    // Check if it's a full month (1st day to last day)
    const isFullMonth = startDate.getDate() === 1 && 
                       endDate.getDate() === new Date(endDate.getFullYear(), endDate.getMonth() + 1, 0).getDate() &&
                       startDate.getMonth() === endDate.getMonth() &&
                       startDate.getFullYear() === endDate.getFullYear();
    
    if (isFullMonth) {
      // Send as YYYY-MM for backend compatibility
      const year = startDate.getFullYear();
      const month = String(startDate.getMonth() + 1).padStart(2, '0');
      activeFilter.value = `${year}-${month}`;
      console.log('Full month detected, sending:', activeFilter.value);
    } else {
      // Send as date range
      const startStr = startDate.toISOString().split('T')[0];
      const endStr = endDate.toISOString().split('T')[0];
      activeFilter.value = `${startStr}|${endStr}`;
      console.log('Date range, sending:', activeFilter.value);
    }
    
    emit('update:modelValue', activeFilter.value);
    emit('monthChange', activeFilter.value);
  } else if (selectedDates.value.length === 1 || !Array.isArray(selectedDates.value)) {
    // Single date selected or direct date object - treat as that day only
    const date = new Date(Array.isArray(selectedDates.value) ? selectedDates.value[0] : selectedDates.value);
    const dateStr = date.toISOString().split('T')[0];
    activeFilter.value = `${dateStr}|${dateStr}`;
    console.log('Single date selected, sending:', activeFilter.value);
    
    emit('update:modelValue', activeFilter.value);
    emit('monthChange', activeFilter.value);
  }
  
  menu.value = false;
};

// Clear filter
const clearFilter = () => {
  activeFilter.value = null;
  selectedDates.value = [];
  emit('update:modelValue', '');
  emit('monthChange', '');
  menu.value = false;
};

// Initialize from modelValue
const initializeFromModelValue = () => {
  if (!props.modelValue) {
    activeFilter.value = null;
    selectedDates.value = [];
    return;
  }
  
  activeFilter.value = props.modelValue;
  
  // Check if it's a date range (contains |)
  if (props.modelValue.includes('|')) {
    const [start, end] = props.modelValue.split('|');
    selectedDates.value = [new Date(start), new Date(end)];
  } else if (props.modelValue.match(/^\d{4}-\d{2}$/)) {
    // It's a month format (YYYY-MM) - convert to date range
    const [year, month] = props.modelValue.split('-');
    const firstDay = new Date(parseInt(year), parseInt(month) - 1, 1);
    const lastDay = new Date(parseInt(year), parseInt(month), 0);
    selectedDates.value = [firstDay, lastDay];
  }
};

initializeFromModelValue();

// Watch for external changes
watch(() => props.modelValue, (newVal) => {
  if (!newVal) {
    activeFilter.value = null;
    selectedDates.value = [];
  } else {
    initializeFromModelValue();
  }
});

// Watch selectedDates for debugging
watch(() => selectedDates.value, (newVal) => {
  console.log('selectedDates changed:', newVal);
}, { deep: true });
</script>

<style lang="scss" scoped>
.date-filter {
  display: inline-block;

  .filter-btn {
    text-transform: none;
    font-weight: 500;
    border-radius: 8px;
    min-width: 200px;
    justify-content: space-between;
    border: 2px solid;
    padding: 8px 16px;
    height: 44px;

    .filter-text {
      flex: 1;
      text-align: left;
      font-size: 14px;
    }

    &:hover {
      background-color: rgba(1, 119, 169, 0.04);
    }
  }
}

.date-picker-card {
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  max-width: 380px;

  .picker-header {
    background: linear-gradient(135deg, #0177a9 0%, #06b6d4 100%);
    color: white;
    padding: 12px 16px;
    display: flex;
    align-items: center;
    gap: 10px;

    span {
      font-size: 1rem;
      font-weight: 600;
    }

    .v-icon {
      opacity: 0.9;
    }
  }

  .quick-presets {
    padding: 12px 16px;
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    background: #f8f9fa;

    .preset-chip {
      cursor: pointer;
      font-weight: 500;
      font-size: 0.75rem;
      height: 28px;
      transition: all 0.2s ease;

      &:hover {
        transform: translateY(-1px);
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
      }
    }
  }

  :deep(.v-date-picker) {
    width: 100%;
    box-shadow: none;

    .v-date-picker-header {
      padding: 8px 16px;
      
      .v-btn {
        font-size: 0.9rem;
      }
    }

    .v-date-picker-month {
      padding: 8px 12px 12px;
      
      .v-btn {
        font-size: 0.85rem;
        min-width: 36px;
        height: 36px;
        margin: 1px;
      }
    }

    .v-btn {
      text-transform: none;
    }
  }

  .picker-actions {
    padding: 10px 16px;
    background: #f8f9fa;
    gap: 8px;

    .v-btn {
      text-transform: none;
      font-weight: 500;
      border-radius: 8px;
      font-size: 0.875rem;
      padding: 0 16px;
      height: 36px;
    }
  }
}

// Mobile responsive
@media (max-width: 600px) {
  .date-picker-card {
    max-width: 100%;

    .picker-header {
      padding: 10px 14px;

      span {
        font-size: 0.95rem;
      }
    }

    .quick-presets {
      padding: 10px 14px;

      .preset-chip {
        flex: 1 1 calc(50% - 3px);
        min-width: 100px;
        justify-content: center;
        font-size: 0.7rem;
      }
    }
  }

  .filter-btn {
    min-width: 160px !important;
    font-size: 0.9rem;
  }
}
</style>
