<script setup>
import { ref, reactive, computed, onMounted } from 'vue';
import { useAuth } from '../composables/useAuth';
import AuthRequired from '../components/AuthRequired.vue';
import apiService from '../services/apiService';

// Use the authentication composable
const auth = useAuth();

// Check if user is admin
const isAdmin = computed(() => {
  if (!auth.isAuthenticated.value) return false;
  
  const hasAdminRole = auth.hasRole('admin') || 
                      auth.hasRole('realm-admin') || 
                      auth.hasRole('climaborough-admin');
  
  const userInfo = auth.userInfo.value;
  const hasAdminGroup = userInfo?.group_membership?.some(group => 
    group.includes('admin') || group.includes('Admin')
  );
  
  return hasAdminRole || hasAdminGroup;
});

// Available cities
const cities = [
  'Ioannina', 'Maribor', 'Grenoble-Alpes', 'Athens', 'Differdange', 
  'Torino', 'Cascais', 'Sofia'
];

// State
const selectedCity = ref('');
const kpis = ref([]);
const loading = ref(false);
const error = ref('');
const deleteLoading = ref(false);
const selectedTab = ref(0);

// KPI Values Dialog State
const showKpiValuesDialog = ref(false);
const selectedKpi = ref(null);
const kpiValues = ref([]);
const loadingKpiValues = ref(false);
const kpiValuesError = ref('');

// KPI data grouped by category
const kpisByCategory = computed(() => {
  const grouped = {};
  kpis.value.forEach(kpi => {
    // Handle KPIs without categories or with null/undefined categories
    const category = kpi.category || 'Uncategorized';
    if (!grouped[category]) {
      grouped[category] = [];
    }
    grouped[category].push(kpi);
  });
  return grouped;
});

// Tab headers based on categories
const tabHeaders = computed(() => {
  return Object.keys(kpisByCategory.value).map(category => ({
    title: category,
    value: category
  }));
});

// Get KPIs for selected city
const fetchKPIs = async () => {
  if (!selectedCity.value) return;
  
  loading.value = true;
  error.value = '';
  
  try {
    // Step 1: Get city by code to retrieve city ID
    const cityCode = selectedCity.value.toLowerCase().replace(/\s+/g, '-');
    const city = await apiService.getCityByCode(cityCode);
    
    if (!city) {
      throw new Error(`Failed to fetch city: ${selectedCity.value}`);
    }
    
    console.log(`Found city:`, city);
    
    // Step 2: Get KPIs using city ID
    const data = await apiService.getKPIs(city.id);
    
    console.log(`Fetched ${data.length} KPIs for ${selectedCity.value}:`, data);
    
    // Store KPIs with snake_case properties from backend
    kpis.value = data;
    
    console.log('KPIs grouped by category:', kpisByCategory.value);
    
  } catch (err) {
    error.value = err.message;
    console.error('Error fetching KPIs:', err);
  } finally {
    loading.value = false;
  }
};

// Fetch KPI values for a specific KPI
const fetchKpiValues = async (kpi) => {
  if (!selectedCity.value || !kpi.id) return;
  
  loadingKpiValues.value = true;
  kpiValuesError.value = '';
  selectedKpi.value = kpi;
  
  try {
    // Use the API service - kpi.id is the database ID
    const data = await apiService.getKPIValues(kpi.id);
    
    kpiValues.value = data.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp)); // Sort by timestamp descending
    console.log('Fetched KPI values:', data.slice(0, 5)); // Log first 5 for debugging
    showKpiValuesDialog.value = true;
    
  } catch (err) {
    kpiValuesError.value = err.message;
    console.error('Error fetching KPI values:', err);
  } finally {
    loadingKpiValues.value = false;
  }
};

// Close KPI values dialog
const closeKpiValuesDialog = () => {
  showKpiValuesDialog.value = false;
  selectedKpi.value = null;
  kpiValues.value = [];
  kpiValuesError.value = '';
};

