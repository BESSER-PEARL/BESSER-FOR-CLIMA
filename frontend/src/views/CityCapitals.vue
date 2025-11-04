<template>
  <div class="city-capitals-view">
    <!-- Header -->
    <v-container fluid class="page-header">
      <v-row align="center">
        <v-col cols="12" md="8">
          <div class="header-content">
            <v-icon size="40" color="primary" class="mr-4">mdi-city</v-icon>
            <div>
              <h1 class="text-h4 font-weight-bold">{{ cityName }} Capitals</h1>
              <p class="text-subtitle-1 text-medium-emphasis mt-1">
                Climate change response indicators and assessment framework
              </p>
            </div>
          </div>
        </v-col>
        <v-col cols="12" md="4" class="text-right">
          <v-btn
            color="primary"
            variant="flat"
            prepend-icon="mdi-download"
            @click="exportToExcel"
          >
            Export to Excel
          </v-btn>
        </v-col>
      </v-row>
    </v-container>

    <!-- Filters and Search -->
    <v-container fluid class="filters-section">
      <v-row>
        <v-col cols="12" md="4">
          <v-text-field
            v-model="searchQuery"
            prepend-inner-icon="mdi-magnify"
            label="Search indicators..."
            variant="outlined"
            density="comfortable"
            hide-details
            clearable
          ></v-text-field>
        </v-col>
        <v-col cols="12" md="2">
          <v-select
            v-model="selectedCapital"
            :items="capitalCategories"
            label="Capital Category"
            variant="outlined"
            density="comfortable"
            hide-details
            clearable
          ></v-select>
        </v-col>
        <v-col cols="12" md="2">
          <v-select
            v-model="selectedThreshold"
            :items="thresholdFilters"
            label="Threshold Status"
            variant="outlined"
            density="comfortable"
            hide-details
            clearable
          ></v-select>
        </v-col>
        <v-col cols="12" md="2">
          <v-select
            v-model="selectedIndicator"
            :items="indicatorFilters"
            label="Indicator Type"
            variant="outlined"
            density="comfortable"
            hide-details
            clearable
          ></v-select>
        </v-col>
        <v-col cols="12" md="2">
          <v-btn
            color="secondary"
            variant="outlined"
            block
            @click="resetFilters"
            prepend-icon="mdi-filter-off"
          >
            Reset Filters
          </v-btn>
        </v-col>
      </v-row>
    </v-container>

    <!-- Tabs for different capital types -->
    <v-container fluid>
      <v-tabs
        v-model="activeTab"
        color="primary"
        align-tabs="start"
        class="capitals-tabs"
      >
        <v-tab value="all">
          <v-icon start>mdi-view-list</v-icon>
          All Capitals
        </v-tab>
        <v-tab value="social">
          <v-icon start>mdi-account-group</v-icon>
          Social
        </v-tab>
        <v-tab value="institutional">
          <v-icon start>mdi-domain</v-icon>
          Institutional
        </v-tab>
        <v-tab value="policy">
          <v-icon start>mdi-gavel</v-icon>
          Policy
        </v-tab>
        <v-tab value="financial">
          <v-icon start>mdi-currency-usd</v-icon>
          Financial
        </v-tab>
        <v-tab value="information">
          <v-icon start>mdi-information</v-icon>
          Information
        </v-tab>
        <v-tab value="thresholds">
          <v-icon start>mdi-alert</v-icon>
          Thresholds
        </v-tab>
      </v-tabs>

      <v-window v-model="activeTab" class="mt-4">
        <v-window-item
          v-for="tab in ['all', 'social', 'institutional', 'policy', 'financial', 'information', 'thresholds']"
          :key="tab"
          :value="tab"
        >
          <!-- Statistics Cards -->
          <v-row class="mb-4">
            <v-col cols="12" sm="6" md="3">
              <v-card class="stat-card" color="primary" variant="tonal">
                <v-card-text>
                  <div class="d-flex align-center">
                    <v-icon size="40" class="mr-3">mdi-check-circle</v-icon>
                    <div>
                      <div class="text-h5 font-weight-bold">{{ stats.validated }}</div>
                      <div class="text-caption">Validated</div>
                    </div>
                  </div>
                </v-card-text>
              </v-card>
            </v-col>
            <v-col cols="12" sm="6" md="3">
              <v-card class="stat-card" color="success" variant="tonal">
                <v-card-text>
                  <div class="d-flex align-center">
                    <v-icon size="40" class="mr-3">mdi-thumb-up</v-icon>
                    <div>
                      <div class="text-h5 font-weight-bold">{{ stats.meetThresholds }}</div>
                      <div class="text-caption">Meet Thresholds</div>
                    </div>
                  </div>
                </v-card-text>
              </v-card>
            </v-col>
            <v-col cols="12" sm="6" md="3">
              <v-card class="stat-card" color="warning" variant="tonal">
                <v-card-text>
                  <div class="d-flex align-center">
                    <v-icon size="40" class="mr-3">mdi-alert</v-icon>
                    <div>
                      <div class="text-h5 font-weight-bold">{{ stats.partialThresholds }}</div>
                      <div class="text-caption">Partial</div>
                    </div>
                  </div>
                </v-card-text>
              </v-card>
            </v-col>
            <v-col cols="12" sm="6" md="3">
              <v-card class="stat-card" color="error" variant="tonal">
                <v-card-text>
                  <div class="d-flex align-center">
                    <v-icon size="40" class="mr-3">mdi-close-circle</v-icon>
                    <div>
                      <div class="text-h5 font-weight-bold">{{ stats.notMeetThresholds }}</div>
                      <div class="text-caption">Not Meet</div>
                    </div>
                  </div>
                </v-card-text>
              </v-card>
            </v-col>
          </v-row>

          <!-- Data Table -->
          <v-card class="table-card">
            <v-data-table
              :headers="headers"
              :items="filteredIndicators"
              :search="searchQuery"
              :items-per-page="15"
              class="capitals-table"
              density="comfortable"
            >
              <!-- Capital Column -->
              <template v-slot:item.capital="{ item }">
                <div class="capital-cell">
                  <v-chip
                    size="small"
                    :color="getCapitalColor(item.capital)"
                    variant="flat"
                  >
                    {{ item.capital }}
                  </v-chip>
                </div>
              </template>

              <!-- Code Column -->
              <template v-slot:item.code="{ item }">
                <span class="font-weight-medium">{{ item.code }}</span>
              </template>

              <!-- Indicators Column -->
              <template v-slot:item.indicators="{ item }">
                <div class="indicator-cell">
                  {{ item.indicators }}
                </div>
              </template>

              <!-- Validated Column -->
              <template v-slot:item.validated="{ item }">
                <v-chip
                  size="small"
                  :color="item.validated === 'Y/N' ? 'primary' : 'default'"
                  variant="flat"
                >
                  {{ item.validated }}
                </v-chip>
              </template>

              <!-- Thresholds Columns -->
              <template v-slot:item.thresholdsA="{ item }">
                <v-chip
                  size="small"
                  :color="getThresholdColor(item.thresholdsA)"
                  variant="flat"
                  class="threshold-chip"
                >
                  {{ item.thresholdsA || '-' }}
                </v-chip>
              </template>

              <template v-slot:item.thresholdsB="{ item }">
                <v-chip
                  size="small"
                  :color="getThresholdColor(item.thresholdsB)"
                  variant="flat"
                  class="threshold-chip"
                >
                  {{ item.thresholdsB || '-' }}
              </v-chip>
              </template>

              <template v-slot:item.thresholdsC="{ item }">
                <v-chip
                  size="small"
                  :color="getThresholdColor(item.thresholdsC)"
                  variant="flat"
                  class="threshold-chip"
                >
                  {{ item.thresholdsC || '-' }}
                </v-chip>
              </template>

              <!-- Actions -->
              <template v-slot:item.actions="{ item }">
                <v-btn
                  icon="mdi-eye"
                  size="small"
                  variant="text"
                  @click="viewDetails(item)"
                ></v-btn>
                <v-btn
                  icon="mdi-pencil"
                  size="small"
                  variant="text"
                  @click="editIndicator(item)"
                ></v-btn>
              </template>
            </v-data-table>
          </v-card>
        </v-window-item>
      </v-window>
    </v-container>

    <!-- Details Dialog -->
    <v-dialog v-model="detailsDialog" max-width="800">
      <v-card v-if="selectedIndicator">
        <v-card-title class="d-flex align-center bg-primary">
          <v-icon class="mr-2">mdi-information</v-icon>
          Indicator Details
          <v-spacer></v-spacer>
          <v-btn icon="mdi-close" variant="text" @click="detailsDialog = false"></v-btn>
        </v-card-title>
        
        <v-card-text class="pt-6">
          <v-row>
            <v-col cols="12" md="6">
              <div class="detail-field">
                <span class="text-caption text-medium-emphasis">Code</span>
                <div class="text-h6">{{ selectedIndicatorDetails.code }}</div>
              </div>
            </v-col>
            <v-col cols="12" md="6">
              <div class="detail-field">
                <span class="text-caption text-medium-emphasis">Capital</span>
                <v-chip :color="getCapitalColor(selectedIndicatorDetails.capital)">
                  {{ selectedIndicatorDetails.capital }}
                </v-chip>
              </div>
            </v-col>
            <v-col cols="12">
              <div class="detail-field">
                <span class="text-caption text-medium-emphasis">Indicator Description</span>
                <div class="text-body-1">{{ selectedIndicatorDetails.indicators }}</div>
              </div>
            </v-col>
            <v-col cols="12" md="4">
              <div class="detail-field">
                <span class="text-caption text-medium-emphasis">Validated</span>
                <v-chip :color="selectedIndicatorDetails.validated === 'Y/N' ? 'primary' : 'default'">
                  {{ selectedIndicatorDetails.validated }}
                </v-chip>
              </div>
            </v-col>
            <v-col cols="12" md="4">
              <div class="detail-field">
                <span class="text-caption text-medium-emphasis">Threshold A</span>
                <v-chip :color="getThresholdColor(selectedIndicatorDetails.thresholdsA)">
                  {{ selectedIndicatorDetails.thresholdsA || 'N/A' }}
                </v-chip>
              </div>
            </v-col>
            <v-col cols="12" md="4">
              <div class="detail-field">
                <span class="text-caption text-medium-emphasis">Threshold B</span>
                <v-chip :color="getThresholdColor(selectedIndicatorDetails.thresholdsB)">
                  {{ selectedIndicatorDetails.thresholdsB || 'N/A' }}
                </v-chip>
              </div>
            </v-col>
          </v-row>
        </v-card-text>
        
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="primary" variant="flat" @click="detailsDialog = false">Close</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useRoute } from 'vue-router';

