<script setup>
import { ref, defineEmits, computed } from 'vue';

const emit = defineEmits(["cancel","addElement", "createVisualisation"])

const props = defineProps({
    label: {
        type: String,
        required: false,
        default: 'Data source'
    },
    city: {
        type: String,
        required: true
    },
    cityId: {
        type: Number,
        required: false,
        default: null
    },
    chart: {
        type: String,
        required: true
    }
})

const textValue = ref("")
const error = ref(false)
const searchQuery = ref("")
const loading = ref(false)

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

// Get chart type icon
const chartIcon = computed(() => {
    const icons = {
        'linechart': 'mdi-chart-line',
        'barchart': 'mdi-chart-bar',
        'piechart': 'mdi-chart-pie',
        'statchart': 'mdi-speedometer',
        'table': 'mdi-table',
        'map': 'mdi-map'
    };
    return icons[props.chart.toLowerCase()] || 'mdi-chart-box';
});

// Get chart type display name
const chartDisplayName = computed(() => {
    const names = {
        'linechart': 'Line Chart',
        'barchart': 'Bar Chart',
        'piechart': 'Pie Chart',
        'statchart': 'Stat Widget',
        'table': 'Table',
        'map': 'Map'
    };
    return names[props.chart.toLowerCase()] || props.chart;
});

// Function to sort KPIs based on chart type using has_category_label
const sortKPIsForChart = (kpis, chartType) => {
    const isBarOrPieChart = chartType.toLowerCase() === 'barchart' || chartType.toLowerCase() === 'piechart';

    return kpis.sort((a, b) => {
        if (isBarOrPieChart) {
            // For Bar/Pie charts, prioritize KPIs with has_category_label
            if (a.has_category_label && !b.has_category_label) return -1;
            if (!a.has_category_label && b.has_category_label) return 1;
        } else {
            // For other charts, prioritize KPIs without has_category_label
            if (!a.has_category_label && b.has_category_label) return -1;
            if (a.has_category_label && !b.has_category_label) return 1;
        }
        // Secondary sort by name
        return a.name.localeCompare(b.name);
    });
}

// Function to add recommendation labels using has_category_label
const addRecommendationLabels = (kpis, chartType) => {
    const isBarOrPieChart = chartType.toLowerCase() === 'barchart' || chartType.toLowerCase() === 'piechart';

    return kpis.map(kpi => {
        const hasCategoryLabel = kpi.has_category_label;
        let isRecommended = false;
        let warningMessage = '';

        if (isBarOrPieChart) {
            isRecommended = hasCategoryLabel;
            if (!hasCategoryLabel) {
                warningMessage = 'No category labels - may not display optimally';
            }
        } else {
            isRecommended = !hasCategoryLabel;
            if (hasCategoryLabel) {
                warningMessage = 'Better suited for Bar/Pie charts';
            }
        }

        return {
            ...kpi,
            isRecommended,
            warningMessage,
            displayName: kpi.name
        };
    });
}

// Filtered items based on search
const filteredItems = computed(() => {
    if (!searchQuery.value) {
        return items.value;
    }
    
    const query = searchQuery.value.toLowerCase();
    return items.value.filter(item => 
        item.name.toLowerCase().includes(query) ||
        item.description?.toLowerCase().includes(query)
    );
});

// Count of recommended vs not recommended
const recommendationStats = computed(() => {
    const recommended = items.value.filter(item => item.isRecommended).length;
    const total = items.value.length;
    return { recommended, total, notRecommended: total - recommended };
});

async function getItem(){
    try{
        loading.value = true;
        if (!props.cityId) {
            console.warn('KPIForm: No cityId provided');
            items.value = [];
            itemObjects.value = [];
            return;
        }
        const response = await fetch(`http://localhost:8000/kpis/?city_id=${props.cityId}`);
        if (!response.ok) {
            throw new Error(`API request failed: ${response.status}`);
        }
        const data = await response.json();

        // Sort and add recommendation labels based on chart type
        const sortedKPIs = sortKPIsForChart(data, props.chart);
        const labeledKPIs = addRecommendationLabels(sortedKPIs, props.chart);

        items.value = labeledKPIs;
        itemObjects.value = data;
    } catch (error) {
        console.error('Error fetching KPIs:', error);
        items.value = [];
        itemObjects.value = [];
    } finally {
        loading.value = false;
    }
}
getItem()