// Delete KPI
const deleteKPI = async (kpiId) => {
  if (!confirm('Are you sure you want to delete this KPI? This action cannot be undone.')) {
    return;
  }
  
  deleteLoading.value = true;
  
  try {
    // Use the API service - it will automatically include the token
    await apiService.deleteKPI(kpiId);
    
    // Refresh KPIs list
    await fetchKPIs();
    
    // Show success message
    alert('KPI deleted successfully');
    
  } catch (err) {
    error.value = err.message;
    console.error('Error deleting KPI:', err);
    alert('Failed to delete KPI: ' + err.message);
  } finally {
    deleteLoading.value = false;
  }
};

// Format threshold values
const formatThreshold = (value) => {
  if (value === null || value === undefined) return 'N/A';
  return value.toString();
};

// Get status color based on KPI value vs thresholds
const getStatusColor = (kpi) => {
  // Since we don't have latest values from the basic endpoint, show neutral color
  return 'grey';
};

// Get value status based on thresholds
const getValueStatus = (value) => {
  if (!selectedKpi.value || selectedKpi.value.min_threshold === null || selectedKpi.value.max_threshold === null) {
    return 'Normal';
  }
  
  const numValue = parseFloat(value);
  const min = parseFloat(selectedKpi.value.min_threshold);
  const max = parseFloat(selectedKpi.value.max_threshold);
  
  if (numValue < min) return 'Below Min';
  if (numValue > max) return 'Above Max';
  return 'Normal';
};

// Get value status color
const getValueStatusColor = (value) => {
  if (!selectedKpi.value || selectedKpi.value.min_threshold === null || selectedKpi.value.max_threshold === null) {
    return 'grey';
  }
  
  const numValue = parseFloat(value);
  const min = parseFloat(selectedKpi.value.min_threshold);
  const max = parseFloat(selectedKpi.value.max_threshold);
  
  if (numValue < min || numValue > max) return 'error';
  return 'success';
};

// Watch for city selection changes
const onCityChange = () => {
  if (selectedCity.value) {
    fetchKPIs();
  }
};

onMounted(() => {
  // Debug admin access
  //console.log('AdminKPIView - Debug Info:');
  //console.log('isAuthenticated:', auth.isAuthenticated.value);
  //console.log('userInfo:', auth.userInfo.value);
  //console.log('hasRole(admin):', auth.hasRole('admin'));
  //console.log('hasRole(realm-admin):', auth.hasRole('realm-admin'));
  //console.log('hasRole(climaborough-admin):', auth.hasRole('climaborough-admin'));
  //console.log('group_membership:', auth.userInfo.value?.group_membership);
  //console.log('isAdmin computed:', isAdmin.value);
  
  // Check if user is admin, if not redirect
  if (!isAdmin.value) {
    error.value = 'Access denied. Admin privileges required.';
  }
});
</script>