const route = useRoute();

// Get city name from route or default
const cityName = computed(() => {
  const city = route.params.city || 'Athens';
  return city.charAt(0).toUpperCase() + city.slice(1);
});

// Active tab
const activeTab = ref('all');

// Search and filters
const searchQuery = ref('');
const selectedCapital = ref(null);
const selectedThreshold = ref(null);
const selectedIndicator = ref(null);

// Dialog
const detailsDialog = ref(false);
const selectedIndicatorDetails = ref(null);

// Filter options
const capitalCategories = ['C1.1 Participation', 'C1.2 Communication and knowledge', 'C1.3 Public and norms of society'];
const thresholdFilters = ['Y (Meets all)', 'Y/N (Partially meets)', 'N (Does not meet)', 'Not applicable'];
const indicatorFilters = ['Y/N', 'Y/N/Frequency', 'Frequency'];

// Table headers
const headers = [
  { title: 'Capital', key: 'capital', width: '150px' },
  { title: 'Code', key: 'code', width: '100px' },
  { title: 'Indicators Related to Factors', key: 'indicators', width: '40%' },
  { title: 'Validated', key: 'validated', align: 'center', width: '100px' },
  { title: 'A', key: 'thresholdsA', align: 'center', width: '80px' },
  { title: 'B', key: 'thresholdsB', align: 'center', width: '80px' },
  { title: 'C', key: 'thresholdsC', align: 'center', width: '80px' },
  { title: 'Actions', key: 'actions', align: 'center', sortable: false, width: '120px' },
];

