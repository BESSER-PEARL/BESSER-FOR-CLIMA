<template>
  <v-dialog v-model="show" max-width="600px">
    <v-card>
      <v-card-title class="dialog-header">
        <div class="header-content">
          <Icon icon="material-symbols:info" class="info-icon" />
          <span>KPI Information</span>
        </div>
        <v-btn
          icon
          variant="text"
          @click="show = false"
        >
          <Icon icon="material-symbols:close" />
        </v-btn>
      </v-card-title>

      <v-card-text v-if="kpiData" class="kpi-details">
        <div class="detail-row">
          <div class="label">Name:</div>
          <div class="value">{{ kpiData.name }}</div>
        </div>

        <div class="detail-row" v-if="kpiData.id_kpi">
          <div class="label">KPI ID:</div>
          <div class="value code">{{ kpiData.id_kpi }}</div>
        </div>

        <div class="detail-row" v-if="kpiData.description">
          <div class="label">Description:</div>
          <div class="value">{{ kpiData.description }}</div>
        </div>

        <div class="detail-row">
          <div class="label">Category:</div>
          <div class="value">
            <v-chip size="small" color="primary">{{ kpiData.category }}</v-chip>
          </div>
        </div>

        <div class="detail-row">
          <div class="label">Unit:</div>
          <div class="value">{{ kpiData.unit_text }}</div>
        </div>

        <div class="detail-row" v-if="kpiData.provider">
          <div class="label">Provider:</div>
          <div class="value">{{ kpiData.provider }}</div>
        </div>

        <div class="detail-row" v-if="kpiData.calculation_frequency">
          <div class="label">Frequency:</div>
          <div class="value">{{ kpiData.calculation_frequency }}</div>
        </div>

        <div class="thresholds-section" v-if="kpiData.min_threshold !== null || kpiData.max_threshold !== null">
          <div class="section-title">
            <Icon icon="material-symbols:trending-flat" />
            Thresholds
          </div>
          
          <div class="thresholds-grid">
            <div class="threshold-card" v-if="kpiData.min_threshold !== null">
              <div class="threshold-label">Minimum</div>
              <div class="threshold-value min">{{ kpiData.min_threshold }} {{ kpiData.unit_text }}</div>
            </div>
            
            <div class="threshold-card" v-if="kpiData.max_threshold !== null">
              <div class="threshold-label">Maximum</div>
              <div class="threshold-value max">{{ kpiData.max_threshold }} {{ kpiData.unit_text }}</div>
            </div>
          </div>
        </div>

        <div class="categories-section" v-if="kpiData.has_category_label && kpiData.category_label_dictionary">
          <div class="section-title">
            <Icon icon="material-symbols:label" />
            Category Labels
          </div>
          
          <div class="categories-grid">
            <v-chip
              v-for="(label, key) in kpiData.category_label_dictionary"
              :key="key"
              size="small"
              variant="outlined"
              class="category-chip"
            >
              {{ label }}
            </v-chip>
          </div>
        </div>

        <div class="meta-section">
          <div class="meta-item">
            <Icon icon="material-symbols:check-circle" :class="{ active: kpiData.is_active }" />
            <span>{{ kpiData.is_active ? 'Active' : 'Inactive' }}</span>
          </div>
          <div class="meta-item">
            <Icon icon="material-symbols:sync" :class="{ active: kpiData.is_processed }" />
            <span>{{ kpiData.is_processed ? 'Processed' : 'Not Processed' }}</span>
          </div>
        </div>
      </v-card-text>

      <v-card-text v-else-if="loading" class="loading-state">
        <v-progress-circular indeterminate color="primary" />
        <span>Loading KPI information...</span>
      </v-card-text>

      <v-card-text v-else class="error-state">
        <Icon icon="material-symbols:error" class="error-icon" />
        <span>{{ error || 'Failed to load KPI information' }}</span>
      </v-card-text>

      <v-card-actions>
        <v-spacer />
        <v-btn
          color="primary"
          variant="text"
          @click="show = false"
        >
          Close
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { ref, watch } from 'vue';
import { Icon } from '@iconify/vue';
import apiService from '@/services/apiService';

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  kpiId: {
    type: Number,
    required: false,
    default: null
  }
});

const emit = defineEmits(['update:modelValue']);

const show = ref(props.modelValue);
const kpiData = ref(null);
const loading = ref(false);
const error = ref(null);

// Watch for dialog open/close
watch(() => props.modelValue, (newVal) => {
  show.value = newVal;
  if (newVal && props.kpiId) {
    loadKPIData();
  }
});

watch(show, (newVal) => {
  emit('update:modelValue', newVal);
  if (!newVal) {
    // Clear data when closing
    kpiData.value = null;
    error.value = null;
  }
});

const loadKPIData = async () => {
  if (!props.kpiId) {
    error.value = 'No KPI ID provided';
    return;
  }

  loading.value = true;
  error.value = null;
  
  try {
    kpiData.value = await apiService.getKPIById(props.kpiId);
  } catch (err) {
    console.error('Error loading KPI data:', err);
    error.value = err.message || 'Failed to load KPI information';
  } finally {
    loading.value = false;
  }
};
</script>

<style lang="scss" scoped>
.dialog-header {
  background: linear-gradient(135deg, #0177a9 0%, #086494 100%);
  color: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  
  .header-content {
    display: flex;
    align-items: center;
    gap: 12px;
    font-size: 20px;
    font-weight: 600;
    
    .info-icon {
      font-size: 28px;
    }
  }
}

.kpi-details {
  padding: 24px;
  
  .detail-row {
    display: grid;
    grid-template-columns: 140px 1fr;
    gap: 16px;
    padding: 12px 0;
    border-bottom: 1px solid #f0f0f0;
    
    &:last-child {
      border-bottom: none;
    }
    
    .label {
      font-weight: 600;
      color: #666;
      font-size: 14px;
    }
    
    .value {
      color: #333;
      font-size: 14px;
      
      &.code {
        font-family: monospace;
        background: #f5f5f5;
        padding: 4px 8px;
        border-radius: 4px;
        display: inline-block;
      }
    }
  }
  
  .thresholds-section,
  .categories-section {
    margin-top: 24px;
    padding-top: 24px;
    border-top: 2px solid #f0f0f0;
    
    .section-title {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 16px;
      font-weight: 600;
      color: #0177a9;
      margin-bottom: 16px;
    }
  }
  
  .thresholds-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 16px;
    
    .threshold-card {
      background: #f8f9fa;
      border-radius: 8px;
      padding: 16px;
      border-left: 4px solid;
      
      &:has(.min) {
        border-left-color: #4ECDC4;
      }
      
      &:has(.max) {
        border-left-color: #FF6B6B;
      }
      
      .threshold-label {
        font-size: 12px;
        color: #666;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 8px;
      }
      
      .threshold-value {
        font-size: 20px;
        font-weight: 700;
        
        &.min {
          color: #4ECDC4;
        }
        
        &.max {
          color: #FF6B6B;
        }
      }
    }
  }
  
  .categories-grid {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    
    .category-chip {
      font-weight: 500;
    }
  }
  
  .meta-section {
    margin-top: 24px;
    padding-top: 16px;
    border-top: 1px solid #f0f0f0;
    display: flex;
    gap: 24px;
    
    .meta-item {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 14px;
      color: #666;
      
      svg {
        font-size: 20px;
        color: #ccc;
        
        &.active {
          color: #4caf50;
        }
      }
    }
  }
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px;
  gap: 16px;
  color: #666;
}

.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px;
  gap: 12px;
  color: #f44336;
  
  .error-icon {
    font-size: 48px;
  }
}
</style>