<template>
  <AuthRequired>
    <div class="admin-kpi-view">
      <div class="header">
        <h1>KPI Administration</h1>
        <p class="subtitle">Manage Key Performance Indicators across all cities</p>
      </div>

      <!-- Access denied message for non-admin users -->
      <div v-if="!isAdmin" class="access-denied">
        <v-alert type="error" variant="tonal" class="mb-4">
          <v-alert-title>Access Denied</v-alert-title>
          You need administrator privileges to access this page.
        </v-alert>
      </div>

      <!-- Admin interface -->
      <template v-else>
        <!-- City Selection -->
        <div class="city-selector">
          <v-select
            v-model="selectedCity"
            :items="cities"
            label="Select City"
            variant="outlined"
            class="city-select"
            @update:model-value="onCityChange"
          ></v-select>
        </div>

        <!-- Error Alert -->
        <v-alert v-if="error" type="error" variant="tonal" class="mb-4" dismissible @click:close="error = ''">
          {{ error }}
        </v-alert>

        <!-- Loading State -->
        <div v-if="loading" class="loading-container">
          <v-progress-circular indeterminate color="primary" size="64"></v-progress-circular>
          <p>Loading KPIs...</p>
        </div>

        <!-- KPI Data Display -->
        <div v-else-if="selectedCity && kpis.length > 0" class="kpi-content">
          <div class="kpi-summary">
            <h2>{{ selectedCity }} - {{ kpis.length }} KPIs Total</h2>
            <div class="category-summary">
              <v-chip 
                v-for="(categoryKpis, category) in kpisByCategory" 
                :key="category"
                class="ma-1"
                color="primary"
                variant="outlined"
              >
                {{ category }}: {{ categoryKpis.length }}
              </v-chip>
            </div>
          </div>

          <!-- Tabs by Category -->
          <v-tabs v-model="selectedTab" class="category-tabs">
            <v-tab v-for="(category, index) in Object.keys(kpisByCategory)" :key="category" :value="index">
              {{ category }} ({{ kpisByCategory[category].length }})
            </v-tab>
          </v-tabs>

          <!-- Tab Windows -->
          <v-window v-model="selectedTab" class="tab-content">
            <v-window-item v-for="(category, index) in Object.keys(kpisByCategory)" :key="category" :value="index">
              <div class="category-section">
                <h3 class="category-title">{{ category }} KPIs</h3>
                
                <!-- KPI Cards -->
                <div class="kpi-grid">
                  <v-card
                    v-for="kpi in kpisByCategory[category]"
                    :key="kpi.id_kpi"
                    class="kpi-card"
                    elevation="2"
                  >
                    <v-card-title>
                      <div class="kpi-header">
                        <div class="kpi-title-section">
                          <h4 class="kpi-name">{{ kpi.name }}</h4>
                          <v-chip 
                            color="grey"
                            size="small"
                            variant="flat"
                            class="status-chip"
                          >
                            {{ kpi.unit_text || 'No Unit' }}
                          </v-chip>
                        </div>
                        <div class="kpi-actions">
                          <v-btn
                            icon="mdi-chart-line"
                            size="small"
                            color="primary"
                            variant="text"
                            @click="fetchKpiValues(kpi)"
                            :loading="loadingKpiValues && selectedKpi?.id === kpi.id"
                            title="View KPI Values"
                          ></v-btn>
                          <v-btn
                            icon="mdi-delete"
                            size="small"
                            color="error"
                            variant="text"
                            :loading="deleteLoading"
                            @click="deleteKPI(kpi.id)"
                            title="Delete KPI"
                          ></v-btn>
                        </div>
                      </div>
                    </v-card-title>

                    <v-card-text>
                      <div class="kpi-details">
                        <div class="detail-row">
                          <span class="label">ID:</span>
                          <span class="value">{{ kpi.id_kpi }}</span>
                        </div>
                        
                        <div class="detail-row">
                          <span class="label">Description:</span>
                          <span class="value">{{ kpi.description || 'No description' }}</span>
                        </div>
                        
                        <div class="detail-row">
                          <span class="label">Provider:</span>
                          <span class="value">{{ kpi.provider || 'N/A' }}</span>
                        </div>
                        
                        <div class="detail-row">
                          <span class="label">Frequency:</span>
                          <span class="value">{{ kpi.calculation_frequency || 'N/A' }}</span>
                        </div>
                        
                        <div class="detail-row">
                          <span class="label">Unit:</span>
                          <span class="value">{{ kpi.unit_text || 'N/A' }}</span>
                        </div>
                        
                        <div class="detail-row">
                          <span class="label">Min Threshold:</span>
                          <span class="value">{{ formatThreshold(kpi.min_threshold) }}</span>
                        </div>
                        
                        <div class="detail-row">
                          <span class="label">Max Threshold:</span>
                          <span class="value">{{ formatThreshold(kpi.max_threshold) }}</span>
                        </div>
                        
                        <div class="detail-row">
                          <span class="label">Has Category Label:</span>
                          <span class="value">{{ kpi.has_category_label ? 'Yes' : 'No' }}</span>
                        </div>
                        
                        <div class="detail-row" v-if="kpi.has_category_label && kpi.category_label_dictionary">
                          <span class="label">Category Labels:</span>
                          <span class="value">
                            <div v-if="typeof kpi.category_label_dictionary === 'object'" class="category-labels">
                              <v-chip 
                                v-for="(label, key) in kpi.category_label_dictionary" 
                                :key="key" 
                                size="x-small" 
                                class="ma-1"
                                variant="outlined"
                              >
                                {{ key }}: {{ label }}
                              </v-chip>
                            </div>
                            <span v-else>{{ kpi.category_label_dictionary }}</span>
                          </span>
                        </div>
                      </div>
                    </v-card-text>
                  </v-card>
                </div>
              </div>
            </v-window-item>
          </v-window>
        </div>

        <!-- No KPIs State -->
        <div v-else-if="selectedCity && kpis.length === 0 && !loading" class="no-data">
          <v-icon size="64" color="grey">mdi-database-off</v-icon>
          <h3>No KPIs Found</h3>
          <p>No KPIs are available for {{ selectedCity }}.</p>
        </div>

        <!-- No City Selected State -->
        <div v-else-if="!selectedCity" class="no-selection">
          <v-icon size="64" color="grey">mdi-city</v-icon>
          <h3>Select a City</h3>
          <p>Choose a city from the dropdown to view and manage its KPIs.</p>
        </div>
      </template>
    </div>

    <!-- KPI Values Dialog -->
    <v-dialog v-model="showKpiValuesDialog" max-width="800px" scrollable>
      <v-card>
        <v-card-title class="text-h5">
          <div class="dialog-title">
            <v-icon left>mdi-chart-line</v-icon>
            KPI Values: {{ selectedKpi?.name }}
          </div>
        </v-card-title>
        
        <v-card-subtitle v-if="selectedKpi">
          <div class="kpi-info">
            <span><strong>ID:</strong> {{ selectedKpi.id_kpi }}</span>
            <span><strong>Unit:</strong> {{ selectedKpi.unit_text || 'N/A' }}</span>
            <span><strong>Provider:</strong> {{ selectedKpi.provider || 'N/A' }}</span>
          </div>
        </v-card-subtitle>

        <v-divider></v-divider>

        <v-card-text style="height: 400px;">
          <!-- Loading State -->
          <div v-if="loadingKpiValues" class="loading-container">
            <v-progress-circular indeterminate color="primary" size="48"></v-progress-circular>
            <p>Loading KPI values...</p>
          </div>

          <!-- Error State -->
          <v-alert v-else-if="kpiValuesError" type="error" variant="tonal" class="mb-4">
            {{ kpiValuesError }}
          </v-alert>

          <!-- KPI Values List -->
          <div v-else-if="kpiValues.length > 0">
            <div class="values-summary mb-4">
              <v-chip color="primary" variant="outlined">
                {{ kpiValues.length }} values found
              </v-chip>
              <v-chip v-if="kpiValues[0]" color="success" variant="outlined">
                Latest: {{ kpiValues[0].value }} {{ selectedKpi?.unit_text || '' }}
              </v-chip>
            </div>

            <v-list>
              <v-list-item
                v-for="(value, index) in kpiValues"
                :key="index"
                class="value-item"
              >
                <template v-slot:prepend>
                  <v-icon color="primary">mdi-chart-box-outline</v-icon>
                </template>

                <v-list-item-title>
                  <span class="value-number">{{ value.value }}</span>
                  <span class="value-unit">{{ selectedKpi?.unit_text || '' }}</span>
                </v-list-item-title>

                <v-list-item-subtitle>
                  <div class="value-details">
                    <span class="timestamp">
                      <v-icon size="small">mdi-clock-outline</v-icon>
                      {{ new Date(value.timestamp).toLocaleString() }}
                    </span>
                    <span v-if="value.category_label" class="category-label">
                      <v-chip size="x-small" variant="outlined">
                        {{ value.category_label }}
                      </v-chip>
                    </span>
                  </div>
                </v-list-item-subtitle>

                <template v-slot:append>
                  <v-chip 
                    :color="getValueStatusColor(value.value)"
                    size="small"
                    variant="flat"
                  >
                    {{ getValueStatus(value.value) }}
                  </v-chip>
                </template>
              </v-list-item>
            </v-list>
          </div>

          <!-- No Values State -->
          <div v-else class="no-values">
            <v-icon size="64" color="grey">mdi-chart-line-variant</v-icon>
            <h3>No Values Found</h3>
            <p>No values are available for this KPI.</p>
          </div>
        </v-card-text>

        <v-divider></v-divider>

        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="primary" @click="closeKpiValuesDialog">
            Close
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

  </AuthRequired>