// Sample data (matching the Excel structure)
const indicators = ref([
  {
    capital: 'C1.1 Participation',
    code: '1.1.a',
    indicators: 'Presence of a local government climate-related mitigation strategy or plan',
    validated: 'Y/N',
    thresholdsA: 'Y',
    thresholdsB: 'Y',
    thresholdsC: 'N',
  },
  {
    capital: 'C1.1 Participation',
    code: '1.1.b',
    indicators: 'Presence of a local government mitigation strategy that engages citizens in climate change response',
    validated: 'Y/N',
    thresholdsA: 'Y',
    thresholdsB: 'Y',
    thresholdsC: 'N',
  },
  {
    capital: 'C1.1 Participation',
    code: '1.1.c',
    indicators: 'Enrollment of climate-related partnerships with local stakeholders',
    validated: 'Y/N',
    thresholdsA: 'Y',
    thresholdsB: 'Y',
    thresholdsC: 'N',
  },
  {
    capital: 'C1.1 Participation',
    code: '1.1.d',
    indicators: 'Presence of climate-related networks involving the local private sector',
    validated: 'Y/N',
    thresholdsA: 'Y',
    thresholdsB: 'Y',
    thresholdsC: 'N',
  },
  {
    capital: 'C1.1 Participation',
    code: '1.1.e',
    indicators: 'Presence of volunteer citizens programs related to climate transformation agencies',
    validated: 'Y/N',
    thresholdsA: 'Y',
    thresholdsB: 'Y',
    thresholdsC: 'N',
  },
  {
    capital: 'C1.1 Participation',
    code: '1.1.f',
    indicators: 'Civic engagement in climate-related (mitigation) R&D projects which strongly involve and engage citizens and/or the civil society',
    validated: 'Y/N',
    thresholdsA: 'Y',
    thresholdsB: 'Y',
    thresholdsC: 'N',
  },
  {
    capital: 'C1.1 Participation',
    code: '1.1.g',
    indicators: '(Advocacy/Mobilizing/Lobby) events on climate-related (climate-related/impacts) by citizens',
    validated: 'Y/N/Frequency',
    thresholdsA: 'N/Frequently (4 or more)',
    thresholdsB: 'Y (at least 1 every 2 years)',
    thresholdsC: 'N',
  },
  {
    capital: 'C1.1 Participation',
    code: '1.1.h',
    indicators: 'Organization of a local government of deliberative budgeting activities for citizens',
    validated: 'Y/N/Frequency',
    thresholdsA: 'Frequently',
    thresholdsB: 'Monthly',
    thresholdsC: 'N',
  },
  {
    capital: 'C1.1 Participation',
    code: '1.1.i',
    indicators: 'Co-development of climate plans with stakeholders (involving youth, women, elderly etc.) through participatory processes & decision-making',
    validated: 'Y/N',
    thresholdsA: 'Y',
    thresholdsB: 'Y',
    thresholdsC: 'Y',
  },
  {
    capital: 'C1.1 Participation',
    code: '1.1.j',
    indicators: 'Existence of citizen/broad-based demonstrations and stakeholders about climate change though participatory practices',
    validated: 'Y/N/Frequency',
    thresholdsA: 'Y (at Minimum of at least 1 per year)',
    thresholdsB: 'Y (at least 1 per year)',
    thresholdsC: 'N',
  },
  {
    capital: 'C1.1 Participation',
    code: '1.1.l',
    indicators: 'Implementation of citizens participation monitoring incursions (e.g. through an external audit)',
    validated: 'Y/N/Frequency',
    thresholdsA: 'Y (at Minimum of 1 per year)',
    thresholdsB: 'Monthly',
    thresholdsC: 'N',
  },
  {
    capital: 'C1.2 Communication',
    code: '1.2.a',
    indicators: 'Public communications campaigns that target mitigation and progress towards climate neutrality (public action or report on the institutional website or others)',
    validated: 'Y/N/Frequency',
    thresholdsA: 'Y (at Minimum of 1 per year)',
    thresholdsB: 'Monthly',
    thresholdsC: 'N',
  },
  {
    capital: 'C1.2 Communication',
    code: '1.2.b',
    indicators: 'Public information campaigns on climate change',
    validated: 'Frequency',
    thresholdsA: 'Y (at year minimum)',
    thresholdsB: 'Monthly',
    thresholdsC: 'N',
  },
  {
    capital: 'C1.2 Communication',
    code: '1.2.c',
    indicators: 'Organization of public hearings on climate-related mitigation',
    validated: 'Y/N/Frequency',
    thresholdsA: 'Y',
    thresholdsB: 'Monthly',
    thresholdsC: 'N',
  },
  {
    capital: 'C1.2 Communication',
    code: '1.2.d',
    indicators: 'Organization of educational activities (capacity-building, courses, trainings, etc.) for citizens (including youth women & men, children, teenagers, etc.) for climate-related capacity building courses, trainings, etc.) for young generations',
    validated: 'Y/N',
    thresholdsA: 'Y',
    thresholdsB: 'Y',
    thresholdsC: 'N',
  },
  {
    capital: 'C1.2 Communication',
    code: '1.2.e',
    indicators: 'Existence of formal broadcasting (used resulting from (Data collection/climate development)',
    validated: 'Y/N',
    thresholdsA: 'Y',
    thresholdsB: 'Y',
    thresholdsC: 'Y',
  },
  {
    capital: 'C1.3 Public norms',
    code: '1.3.a',
    indicators: 'Existence of informed broadcasting (events resulting from (Data-climate) development',
    validated: 'Y/N',
    thresholdsA: 'Y',
    thresholdsB: 'Y',
    thresholdsC: 'N',
  },
  {
    capital: 'C1.3 Public norms',
    code: '1.3.b',
    indicators: 'Incentives for local government to must climate-required social social behavior',
    validated: 'Y/N',
    thresholdsA: 'Y',
    thresholdsB: 'Y',
    thresholdsC: 'N',
  },
  {
    capital: 'C1.3 Public norms',
    code: '1.3.c',
    indicators: 'Existence of volunteer organizations/brigade in generate in case of weather extremes and climate-related emergencies',
    validated: 'Y/N',
    thresholdsA: 'Y',
    thresholdsB: 'Y',
    thresholdsC: 'N',
  },
]);