const createVisualisation = () => {    
    if (!table.value) {
        error.value = true;
        return;
    }
    emit('createVisualisation', table.value.id, table.value.name, props.chart, table.value)
}

</script>

<template>
  <div class="popup" @click.self="$emit('cancel')">
    <div class="popup-inner">
      <!-- Header -->
      <div class="popup-header">
        <div class="header-content">
          <v-icon :icon="chartIcon" size="32" color="primary"></v-icon>
          <div class="header-text">
            <h3>Add {{ chartDisplayName }}</h3>
            <p class="subtitle">Select a KPI to visualize</p>
          </div>
        </div>
        <v-btn 
          icon="mdi-close" 
          variant="text" 
          @click="$emit('cancel')"
          class="close-btn"
        ></v-btn>
      </div>

      <v-divider></v-divider>

      <!-- Info Banner -->
      <v-alert
        v-if="recommendationStats.total > 0"
        :icon="chartIcon"
        density="compact"
        class="recommendation-alert"
        color="info"
        variant="tonal"
      >
        <div class="alert-content">
          <strong>{{ recommendationStats.recommended }}</strong> of {{ recommendationStats.total }} KPIs 
          are recommended for {{ chartDisplayName }}
        </div>
      </v-alert>

      <!-- Search Bar -->
      <div class="search-container">
        <v-text-field
          v-model="searchQuery"
          prepend-inner-icon="mdi-magnify"
          label="Search KPIs"
          placeholder="Type to search by name or description..."
          variant="outlined"
          density="comfortable"
          clearable
          hide-details
          class="search-field"
        ></v-text-field>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="loading-container">
        <v-progress-circular
          indeterminate
          color="primary"
          size="48"
        ></v-progress-circular>
        <p class="loading-text">Loading KPIs...</p>
      </div>

      <!-- KPI Selection -->
      <div v-else class="kpi-selection">
        <v-list class="kpi-list" v-if="filteredItems.length > 0">
          <v-list-item
            v-for="item in filteredItems"
            :key="item.id"
            :value="item"
            @click="table = item"
            :active="table?.id === item.id"
            class="kpi-list-item"
            :class="{ 'recommended': item.isRecommended, 'selected': table?.id === item.id }"
          >
            <template v-slot:prepend>
              <v-avatar
                :color="item.isRecommended ? 'success' : 'warning'"
                size="40"
              >
                <v-icon 
                  :icon="item.isRecommended ? 'mdi-check-circle' : 'mdi-alert-circle'"
                  color="white"
                ></v-icon>
              </v-avatar>
            </template>

            <v-list-item-title class="kpi-title">
              {{ item.name }}
            </v-list-item-title>

            <v-list-item-subtitle v-if="item.description" class="kpi-description">
              {{ item.description }}
            </v-list-item-subtitle>

            <v-list-item-subtitle v-if="item.warningMessage" class="kpi-warning">
              <v-icon size="14" class="mr-1">mdi-information</v-icon>
              {{ item.warningMessage }}
            </v-list-item-subtitle>

            <template v-slot:append>
              <v-chip
                :color="item.isRecommended ? 'success' : 'warning'"
                size="small"
                variant="flat"
              >
                {{ item.isRecommended ? 'Recommended' : 'Alternative' }}
              </v-chip>
            </template>
          </v-list-item>
        </v-list>

        <!-- Empty State -->
        <div v-else class="empty-state">
          <v-icon icon="mdi-database-search" size="64" color="grey"></v-icon>
          <h4>No KPIs Found</h4>
          <p v-if="searchQuery">Try adjusting your search criteria</p>
          <p v-else>No KPIs available for this city</p>
        </div>
      </div>

      <!-- Error Message -->
      <v-alert
        v-if="error"
        type="error"
        variant="tonal"
        density="compact"
        class="error-alert"
      >
        Please select a KPI to continue
      </v-alert>

      <v-divider></v-divider>

      <!-- Actions -->
      <div class="popup-actions">
        <v-btn
          variant="outlined"
          size="large"
          @click="$emit('cancel')"
          prepend-icon="mdi-close"
        >
          Cancel
        </v-btn>
        <v-btn
          color="primary"
          size="large"
          @click="createVisualisation"
          :disabled="!table"
          prepend-icon="mdi-plus"
        >
          Add Visualization
        </v-btn>
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
  z-index: 9999;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  backdrop-filter: blur(4px);

  .popup-inner {
    background: #ffffff;
    border-radius: 16px;
    width: 100%;
    max-width: 800px;
    max-height: 90vh;
    display: flex;
    flex-direction: column;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
    overflow: hidden;
  }

  .popup-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 24px;
    background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);

    .header-content {
      display: flex;
      align-items: center;
      gap: 16px;

      .header-text {
        h3 {
          margin: 0;
          font-size: 24px;
          font-weight: 600;
          color: #333;
        }

        .subtitle {
          margin: 4px 0 0 0;
          font-size: 14px;
          color: #666;
        }
      }
    }

    .close-btn {
      opacity: 0.7;
      transition: opacity 0.2s;

      &:hover {
        opacity: 1;
      }
    }
  }

  .recommendation-alert {
    margin: 16px 24px 0;
    border-radius: 8px;

    .alert-content {
      font-size: 14px;
    }
  }

  .search-container {
    padding: 16px 24px;

    .search-field {
      :deep(.v-field) {
        border-radius: 12px;
      }
    }
  }

  .loading-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 60px 24px;
    gap: 16px;

    .loading-text {
      color: #666;
      font-size: 16px;
      margin: 0;
    }
  }

  .kpi-selection {
    flex: 1;
    overflow-y: auto;
    padding: 0 24px;
    min-height: 300px;

    .kpi-list {
      padding: 0;

      .kpi-list-item {
        border: 2px solid transparent;
        border-radius: 12px;
        margin-bottom: 8px;
        padding: 12px;
        transition: all 0.2s ease;
        cursor: pointer;

        &.recommended {
          background-color: rgba(76, 175, 80, 0.02);
        }

        &.selected {
          border-color: #1976d2;
          background-color: rgba(25, 118, 210, 0.05);
        }

        &:hover {
          background-color: rgba(0, 0, 0, 0.02);
          transform: translateX(4px);
        }

        .kpi-title {
          font-weight: 600;
          font-size: 16px;
          color: #333;
          margin-bottom: 4px;
        }

        .kpi-description {
          font-size: 13px;
          color: #666;
          margin-top: 4px;
          line-height: 1.4;
        }

        .kpi-warning {
          font-size: 12px;
          color: #f57c00;
          margin-top: 6px;
          display: flex;
          align-items: center;
        }
      }
    }

    .empty-state {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 60px 24px;
      text-align: center;

      h4 {
        margin: 16px 0 8px;
        font-size: 20px;
        color: #333;
      }

      p {
        margin: 0;
        color: #666;
        font-size: 14px;
      }
    }
  }

  .error-alert {
    margin: 16px 24px 0;
    border-radius: 8px;
  }

  .popup-actions {
    display: flex;
    justify-content: flex-end;
    gap: 12px;
    padding: 20px 24px;
    background-color: #f8f9fa;
    border-top: 1px solid #e9ecef;

    .v-btn {
      text-transform: none;
      font-weight: 500;
    }
  }
}

// Scrollbar styling
.kpi-selection::-webkit-scrollbar {
  width: 8px;
}

.kpi-selection::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.kpi-selection::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;

  &:hover {
    background: #a8a8a8;
  }
}

// Responsive design
@media (max-width: 768px) {
  .popup {
    padding: 10px;

    .popup-inner {
      max-height: 95vh;
    }

    .popup-header {
      padding: 16px;

      .header-content {
        gap: 12px;

        .header-text h3 {
          font-size: 20px;
        }
      }
    }

    .search-container,
    .recommendation-alert {
      padding: 12px 16px;
    }

    .kpi-selection {
      padding: 0 16px;
    }

    .popup-actions {
      flex-direction: column-reverse;
      padding: 16px;

      .v-btn {
        width: 100%;
      }
    }
  }
}
</style>