</template>

<style lang="scss" scoped>
.admin-kpi-view {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
  min-height: calc(100vh - 140px);
}

.header {
  text-align: center;
  margin-bottom: 30px;
  
  h1 {
    color: #0177a9;
    font-size: 2.5rem;
    margin-bottom: 10px;
  }
  
  .subtitle {
    color: #666;
    font-size: 1.1rem;
  }
}

.access-denied {
  max-width: 600px;
  margin: 50px auto;
  text-align: center;
}

.city-selector {
  max-width: 400px;
  margin: 0 auto 30px auto;
  
  .city-select {
    font-size: 1.1rem;
  }
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 50px;
  
  p {
    margin-top: 20px;
    color: #666;
    font-size: 1.1rem;
  }
}

.kpi-content {
  .kpi-summary {
    text-align: center;
    margin-bottom: 20px;
    
    h2 {
      color: #0177a9;
      font-size: 1.8rem;
      margin-bottom: 10px;
    }
    
    .category-summary {
      margin-top: 15px;
      display: flex;
      justify-content: center;
      flex-wrap: wrap;
      gap: 5px;
    }
  }
}

.category-tabs {
  margin-bottom: 20px;
  
  :deep(.v-tab) {
    font-weight: 500;
  }
}

.tab-content {
  min-height: 400px;
}