// Statistics
const stats = computed(() => {
  const filtered = filteredIndicators.value;
  return {
    validated: filtered.filter(i => i.validated === 'Y/N').length,
    meetThresholds: filtered.filter(i => i.thresholdsA === 'Y' || i.thresholdsB === 'Y').length,
    partialThresholds: filtered.filter(i => 
      (i.thresholdsA && i.thresholdsA.includes('Y/N')) || 
      (i.thresholdsB && i.thresholdsB.includes('Y/N'))
    ).length,
    notMeetThresholds: filtered.filter(i => 
      i.thresholdsA === 'N' || i.thresholdsB === 'N' || i.thresholdsC === 'N'
    ).length,
  };
});

// Filtered indicators
const filteredIndicators = computed(() => {
  let filtered = indicators.value;

  // Filter by active tab
  if (activeTab.value !== 'all') {
    const tabMapping = {
      'social': 'C1.1',
      'institutional': 'C1.2',
      'policy': 'C1.3',
    };
    const prefix = tabMapping[activeTab.value];
    if (prefix) {
      filtered = filtered.filter(i => i.capital.startsWith(prefix));
    }
  }

  // Filter by capital category
  if (selectedCapital.value) {
    filtered = filtered.filter(i => i.capital === selectedCapital.value);
  }

  // Filter by threshold status
  if (selectedThreshold.value) {
    filtered = filtered.filter(i => {
      if (selectedThreshold.value === 'Y (Meets all)') {
        return i.thresholdsA === 'Y' || i.thresholdsB === 'Y';
      } else if (selectedThreshold.value === 'Y/N (Partially meets)') {
        return i.thresholdsA?.includes('Y/N') || i.thresholdsB?.includes('Y/N');
      } else if (selectedThreshold.value === 'N (Does not meet)') {
        return i.thresholdsA === 'N' || i.thresholdsB === 'N' || i.thresholdsC === 'N';
      }
      return true;
    });
  }

  // Filter by indicator type
  if (selectedIndicator.value) {
    filtered = filtered.filter(i => i.validated === selectedIndicator.value);
  }

  return filtered;
});

// Helper functions
const getCapitalColor = (capital) => {
  if (capital.includes('C1.1')) return 'blue';
  if (capital.includes('C1.2')) return 'purple';
  if (capital.includes('C1.3')) return 'teal';
  return 'grey';
};

const getThresholdColor = (threshold) => {
  if (!threshold || threshold === '-') return 'grey-lighten-2';
  if (threshold === 'Y' || threshold.toLowerCase().includes('yes')) return 'success';
  if (threshold === 'N' || threshold.toLowerCase().includes('no')) return 'error';
  if (threshold.includes('Y/N') || threshold.toLowerCase().includes('partial')) return 'warning';
  if (threshold.toLowerCase().includes('frequently') || threshold.toLowerCase().includes('monthly')) return 'info';
  return 'grey';
};

const resetFilters = () => {
  searchQuery.value = '';
  selectedCapital.value = null;
  selectedThreshold.value = null;
  selectedIndicator.value = null;
};

const viewDetails = (item) => {
  selectedIndicatorDetails.value = item;
  detailsDialog.value = true;
};

const editIndicator = (item) => {
  // TODO: Implement edit functionality
  console.log('Edit indicator:', item);
};

const exportToExcel = () => {
  // TODO: Implement Excel export
  console.log('Export to Excel');
};
</script>