.category-section {
  padding: 20px 0;
  
  .category-title {
    color: #0177a9;
    margin-bottom: 20px;
    font-size: 1.5rem;
    border-bottom: 2px solid #0177a9;
    padding-bottom: 10px;
  }
}

.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 20px;
}

.kpi-card {
  border-left: 4px solid #0177a9;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;
  }
}

.kpi-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  
  .kpi-title-section {
    flex-grow: 1;
    
    .kpi-name {
      color: #0177a9;
      font-size: 1.2rem;
      margin-bottom: 8px;
      font-weight: 600;
    }
    
    .status-chip {
      font-weight: 500;
    }
  }
  
  .kpi-actions {
    display: flex;
    gap: 5px;
  }
}

.kpi-details {
  .detail-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 0;
    border-bottom: 1px solid #f0f0f0;
    
    &:last-child {
      border-bottom: none;
    }
    
    .label {
      font-weight: 500;
      color: #666;
      min-width: 120px;
    }
    
    .value {
      text-align: right;
      color: #333;
      font-weight: 400;
      word-break: break-word;
      max-width: 200px;
      
      .category-labels {
        text-align: left;
        max-width: 100%;
        
        .v-chip {
          font-size: 10px;
          height: 20px;
        }
      }
    }
  }
}

.no-data, .no-selection {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 50px;
  text-align: center;
  
  h3 {
    margin: 20px 0 10px 0;
    color: #666;
  }
  
  p {
    color: #999;
    font-size: 1.1rem;
  }
}

// Mobile responsiveness
@media (max-width: 768px) {
  .admin-kpi-view {
    padding: 15px;
  }
  
  .header h1 {
    font-size: 2rem;
  }
  
  .kpi-grid {
    grid-template-columns: 1fr;
  }
  
  .kpi-header {
    flex-direction: column;
    gap: 10px;
    
    .kpi-title-section {
      width: 100%;
    }
  }
  
  .detail-row {
    flex-direction: column;
    align-items: flex-start !important;
    gap: 5px;
    
    .value {
      text-align: left !important;
      max-width: 100%;
    }
  }
}

/* KPI Values Dialog Styles */
.dialog-title {
  display: flex;
  align-items: center;
  gap: 10px;
}

.kpi-info {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
  
  span {
    color: #666;
    font-size: 0.9rem;
  }
}

.values-summary {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.value-item {
  border-bottom: 1px solid #f0f0f0;
  
  &:last-child {
    border-bottom: none;
  }
}

.value-number {
  font-size: 1.2rem;
  font-weight: 600;
  color: #0177a9;
  margin-right: 5px;
}

.value-unit {
  color: #666;
  font-size: 0.9rem;
}

.value-details {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
  
  .timestamp {
    display: flex;
    align-items: center;
    gap: 5px;
    color: #999;
    font-size: 0.8rem;
  }
}

.no-values {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 50px;
  text-align: center;
  
  h3 {
    margin: 20px 0 10px 0;
    color: #666;
  }
  
  p {
    color: #999;
    font-size: 1rem;
  }
}
</style>