<style lang="scss" scoped>
.city-capitals-view {
  min-height: 100vh;
  background: #f5f7fa;
}

.page-header {
  background: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  padding: 24px 0;
  margin-bottom: 24px;

  .header-content {
    display: flex;
    align-items: center;
  }
}

.filters-section {
  margin-bottom: 24px;
}

.capitals-tabs {
  background: white;
  border-radius: 8px 8px 0 0;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.stat-card {
  height: 100%;
  
  .v-card-text {
    padding: 16px !important;
  }
}

.table-card {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  border-radius: 0 0 8px 8px;
}

.capitals-table {
  :deep(.v-data-table-header) {
    background: #f8f9fa;
    
    th {
      font-weight: 600 !important;
      color: #2c3e50 !important;
    }
  }

  :deep(.v-data-table__td) {
    padding: 12px 16px !important;
  }
}

.capital-cell {
  .v-chip {
    font-size: 0.75rem;
    font-weight: 600;
  }
}

.indicator-cell {
  line-height: 1.5;
  font-size: 0.9rem;
}

.threshold-chip {
  min-width: 50px;
  justify-content: center;
}

.detail-field {
  margin-bottom: 20px;

  .text-caption {
    display: block;
    margin-bottom: 8px;
    text-transform: uppercase;
    font-weight: 600;
  }
}

// Mobile responsive
@media (max-width: 960px) {
  .page-header {
    .header-content {
      flex-direction: column;
      align-items: flex-start;

      .v-icon {
        margin-bottom: 12px;
      }
    }
  }

  .capitals-tabs {
    :deep(.v-tab) {
      min-width: auto;
      padding: 0 12px;
      font-size: 0.85rem;
    }
  }
}
</style>
