<script setup>
import { ref, reactive, computed, onMounted, onBeforeUnmount, watchEffect, watch } from 'vue';
import { GridLayout, GridItem } from 'grid-layout-plus'
import { useRoute, useRouter } from 'vue-router';
import { useAuth } from '../composables/useAuth';
import AuthRequired from '../components/AuthRequired.vue';

import ElementForm from '../components/ElementForm.vue'
import KPIForm from '../components/KPIForm.vue'
import LineChartForm from '../components/forms/LineChartForm.vue'
import PieChartForm from '../components/forms/PieChartForm.vue'
import BarChartForm from '../components/forms/BarChartForm.vue'
import StatChartForm from '../components/forms/StatChartForm.vue'
import TableForm from '../components/forms/TableForm.vue'

import LineChart from '../components/LineChart.vue'
import PieChart from '../components/PieChart.vue'
import BarChart from '../components/BarChart.vue'
import StatChart from '../components/StatChart.vue'
import Table from '../components/Table.vue'
import MapComponent from '../components/Map.vue'
import MonthFilter from '../components/MonthFilter.vue'
import DashboardChat from '../components/DashboardChat.vue'
import FreeTextField from '../components/FreeTextField.vue'
import Timeline from '../components/Timeline.vue'
import TimelineForm from '../components/TimelineForm.vue'
import { uid } from "uid"

import { throttle } from '@vexip-ui/utils'
import html2canvas from 'html2canvas';
import jsPDF from 'jspdf';

// Import the new API service
import apiService from '../services/apiService';

// Component mapping for dynamic components
const componentMap = {
    'LineChart': LineChart,
    'PieChart': PieChart,
    'BarChart': BarChart,
    'StatChart': StatChart,
    'Table': Table,
    'Map': MapComponent,
    'FreeTextField': FreeTextField,
    'Timeline': Timeline
};

// Utility functions
const showToast = (message, type = 'info') => {
    console.log(`[${type.toUpperCase()}] ${message}`);
    // You can integrate with a toast library here like vue-toastification
};

const getDashboardId = () => dashboardData.value?.id;
const dashboardId = computed(() => dashboardData.value?.id);

// Use the authentication composable
const auth = useAuth();
const route = useRoute();
const router = useRouter();

// Reactive data
const city = ref(route.params.city);
const cityData = ref(null);
const dashboardData = ref(null);
const loading = ref(false);
const error = ref(null);

// Dashboard state
const sections = ref([{ "name": "Section 1", "edit": false, "layout": [] }]);
const selectedSection = reactive({
    "name": sections.value[0]?.["name"] || "Section 1",
    "edit": sections.value[0]?.["edit"] || false,
    "layout": sections.value[0]?.["layout"] || []
});

// Global state for visualizations
const state = reactive({
    visualizations: [],
    filteredVisualizations: []
});

// UI state
const editMode = ref(false);
const isSaving = ref(false);
const popupTriggers = ref({ buttonTrigger: false });

// Form states
const tableForm = ref(false);
const lineChartBool = ref(false);
const pieChartBool = ref(false);
const barChartBool = ref(false);
const statChartBool = ref(false);
const tableBool = ref(false);
const freeTextForm = ref(false);
const showTimelineForm = ref(false);

// Current item for editing
const currentItem = ref({});
const currentSelectedChart = ref("");
const editingTimeline = ref(null);
const currentTimelineKPIs = ref([]);

// Chat and filter states
const chatMode = ref(false);
const globalMonthFilter = ref('');
const tempName = ref("");

// Projects mapping for flags (lowercase keys for consistent matching)
const projects = {
    differdange: "luxembourgball.png",
    cascais: "portugalball.png",
    sofia: "bulgariaball.png",
    maribor: "sloveniaball.png",
    athens: "greeceball.png",
    ioannina: "greeceball.png",
    grenoble: "franceball.png",
    'grenoble-alpes': "franceball.png",
    torino: "italyball.png"
};

// Computed properties for display
const flag = computed(() => {
    // Convert city to lowercase for matching
    return projects[city.value?.toLowerCase()];
});

const cityDisplayName = computed(() => {
    // Capitalize first letter of each word for display
    if (!city.value) return '';
    return city.value
        .split('-')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join('-');
});

// Computed permissions
const canCreateDashboard = computed(() => {
    // Admins can always create/edit dashboards
    if (auth.userType.value === 'admin') return true;
    
    // City users can only edit their own city's dashboard
    if (auth.userType.value === 'cityuser' && auth.userCity.value) {
        // Case-insensitive comparison
        return city.value.toLowerCase() === auth.userCity.value.toLowerCase();
    }
    
    return false;
});



// API Helper Functions - Now using the centralized API service
const setupApiService = async () => {
    try {
        const token = await auth.getAccessToken();
        if (token) {
            apiService.setAuthToken(token);
        }
    } catch (error) {
        console.warn('Could not set API token:', error);
    }
};

// City Management - Using API service
const loadCityData = async () => {
    try {
        await setupApiService();
        cityData.value = await apiService.getCityByCode(city.value);
        return cityData.value;
    } catch (error) {
        console.error('Error loading city data:', error);
        error.value = `Failed to load city data: ${error.message}`;
        throw error;
    }
};

// Dashboard Management - Using API service
const loadDashboard = async () => {
    try {
        loading.value = true;
        error.value = null;

        // Setup API service with auth
        await setupApiService();

        // First, ensure we have city data
        if (!cityData.value) {
            await loadCityData();
        }

        // Get dashboard for this city
        try {
            dashboardData.value = await apiService.getDashboardByCity(city.value);
        } catch (err) {
            if (err.message.includes('404') || err.message.includes('not found')) {
                // Dashboard doesn't exist via city code lookup, try getting all dashboards
                console.log('No dashboard found via city code, checking all dashboards...');
                try {
                    const allDashboards = await apiService.getDashboards(cityData.value.id);
                    if (allDashboards && allDashboards.length > 0) {
                        dashboardData.value = allDashboards[0];
                        console.log('Found existing dashboard:', dashboardData.value.title);
                    } else {
                        // Create a default dashboard if none exists
                        console.log('No dashboards found, creating default dashboard...');
                        await createDefaultDashboard();
                    }
                } catch (listErr) {
                    console.warn('Error fetching dashboards list:', listErr);
                    await createDefaultDashboard();
                }
            } else {
                throw err;
            }
        }

        // Load visualizations
        if (dashboardData.value) {
            await loadVisualizations();
        }

    } catch (error) {
        console.error('Error loading dashboard:', error);
        error.value = `Failed to load dashboard: ${error.message}`;
        
        // Set default state on error
        sections.value = [{ "name": "Section 1", "edit": false, "layout": [] }];
        selectedSection.name = "Section 1";
        selectedSection.edit = false;
        selectedSection.layout = [];
    } finally {
        loading.value = false;
    }
};

const createDefaultDashboard = async () => {
    if (!cityData.value) return;

    try {
        const newDashboardData = {
            code: `${city.value.toLowerCase()}-dashboard`,
            title: `${city.value} Dashboard`,
            description: `Main dashboard for ${city.value}`,
            city_id: cityData.value.id,
            is_public: true
        };

        dashboardData.value = await apiService.createDashboard(newDashboardData);
        console.log('Created new dashboard:', dashboardData.value.title);
    } catch (err) {
        // If dashboard already exists, try to fetch it by city_id
        if (err.message.includes('already exists')) {
            console.log('Dashboard already exists, fetching existing dashboard...');
            const allDashboards = await apiService.getDashboards(cityData.value.id);
            if (allDashboards && allDashboards.length > 0) {
                dashboardData.value = allDashboards[0];
                console.log('Found existing dashboard:', dashboardData.value.title);
            } else {
                throw new Error('Dashboard exists but cannot be retrieved');
            }
        } else {
            throw err;
        }
    }
};

const loadVisualizations = async () => {
    if (!dashboardData.value) return;

    try {
        // Load dashboard with sections from the new backend
        const dashboardWithSections = await apiService.get(`/dashboards/${dashboardData.value.id}/with-visualizations`);
        
        // Load visualizations
        const visualizations = await apiService.getDashboardVisualizations(dashboardData.value.id);
        
        // Process sections and visualizations
        sections.value = [];
        const sectionsMap = new Map();

        // Create sections from backend data
        if (dashboardWithSections.sections && dashboardWithSections.sections.length > 0) {
            for (const section of dashboardWithSections.sections) {
                const processedSection = {
                    id: section.id,
                    name: section.name,
                    edit: false,
                    layout: [],
                    created: section.created_at,
                    description: section.description,
                    order: section.order
                };
                sections.value.push(processedSection);
                sectionsMap.set(section.id, processedSection);
            }
        } else {
            // Create default section if none exist
            const defaultSection = {
                id: null, // Will be created when first used
                name: "Section 1",
                edit: false,
                layout: [],
                created: new Date().toISOString(),
                description: "Default section"
            };
            sections.value.push(defaultSection);
            sectionsMap.set(null, defaultSection);
        }

        // Process visualizations into their respective sections
        if (visualizations && visualizations.length > 0) {
            visualizations.forEach(item => {
                const vis = {
                    x: item.x_position || 0,
                    y: item.y_position || 0,
                    w: item.width || 4,
                    h: item.height || 8,
                    i: `viz-${item.id}`,  // Always use unique ID based on database ID
                    id: item.id,
                    chart: apiService.mapVisualizationType(item.type),
                    attributes: {
                        city: city.value,
                        title: item.title,
                        tableId: item.kpi_id
                    }
                };

                // Add chart-specific attributes
                if (item.type === 'linechart') {
                    vis.attributes.xtitle = item.x_title || 'Date';
                    vis.attributes.ytitle = item.y_title || 'Values';
                    vis.attributes.color = item.color || '#0177a9';
                } else if (item.type === 'statchart') {
                    vis.attributes.suffix = item.unit || '';
                } else if (item.type === 'freetextfield') {
                    vis.attributes.text = item.text || '';
                } else if (item.type === 'timeline') {
                    vis.attributes.description = item.description || '';
                    vis.attributes.events = item.events || [];
                }

                // Find the section for this visualization
                const targetSection = sectionsMap.get(item.section_id) || sections.value[0];
                if (targetSection) {
                    targetSection.layout.push(vis);
                }
            });
        }

        // Sort sections by order
        sections.value.sort((a, b) => (a.order || 0) - (b.order || 0));

        // Set selected section to the first one
        if (sections.value.length > 0) {
            selectedSection.name = sections.value[0].name;
            selectedSection.edit = sections.value[0].edit;
            selectedSection.layout = [...sections.value[0].layout];
        }

    } catch (error) {
        console.error('Error loading visualizations:', error);
        // Fallback to default section
        sections.value = [{ 
            id: null,
            name: "Section 1", 
            edit: false, 
            layout: [],
            created: new Date().toISOString()
        }];
        selectedSection.name = "Section 1";
        selectedSection.edit = false;
        selectedSection.layout = [];
    }
};

// Helper function to map visualization types (moved to apiService but kept for consistency)
const mapVisualizationType = (type) => apiService.mapVisualizationType(type);
const mapChartTypeToApi = (chart) => apiService.mapChartTypeToApi(chart);

// Save Dashboard - Using API service
const saveDashboard = async () => {
    if (isSaving.value || !dashboardData.value) {
        console.log('Save already in progress or no dashboard data...');
        return;
    }

    isSaving.value = true;

    try {
        console.log('Saving dashboard...');

        // Setup API service with latest auth
        await setupApiService();

        // Sync current section with sections array
        for (let i = 0; i < sections.value.length; i++) {
            if (selectedSection.name === sections.value[i].name) {
                sections.value[i].layout = [...selectedSection.layout];
                break;
            }
        }

        // Clear existing visualizations first
        try {
            const existingVisualizations = await apiService.getDashboardVisualizations(dashboardData.value.id);
            if (existingVisualizations && existingVisualizations.length > 0) {
                const visIds = existingVisualizations.map(vis => vis.id);
                // Delete one by one to avoid query parameter issues
                for (const visId of visIds) {
                    try {
                        await apiService.deleteVisualization(visId);
                    } catch (err) {
                        console.warn(`Failed to delete visualization ${visId}:`, err);
                    }
                }
            }
        } catch (error) {
            console.warn('Error clearing existing visualizations:', error);
        }

        // Check if we have any visualizations to save
        let hasVisualizations = false;
        const savePromises = [];

        for (let section of sections.value) {
            if (section.layout && section.layout.length > 0) {
                hasVisualizations = true;

                for (let item of section.layout) {
                    const visData = {
                        type: mapChartTypeToApi(item.chart),
                        title: item.attributes.title,
                        dashboard_id: dashboardData.value.id,
                        section_id: section.id,  // Use section.id instead of section.name
                        width: item.w,
                        height: item.h,
                        x_position: item.x,
                        y_position: item.y,
                        i: item.i,
                        kpi_id: item.attributes.tableId
                    };

                    // Add chart-specific properties
                    if (item.chart === "LineChart") {
                        visData.x_title = item.attributes.xtitle || 'Date';
                        visData.y_title = item.attributes.ytitle || 'Values';
                        visData.color = item.attributes.color || '#0177a9';
                    } else if (item.chart === "StatChart") {
                        visData.unit = item.attributes.suffix || '';
                    } else if (item.chart === "FreeTextField") {
                        visData.text = item.attributes.text || '';
                        // console.log('Saving FreeTextField with text:', item.attributes.text);
                    } else if (item.chart === "Timeline") {
                        visData.description = item.attributes.description || '';
                        visData.events = item.attributes.events || [];
                    }

                    const savePromise = apiService.createVisualization(dashboardData.value.id, visData);
                    savePromises.push(savePromise);
                }
            }
        }

        // Save new visualizations if any
        if (savePromises.length > 0) {
            await Promise.all(savePromises);
            console.log('All visualizations saved successfully');
        }

        // Reload dashboard to get fresh state
        await loadVisualizations();
        console.log('Dashboard saved successfully!');

    } catch (error) {
        console.error('Error saving dashboard:', error);
        error.value = `Failed to save dashboard: ${error.message}`;
        
        // Refresh to maintain consistency
        await loadVisualizations();
    } finally {
        isSaving.value = false;
        editMode.value = false;
    }
};

// KPI Management - Using API service
const loadKPIs = async () => {
    if (!cityData.value) return [];
    
    try {
        await setupApiService();
        return await apiService.getKPIs(cityData.value.id, { limit: 1000 });
    } catch (error) {
        console.error('Error loading KPIs:', error);
        return [];
    }
};

// Edit Mode Management
const toggleEditMode = async () => {
    try {
        if (!editMode.value) {
            // Entering edit mode - reload data
            await loadDashboard();
        }
        editMode.value = !editMode.value;
        console.log('Edit mode toggled to:', editMode.value);
    } catch (error) {
        console.error('Error toggling edit mode:', error);
        error.value = `Failed to toggle edit mode: ${error.message}`;
    }
};

// Form Management
const toggleForm = () => {
    popupTriggers.value.buttonTrigger = !popupTriggers.value.buttonTrigger;
};

const toggleKPIForm = async (chart) => {
    if (chart === "Map") {
        // For Map widgets, create with first available KPI
        try {
            const kpis = await loadKPIs();
            if (kpis && kpis.length > 0) {
                createVisualization(kpis[0].id.toString(), 'Map', 'Map', kpis[0]);
            } else {
                error.value = 'No KPIs available for this city. Please create a KPI first.';
            }
        } catch (error) {
            console.error('Error loading KPIs for map:', error);
            error.value = 'Failed to load city KPIs. Please try again.';
        }
        return;
    }
    if (chart === "FreeTextField") {
        // FreeTextField doesn't need KPI, create it directly
        createVisualization(null, 'Free Text', 'FreeTextField', {});
        return;
    }
    if (chart === "Timeline") {
        // Timeline doesn't need KPI at creation, show form with available KPIs
        const kpis = await loadKPIs();
        currentTimelineKPIs.value = kpis;
        showTimelineForm.value = true;
        editingTimeline.value = null;
        return;
    }
    tableForm.value = !tableForm.value;
    currentSelectedChart.value = chart;
};

// Visualization Management
const createVisualization = (tableId, tableName, chart, kpi = {}) => {
    let x = 0, y = 0;
    if (dragItemStop.value.chart === chart) {
        x = parseInt(dragItemStop.value.x) || 0;
        y = parseInt(dragItemStop.value.y) || 0;
        selectedSection.layout = selectedSection.layout.filter(item => item.i !== dropId);
    }

    const vis = {
        x: x,
        y: y,
        w: chart === "Map" ? 7 : (chart === "FreeTextField" ? 6 : 4),
        h: chart === "Map" ? 13 : (chart === "FreeTextField" ? 4 : 8),
        i: uid(),
        chart: chart,
        attributes: {
            city: city.value,
            tableId: tableId,
            title: tableName
        },
        id: uid(),
        section_id: selectedSection.id,
        dashboard_id: dashboardData.value?.id
    };

    // Add chart-specific attributes
    if (chart === "LineChart") {
        vis.attributes.xtitle = "Date";
        vis.attributes.ytitle = `Values (in ${kpi.unit_text || ''})`;
        vis.attributes.color = "#0177a9";
        vis.attributes.target = kpi.max_threshold || 0;
    } else if (chart === "StatChart") {
        vis.attributes.suffix = kpi.unit_text || '';
        vis.attributes.target = kpi.max_threshold || 0;
    } else if (chart === "FreeTextField") {
        vis.attributes.text = '';
    } else if (chart === "Timeline") {
        vis.attributes.description = '';
        vis.attributes.events = [];
    }

    selectedSection.layout.push(vis);
    if (chart === "FreeTextField") {
        freeTextForm.value = false;
    } else {
        tableForm.value = false;
    }
};

const deleteVisualization = (item) => {
    selectedSection.layout = selectedSection.layout.filter((vis) => vis.id !== item.id);
};

// Visualization Edit Forms
const editVisualization = async (item) => {
    currentItem.value = item;
    
    switch (item.chart) {
        case "LineChart":
            lineChartBool.value = true;
            break;
        case "PieChart":
            pieChartBool.value = true;
            break;
        case "BarChart":
            barChartBool.value = true;
            break;
        case "StatChart":
            statChartBool.value = true;
            break;
        case "Table":
            tableBool.value = true;
            break;
        case "Timeline":
            const kpis = await loadKPIs();
            currentTimelineKPIs.value = kpis;
            editingTimeline.value = item;
            showTimelineForm.value = true;
            break;
    }
};

const updateChart = (object) => {
    const index = selectedSection.layout.findIndex(obj => obj.i === currentItem.value.i);
    if (index !== -1) {
        for (const [key, value] of Object.entries(object)) {
            selectedSection.layout[index].attributes[key] = value;
        }
        
        // Clear current item and close forms
        currentItem.value = {};
        lineChartBool.value = false;
        pieChartBool.value = false;
        barChartBool.value = false;
        statChartBool.value = false;
        tableBool.value = false;
    }
};

// Close all edit forms
const closeAllForms = () => {
    lineChartBool.value = false;
    pieChartBool.value = false;
    barChartBool.value = false;
    statChartBool.value = false;
    tableBool.value = false;
    freeTextForm.value = false;
    showTimelineForm.value = false;
};

// Timeline Management
const saveTimelineData = (timelineData) => {
    if (editingTimeline.value) {
        // Update existing timeline
        const index = selectedSection.layout.findIndex(obj => obj.i === editingTimeline.value.i);
        if (index !== -1) {
            selectedSection.layout[index].attributes.description = timelineData.description;
            selectedSection.layout[index].attributes.events = timelineData.events;
        }
    } else {
        // Create new timeline
        createVisualization(null, 'Project Timeline', 'Timeline', {});
        const newTimeline = selectedSection.layout[selectedSection.layout.length - 1];
        newTimeline.attributes.description = timelineData.description;
        newTimeline.attributes.events = timelineData.events;
    }
    
    showTimelineForm.value = false;
    editingTimeline.value = null;
};

const closeTimelineForm = () => {
    showTimelineForm.value = false;
    editingTimeline.value = null;
};

// Enhanced Section Management
const sectionOperationInProgress = ref(false);
const sectionErrors = ref(new Map());
const confirmDeleteSection = ref({
    show: false,
    section: null
});

// Generate unique section names
const generateUniqueSectionName = (baseName = 'Section') => {
    let counter = 1;
    let newName = `${baseName} ${counter}`;
    
    while (sections.value.some(section => section.name.toLowerCase() === newName.toLowerCase())) {
        counter++;
        newName = `${baseName} ${counter}`;
    }
    
    return newName;
};

// Validate section name
const validateSectionName = (name, currentName = null) => {
    if (!name || name.trim() === '') {
        return 'Section name cannot be empty.';
    }
    
    if (name.trim().length > 50) {
        return 'Section name cannot exceed 50 characters.';
    }
    
    const trimmedName = name.trim();
    const duplicateExists = sections.value.some(section => 
        section.name.toLowerCase() === trimmedName.toLowerCase() && 
        section.name !== currentName
    );
    
    if (duplicateExists) {
        return 'A section with this name already exists.';
    }
    
    return null;
};

// Enhanced add section with better UX
const addSection = async (event, customName = null) => {
    if (sectionOperationInProgress.value || !dashboardData.value) return;
    
    try {
        sectionOperationInProgress.value = true;
        event.stopPropagation();
        
        // Generate unique name or use custom name
        const sectionName = customName || generateUniqueSectionName();
        
        // Validate the name
        const validationError = validateSectionName(sectionName);
        if (validationError) {
            error.value = validationError;
            return;
        }
        
        // Create section via backend
        const sectionData = {
            dashboard_id: dashboardData.value.id,  // Required by backend schema
            name: sectionName,
            description: `Section created on ${new Date().toLocaleDateString()}`,
            order: sections.value.length + 1,
            is_active: true
        };
        
        const newBackendSection = await apiService.createDashboardSection(dashboardData.value.id, sectionData);
        
        const newSection = {
            id: newBackendSection.id,
            name: newBackendSection.name,
            edit: false,
            layout: [],
            created: newBackendSection.created_at,
            description: newBackendSection.description,
            order: newBackendSection.order
        };
        
        sections.value.push(newSection);
        
        // Automatically switch to new section
        await setSection(newSection);
        
        console.log(`Section "${sectionName}" created successfully`);
        
    } catch (err) {
        console.error('Error adding section:', err);
        error.value = `Failed to add section: ${err.message}`;
    } finally {
        sectionOperationInProgress.value = false;
    }
};

// Enhanced section switching with loading state
const setSection = async (section) => {
    if (sectionOperationInProgress.value) return;
    
    try {
        sectionOperationInProgress.value = true;
        
        // Save current section changes before switching
        await saveCurrentSectionState();
        
        // Clear any section-specific errors
        sectionErrors.value.clear();
        
        // Switch to new section
        selectedSection.name = section.name;
        selectedSection.edit = section.edit;
        selectedSection.layout = [...section.layout];
        
        console.log(`Switched to section: ${section.name}`);
        
    } catch (err) {
        console.error('Error switching section:', err);
        error.value = `Failed to switch section: ${err.message}`;
    } finally {
        sectionOperationInProgress.value = false;
    }
};

// Save current section state helper
const saveCurrentSectionState = async () => {
    const currentSectionIndex = sections.value.findIndex(s => s.name === selectedSection.name);
    
    if (currentSectionIndex !== -1) {
        sections.value[currentSectionIndex] = {
            ...sections.value[currentSectionIndex],
            layout: [...selectedSection.layout],
            edit: selectedSection.edit,
            modified: new Date().toISOString()
        };
    }
};

// Enhanced delete section with backend integration
const deleteSection = async (item, event, skipConfirmation = false) => {
    if (sectionOperationInProgress.value) return;
    
    try {
        sectionOperationInProgress.value = true;
        if (event) event.stopPropagation();
        
        // Prevent deleting the last section
        if (sections.value.length <= 1) {
            error.value = 'Cannot delete the last section. At least one section is required.';
            return;
        }
        
        // Check if section has visualizations
        const sectionVisualizations = state.visualizations.filter(v => v.section_id === item.id);
        if (sectionVisualizations.length > 0 && !skipConfirmation) {
            confirmDeleteSection.value = {
                show: true,
                section: item
            };
            return;
        }
        
        // Delete section from backend
        await apiService.deleteDashboardSection(item.id);
        
        const isCurrentSection = selectedSection.id === item.id;
        
        // Remove the section from local state
        sections.value = sections.value.filter((section) => section.id !== item.id);
        
        // Remove visualizations for this section
        state.visualizations = state.visualizations.filter(v => v.section_id !== item.id);
        state.filteredVisualizations = state.filteredVisualizations.filter(v => v.section_id !== item.id);
        
        // Switch to another section if we deleted the current one
        if (isCurrentSection && sections.value.length > 0) {
            await setSection(sections.value[0]);
        }
        
        showToast(`Section "${item.name}" deleted successfully`, 'success');
        
    } catch (err) {
        console.error('Error deleting section:', err);
        error.value = `Failed to delete section: ${err.message}`;
        showToast('Failed to delete section', 'error');
    } finally {
        sectionOperationInProgress.value = false;
    }
};

// Enhanced section editing
const editSection = (item, event) => {
    event.stopPropagation();
    
    // Clear any existing errors for this section
    sectionErrors.value.delete(item.id);
    
    item.edit = !item.edit;
    tempName.value = item.name;
    
    // Focus on the input field after a brief delay
    if (item.edit) {
        setTimeout(() => {
            const input = document.querySelector(`[data-section-id="${item.id}"] input`);
            if (input) {
                input.focus();
                input.select();
            }
        }, 100);
    }
};

// Enhanced section renaming with backend integration
const renameSection = async (item, event) => {
    try {
        if (event) event.stopPropagation();
        
        if (!tempName.value || tempName.value.trim() === '') {
            sectionErrors.value.set(item.id, 'Section name cannot be empty.');
            return;
        }
        
        const validationError = validateSectionName(tempName.value, item.name);
        if (validationError) {
            sectionErrors.value.set(item.id, validationError);
            return;
        }
        
        const oldName = item.name;
        const newName = tempName.value.trim();
        
        // Update section in backend
        const updatedSection = await apiService.updateDashboardSection(item.id, {
            name: newName,
            description: item.description
        });
        
        // Update local state
        item.edit = false;
        item.name = newName;
        item.modified = new Date().toISOString();
        
        // Update selectedSection if this was the active section
        if (selectedSection.id === item.id) {
            selectedSection.name = newName;
        }
        
        // Clear errors
        sectionErrors.value.delete(item.id);
        tempName.value = "";
        
        showToast(`Section renamed to "${newName}"`, 'success');
        
    } catch (err) {
        console.error('Error renaming section:', err);
        sectionErrors.value.set(item.id, `Failed to rename: ${err.message}`);
        showToast('Failed to rename section', 'error');
    }
};

// Enhanced cancel edit
const cancelEdit = (item, event) => {
    event.stopPropagation();
    
    item.edit = false;
    tempName.value = "";
    sectionErrors.value.delete(item.id);
};

        // Handle confirmation dialog for section deletion
        const confirmSectionDeletion = async () => {
            if (confirmDeleteSection.value.section) {
                await deleteSection(confirmDeleteSection.value.section, null, true);
                confirmDeleteSection.value.show = false;
                confirmDeleteSection.value.section = null;
            }
        };

        // Global click handler to prevent event bubbling
        const cancelClick = (event) => {
            event.preventDefault();
            event.stopPropagation();
        };// Section management utilities with backend integration
const duplicateSection = async (item, event) => {
    if (sectionOperationInProgress.value) return;
    
    try {
        if (event) event.stopPropagation();
        sectionOperationInProgress.value = true;
        
        // Generate a unique name for the duplicated section
        const newName = generateUniqueSectionName(item.name);
        
        // Duplicate section in backend
        const duplicatedSection = await apiService.duplicateDashboardSection(item.id, newName);
        
        // Add to local state
        const newSection = {
            id: duplicatedSection.id,
            name: duplicatedSection.name,
            description: duplicatedSection.description,
            edit: false,
            layout: [], // Will be populated when visualizations are loaded
            created: duplicatedSection.created_at,
            modified: duplicatedSection.updated_at
        };
        
        sections.value.push(newSection);
        
        // Reload visualizations to include the new section's visualizations
        await loadVisualizations();
        
        // Switch to the duplicated section
        await setSection(newSection);
        
        showToast(`Section "${duplicatedSection.name}" duplicated successfully`, 'success');
        
    } catch (err) {
        console.error('Error duplicating section:', err);
        error.value = `Failed to duplicate section: ${err.message}`;
        showToast('Failed to duplicate section', 'error');
    } finally {
        sectionOperationInProgress.value = false;
    }
};

// Get section statistics from backend data
const getSectionStats = (section) => {
    if (!section || !section.id) {
        return {
            visualizations: 0,
            chartTypes: [],
            isEmpty: true
        };
    }
    
    const sectionVisualizations = state.visualizations.filter(v => v.section_id === section.id);
    const chartTypes = sectionVisualizations.length > 0 ? 
        [...new Set(sectionVisualizations.map(v => v.type))].sort() : [];
    
    return {
        visualizations: sectionVisualizations.length,
        chartTypes: chartTypes,
        isEmpty: sectionVisualizations.length === 0
    };
};

// Reorder sections with backend integration
const moveSectionUp = async (index) => {
    if (index > 0) {
        try {
            // Swap sections locally
            const temp = sections.value[index];
            sections.value[index] = sections.value[index - 1];
            sections.value[index - 1] = temp;
            
            // Update backend with new order - API expects array of section IDs
            const sectionIds = sections.value.map(section => section.id);
            
            await apiService.reorderDashboardSections(dashboardData.value.id, sectionIds);
            showToast('Section moved up successfully', 'success');
        } catch (error) {
            console.error('Error moving section up:', error);
            // Revert local changes on error
            const temp = sections.value[index];
            sections.value[index] = sections.value[index - 1];
            sections.value[index - 1] = temp;
            showToast('Failed to reorder section', 'error');
        }
    }
};

const moveSectionDown = async (index) => {
    if (index < sections.value.length - 1) {
        try {
            // Swap sections locally
            const temp = sections.value[index];
            sections.value[index] = sections.value[index + 1];
            sections.value[index + 1] = temp;
            
            const sectionIds = sections.value.map(section => section.id);
            
            await apiService.reorderDashboardSections(dashboardData.value.id, sectionIds);
            showToast('Section moved down successfully', 'success');
        } catch (error) {
            console.error('Error moving section down:', error);
            // Revert local changes on error
            const temp = sections.value[index];
            sections.value[index] = sections.value[index + 1];
            sections.value[index + 1] = temp;
            showToast('Failed to reorder section', 'error');
        }
    }
};

// Layout Organization
const organizeVisualizations = (resizeBool) => {
    let layoutCopy = [...selectedSection.layout];
    let sortedLayout = [];
    
    // Sort widgets by their current positions
    layoutCopy.forEach((object) => {
        object.position = object.x + object.y;
        if (sortedLayout.length === 0) {
            sortedLayout.push(object);
        } else {
            for (let index = 0; index < sortedLayout.length; index++) {
                const value = sortedLayout[index];
                if (object.position <= value.position) {
                    sortedLayout.splice(index, 0, object);
                    break;
                } else if (index === sortedLayout.length - 1) {
                    sortedLayout.push(object);
                    break;
                }
            }
        }
    });

    let currX = 0;
    selectedSection.layout = [];
    let row = 0;

    // Adjust layout and size of widgets
    sortedLayout.forEach((object) => {
        if (resizeBool) {
            if (object.chart === "Map") {
                object.w = 7;
                object.h = 13;
            } else {
                object.w = 4;
                object.h = 8;
            }
        }

        if (currX + object.w > 12) {
            currX = 0;
            row++;
        }
        object.x = currX;
        currX += object.w;
        object.y = row;

        selectedSection.layout.push(object);
    });
};

// Export Functions
const exportToPNG = async () => {
    try {
        const element = document.querySelector('.grid-space-static') || document.querySelector('.grid-space');
        if (!element) return;

        const canvas = await html2canvas(element, {
            useCORS: true,
            allowTaint: true,
            scale: 2,
            backgroundColor: '#ffffff',
            logging: false,
        });

        const link = document.createElement('a');
        link.download = `${city.value}_dashboard_${new Date().toISOString().split('T')[0]}.png`;
        link.href = canvas.toDataURL('image/png', 1.0);
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);

    } catch (error) {
        console.error('Error exporting to PNG:', error);
        error.value = 'Failed to export dashboard as PNG';
    }
};

const exportToPDF = async () => {
    try {
        const pdf = new jsPDF('p', 'mm', 'a4', true);
        const pageWidth = pdf.internal.pageSize.getWidth();
        const pageHeight = pdf.internal.pageSize.getHeight();
        const margin = 15;
        const contentWidth = pageWidth - (2 * margin);

        let yPosition = 35;
        const charts = selectedSection.layout.map(item => document.getElementById(item.i));
        let pageNumber = 1;

        // Add header
        pdf.setFillColor(1, 119, 169);
        pdf.rect(0, 0, pageWidth, 25, 'F');
        pdf.setTextColor(255, 255, 255);
        pdf.setFontSize(16);
        pdf.text(`${city.value} Dashboard`, margin, 17);

        for (let i = 0; i < charts.length; i++) {
            if (!charts[i]) continue;

            const canvas = await html2canvas(charts[i], {
                useCORS: true,
                allowTaint: true,
                scale: 2,
                backgroundColor: '#ffffff',
                logging: false
            });

            const imgData = canvas.toDataURL('image/png', 1.0);
            const imgWidth = contentWidth;
            const imgHeight = (canvas.height * imgWidth) / canvas.width;

            if (yPosition + imgHeight + 20 > pageHeight) {
                pdf.addPage();
                pageNumber++;
                yPosition = 35;
            }

            pdf.addImage(imgData, 'PNG', margin, yPosition, imgWidth, imgHeight);
            yPosition += imgHeight + 20;
        }

        pdf.save(`${city.value}_dashboard_${new Date().toISOString().split('T')[0]}.pdf`);

    } catch (error) {
        console.error('Error exporting to PDF:', error);
        error.value = 'Failed to export dashboard as PDF';
    }
};

// Drag & Drop functionality
const mouseAt = { x: -1, y: -1 };
const dropId = 'drop';
const dragItem = ref({ x: 0, y: 0, w: 2, h: 2, i: '' });
const dragItemStop = ref({});
const gridSpaceRef = ref(null);
const gridLayout = ref(null);

function syncMousePosition(event) {
    mouseAt.x = event.clientX;
    mouseAt.y = event.clientY;
}

const drag = throttle((chart) => {
    const parentRect = gridSpaceRef.value?.getBoundingClientRect();
    if (!parentRect || !gridLayout.value) return;

    const mouseInGrid = mouseAt.x > parentRect.left && mouseAt.x < parentRect.right &&
                       mouseAt.y > parentRect.top && mouseAt.y < parentRect.bottom;
                       
    if (mouseInGrid) {
        dragItem.value.x = mouseAt.x - parentRect.left;
        dragItem.value.y = mouseAt.y - parentRect.top;
        
        if (!selectedSection.layout.find(item => item.i === dropId)) {
            selectedSection.layout.push({
                x: 0, y: 0, w: 4, h: 4,
                i: dropId, chart: "", id: dropId,
                attributes: { title: "", city: city.value, tableId: "" }
            });
        }
    }

    const index = selectedSection.layout.findIndex(item => item.i === dropId);
    if (dragItemStop.value.chart) {
        dragItemStop.value = {};
        selectedSection.layout = selectedSection.layout.filter(item => item.i !== dropId);
        return;
    }
    
    if (index !== -1) {
        const item = gridLayout.value.getItem(dropId);
        if (!item) return;

        Object.assign(item.state, {
            top: mouseAt.y - parentRect.top,
            left: mouseAt.x - parentRect.left
        });
        
        const newPos = item.calcXY(mouseAt.y - parentRect.top, mouseAt.x - parentRect.left);
        
        if (mouseInGrid) {
            gridLayout.value.dragEvent('dragstart', dropId, newPos.x, newPos.y, dragItem.value.h, dragItem.value.w);
            dragItem.value.i = String(index);
            dragItem.value.x = selectedSection.layout[index].x;
            dragItem.value.y = selectedSection.layout[index].y;
        } else {
            gridLayout.value.dragEvent('dragend', dropId, newPos.x, newPos.y, dragItem.value.h, dragItem.value.w);
            selectedSection.layout = selectedSection.layout.filter(item => item.i !== dropId);
        }
    }
});

function dragEnd(chart) {
    const parentRect = gridSpaceRef.value?.getBoundingClientRect();
    if (!parentRect || !gridLayout.value) return;

    const mouseInGrid = mouseAt.x > parentRect.left && mouseAt.x < parentRect.right &&
                       mouseAt.y > parentRect.top && mouseAt.y < parentRect.bottom;

    if (mouseInGrid) {
        dragItemStop.value = JSON.parse(JSON.stringify(dragItem.value));
        dragItemStop.value.chart = chart;
        toggleKPIForm(chart);
        gridLayout.value.dragEvent('dragend', dropId, dragItemStop.value.x, dragItemStop.value.y, 
                                  dragItemStop.value.h, dragItemStop.value.w);
        selectedSection.layout = selectedSection.layout.filter(item => item.i !== dropId);
    }
}

// Chat functionality
const toggleChat = () => {
    chatMode.value = !chatMode.value;
};

const handleGlobalMonthChange = (monthValue) => {
    console.log('Dashboard handleGlobalMonthChange - new month:', monthValue);
    globalMonthFilter.value = monthValue;
    console.log('Dashboard globalMonthFilter updated to:', globalMonthFilter.value);
};

// Lifecycle
const handleKeycloakLoginSuccess = async () => {
    if (auth.isAuthenticated.value) {
        console.log('User logged in, refreshing dashboard');
        try {
            await loadDashboard();
        } catch (error) {
            console.error('Error refreshing dashboard after login:', error);
        }
    }
};

onMounted(async () => {
    document.addEventListener('dragover', syncMousePosition);
    document.addEventListener('mousemove', syncMousePosition);
    window.addEventListener('keycloak-login-success', handleKeycloakLoginSuccess);
    
    // Load initial data
    await loadDashboard();
});

onBeforeUnmount(() => {
    document.removeEventListener('dragover', syncMousePosition);
    document.removeEventListener('mousemove', syncMousePosition);
    window.removeEventListener('keycloak-login-success', handleKeycloakLoginSuccess);
});

// Watch for route changes
watch(() => route.params.city, async (newCity) => {
    if (newCity) {
        city.value = newCity;
        await loadDashboard();
    }
});

// Clear error after 5 seconds
watch(error, (newError) => {
    if (newError) {
        setTimeout(() => {
            error.value = null;
        }, 5000);
    }
});
</script>

<template>
    <AuthRequired>
        <div class="dashboard-container">
            <!-- Loading State -->
            <div v-if="loading" class="loading-state">
                <div class="spinner"></div>
                <p>Loading dashboard...</p>
            </div>

            <!-- Error State -->
            <div v-if="error" class="error-banner">
                <div class="error-content">
                    <Icon icon="material-symbols:error" class="error-icon" />
                    <span>{{ error }}</span>
                    <v-btn size="small" @click="error = null" icon="mdi-close" variant="text"></v-btn>
                </div>
            </div>

            <div v-if="!loading" class="dashboard-content">
                <!-- Header -->
                <div class="dashboard-header">
                    <div class="city-title-container">
                        <h2 class="city-title">
                            <img v-if="flag" :src='"../../" + flag' class="city-flag" alt="City flag" />
                            {{ cityDisplayName }} Dashboard
                        </h2>
                        <div class="dashboard-meta">
                            <span v-if="auth.userType.value" class="user-badge" :class="`badge-${auth.userType.value}`">
                                <Icon icon="material-symbols:person" />
                                {{ auth.userType.value === 'admin' ? 'Administrator' : 'City User' }}
                            </span>
                            <span v-if="dashboardData" class="dashboard-info">
                                <Icon icon="material-symbols:dashboard" />
                                {{ sections.length }} Section{{ sections.length !== 1 ? 's' : '' }}
                            </span>
                            <span v-if="selectedSection.layout.length > 0" class="dashboard-info">
                                <Icon icon="material-symbols:widgets" />
                                {{ selectedSection.layout.length }} Visualization{{ selectedSection.layout.length !== 1 ? 's' : '' }}
                            </span>
                        </div>
                    </div>
                </div>

                <!-- Edit Mode -->
                <div v-if="editMode && canCreateDashboard" class="edit-mode">
                    <div class="edit-header">
                        <div class="edit-header-content">
                            <div class="left-section">
                                <v-menu>
                                    <template v-slot:activator="{ props }">
                                        <v-btn v-bind="props" size="large" class="section-btn">
                                            {{ selectedSection.name }} 
                                            <Icon icon="material-symbols:arrow-drop-down" />
                                        </v-btn>
                                    </template>
                                    <v-list>
                                        <v-list-item
                                            v-for="(section, index) in sections"
                                            :key="section.id || index"
                                            @click="!section.edit && setSection(section)"
                                            class="list-item-wrapper"
                                            :class="{ 
                                                'active-section': selectedSection.name === section.name,
                                                'editing-section': section.edit
                                            }"
                                        >
                                            <div class="list-item-content" :data-section-id="section.id">
                                                <!-- Section Display/Edit Mode -->
                                                <div v-if="!section.edit" class="section-display">
                                                    <div class="section-info">
                                                        <div class="section-name">
                                                            {{ section.name }}
                                                            <v-chip 
                                                                v-if="getSectionStats(section).visualizations > 0"
                                                                size="x-small" 
                                                                class="visualization-count"
                                                            >
                                                                {{ getSectionStats(section).visualizations }}
                                                            </v-chip>
                                                        </div>
                                                        <div v-if="getSectionStats(section).chartTypes.length > 0" class="section-types">
                                                            <v-chip 
                                                                v-for="type in getSectionStats(section).chartTypes.slice(0, 3)" 
                                                                :key="type"
                                                                size="x-small"
                                                                variant="outlined"
                                                                class="chart-type-chip"
                                                            >
                                                                {{ type }}
                                                            </v-chip>
                                                            <span v-if="getSectionStats(section).chartTypes.length > 3" class="more-types">
                                                                +{{ getSectionStats(section).chartTypes.length - 3 }}
                                                            </span>
                                                        </div>
                                                    </div>
                                                </div>
                                                
                                                <!-- Edit Mode -->
                                                <v-text-field
                                                    v-else
                                                    v-model="tempName"
                                                    @keyup.enter="renameSection(section, $event)"
                                                    @keyup.escape="cancelEdit(section, $event)"
                                                    @click="cancelClick"
                                                    density="compact"
                                                    hide-details
                                                    autofocus
                                                    :error="sectionErrors.has(section.id)"
                                                    :error-messages="sectionErrors.get(section.id)"
                                                    placeholder="Enter section name..."
                                                />
                                                
                                                <!-- Section Actions -->
                                                <div class="section-actions">
                                                    <!-- View Mode Actions -->
                                                    <template v-if="!section.edit">
                                                        <v-tooltip text="Duplicate Section">
                                                            <template v-slot:activator="{ props: tooltipProps }">
                                                                <Icon 
                                                                    v-bind="tooltipProps"
                                                                    icon="material-symbols:content-copy" 
                                                                    @click="duplicateSection(section, $event)"
                                                                    class="action-icon copy-icon"
                                                                    :class="{ disabled: sectionOperationInProgress }"
                                                                />
                                                            </template>
                                                        </v-tooltip>
                                                        
                                                        <v-tooltip text="Move Up" v-if="index > 0">
                                                            <template v-slot:activator="{ props: tooltipProps }">
                                                                <Icon 
                                                                    v-bind="tooltipProps"
                                                                    icon="material-symbols:keyboard-arrow-up" 
                                                                    @click="moveSectionUp(index)"
                                                                    class="action-icon move-icon"
                                                                />
                                                            </template>
                                                        </v-tooltip>
                                                        
                                                        <v-tooltip text="Move Down" v-if="index < sections.length - 1">
                                                            <template v-slot:activator="{ props: tooltipProps }">
                                                                <Icon 
                                                                    v-bind="tooltipProps"
                                                                    icon="material-symbols:keyboard-arrow-down" 
                                                                    @click="moveSectionDown(index)"
                                                                    class="action-icon move-icon"
                                                                />
                                                            </template>
                                                        </v-tooltip>
                                                        
                                                        <v-tooltip text="Edit Section">
                                                            <template v-slot:activator="{ props: tooltipProps }">
                                                                <Icon 
                                                                    v-bind="tooltipProps"
                                                                    icon="material-symbols:edit" 
                                                                    @click="editSection(section, $event)"
                                                                    class="action-icon edit-icon"
                                                                />
                                                            </template>
                                                        </v-tooltip>
                                                        
                                                        <v-tooltip text="Delete Section">
                                                            <template v-slot:activator="{ props: tooltipProps }">
                                                                <Icon 
                                                                    v-bind="tooltipProps"
                                                                    icon="material-symbols:delete" 
                                                                    @click="deleteSection(section, $event)"
                                                                    class="action-icon delete-icon"
                                                                    :class="{ disabled: sections.length <= 1 }"
                                                                />
                                                            </template>
                                                        </v-tooltip>
                                                    </template>
                                                    
                                                    <!-- Edit Mode Actions -->
                                                    <template v-else>
                                                        <v-tooltip text="Save Changes">
                                                            <template v-slot:activator="{ props: tooltipProps }">
                                                                <Icon 
                                                                    v-bind="tooltipProps"
                                                                    icon="material-symbols:check" 
                                                                    @click="renameSection(section, $event)"
                                                                    class="action-icon save-icon"
                                                                />
                                                            </template>
                                                        </v-tooltip>
                                                        
                                                        <v-tooltip text="Cancel">
                                                            <template v-slot:activator="{ props: tooltipProps }">
                                                                <Icon 
                                                                    v-bind="tooltipProps"
                                                                    icon="material-symbols:close" 
                                                                    @click="cancelEdit(section, $event)"
                                                                    class="action-icon cancel-icon"
                                                                />
                                                            </template>
                                                        </v-tooltip>
                                                    </template>
                                                </div>
                                            </div>
                                        </v-list-item>
                                        
                                        <v-divider />
                                        
                                        <v-list-item 
                                            @click="addSection" 
                                            class="add-section-item"
                                            :disabled="sectionOperationInProgress"
                                        >
                                            <div class="add-section-content">
                                                <Icon icon="material-symbols:add" />
                                                <span>Add Section</span>
                                                <v-progress-circular
                                                    v-if="sectionOperationInProgress"
                                                    indeterminate
                                                    size="16"
                                                    class="ml-2"
                                                />
                                            </div>
                                        </v-list-item>
                                    </v-list>
                                </v-menu>
                            </div>
                            
                            <div class="right-section">
                                <v-btn 
                                    size="large" 
                                    @click="toggleEditMode" 
                                    color="red" 
                                    class="action-btn"
                                >
                                    <Icon icon="material-symbols:edit-off" />
                                    Exit Edit Mode
                                </v-btn>
                                <v-btn 
                                    size="large" 
                                    @click="saveDashboard" 
                                    :loading="isSaving" 
                                    :disabled="isSaving" 
                                    color="success"
                                    class="action-btn"
                                >
                                    <Icon icon="material-symbols:save" />
                                    {{ isSaving ? 'Saving...' : 'Save Dashboard' }}
                                </v-btn>
                                <v-btn 
                                    size="large" 
                                    @click="organizeVisualizations(false)" 
                                    color="primary"
                                    class="action-btn"
                                >
                                    <Icon icon="material-symbols:border-all" />
                                    Organize
                                </v-btn>
                                <v-btn 
                                    size="large" 
                                    @click="organizeVisualizations(true)" 
                                    color="primary"
                                    class="action-btn"
                                >
                                    <Icon icon="material-symbols:border-all" />
                                    Organize & Resize
                                </v-btn>
                                <v-btn 
                                    size="large" 
                                    @click="toggleChat" 
                                    color="primary"
                                    class="action-btn"
                                >
                                    <Icon icon="material-symbols:chat" />
                                    Assistant
                                </v-btn>
                            </div>
                        </div>
                    </div>

                    <div class="edit-container">
                        <!-- Widget Sidebar -->
                        <div class="widget-sidebar">
                            <div class="widget-sidebar-content">
                                <h3 class="widget-title">Choose widgets</h3>
                                
                                <div class="widget-grid">
                                    <div 
                                        class="widget-item"
                                        draggable="true"
                                        unselectable="on"
                                        @drag="drag('LineChart')"
                                        @dragend="dragEnd('LineChart')"
                                        @click="toggleKPIForm('LineChart')"
                                    >
                                        <Icon icon="material-symbols:show-chart" class="widget-icon" />
                                        <span>Line Chart</span>
                                    </div>
                                    
                                    <div 
                                        class="widget-item"
                                        draggable="true"
                                        unselectable="on"
                                        @drag="drag('PieChart')"
                                        @dragend="dragEnd('PieChart')"
                                        @click="toggleKPIForm('PieChart')"
                                    >
                                        <Icon icon="material-symbols:pie-chart" class="widget-icon" />
                                        <span>Pie Chart</span>
                                    </div>
                                    
                                    <div 
                                        class="widget-item"
                                        draggable="true"
                                        unselectable="on"
                                        @drag="drag('BarChart')"
                                        @dragend="dragEnd('BarChart')"
                                        @click="toggleKPIForm('BarChart')"
                                    >
                                        <Icon icon="material-symbols:bar-chart" class="widget-icon" />
                                        <span>Bar Chart</span>
                                    </div>
                                    
                                    <div 
                                        class="widget-item"
                                        draggable="true"
                                        unselectable="on"
                                        @drag="drag('StatChart')"
                                        @dragend="dragEnd('StatChart')"
                                        @click="toggleKPIForm('StatChart')"
                                    >
                                        <Icon icon="material-symbols:speed" class="widget-icon" />
                                        <span>Stat Chart</span>
                                    </div>
                                    
                                    <div 
                                        class="widget-item"
                                        draggable="true"
                                        unselectable="on"
                                        @drag="drag('Table')"
                                        @dragend="dragEnd('Table')"
                                        @click="toggleKPIForm('Table')"
                                    >
                                        <Icon icon="material-symbols:table" class="widget-icon" />
                                        <span>Table</span>
                                    </div>
                                    
                                    <div 
                                        class="widget-item"
                                        draggable="true"
                                        unselectable="on"
                                        @drag="drag('Map')"
                                        @dragend="dragEnd('Map')"
                                        @click="toggleKPIForm('Map')"
                                    >
                                        <Icon icon="material-symbols:map" class="widget-icon" />
                                        <span>Map</span>
                                    </div>
                                    <div 
                                        class="widget-item"
                                        draggable="true"
                                        unselectable="on"
                                        @drag="drag('FreeTextField')"
                                        @dragend="dragEnd('FreeTextField')"
                                        @click="toggleKPIForm('FreeTextField')"
                                    >
                                        <Icon icon="material-symbols:notes" class="widget-icon" />
                                        <span>Text Field</span>
                                    </div>
                                    <div 
                                        class="widget-item"
                                        draggable="true"
                                        unselectable="on"
                                        @drag="drag('Timeline')"
                                        @dragend="dragEnd('Timeline')"
                                        @click="toggleKPIForm('Timeline')"
                                    >
                                        <Icon icon="material-symbols:timeline" class="widget-icon" />
                                        <span>Timeline</span>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- Grid Space -->
                        <div ref="gridSpaceRef" class="grid-space">
                            <GridLayout 
                                v-model:layout="selectedSection.layout" 
                                ref="gridLayout" 
                                :col-num="12" 
                                :row-height="30"
                                is-draggable 
                                is-bounded 
                                use-css-transforms 
                                restore-on-drag 
                                :vertical-compact="false" 
                                class="grid-layout"
                            >
                                <GridItem
                                    v-for="item in selectedSection.layout"
                                    :key="item.i"
                                    :x="item.x"
                                    :y="item.y"
                                    :w="item.w"
                                    :h="item.h"
                                    :i="item.i"
                                    :id="item.i"
                                    class="grid-item"
                                >
                                    <!-- Drop placeholder (shown during drag) -->
                                    <div v-if="item.i === 'drop'" class="drop-placeholder">
                                        <Icon icon="material-symbols:add" class="drop-icon" />
                                        <span>Drop widget here</span>
                                    </div>
                                    
                                    <!-- Regular grid item -->
                                    <div v-else class="grid-item-content">
                                        <div class="grid-item-header">
                                            <div class="grid-item-type">
                                                <Icon 
                                                    :icon="item.chart === 'LineChart' ? 'material-symbols:show-chart' :
                                                           item.chart === 'PieChart' ? 'material-symbols:pie-chart' :
                                                           item.chart === 'BarChart' ? 'material-symbols:bar-chart' :
                                                           item.chart === 'StatChart' ? 'material-symbols:speed' :
                                                           item.chart === 'Table' ? 'material-symbols:table' :
                                                           item.chart === 'Map' ? 'material-symbols:map' :
                                                           item.chart === 'Timeline' ? 'material-symbols:timeline' :
                                                           item.chart === 'FreeTextField' ? 'material-symbols:notes' :
                                                           'material-symbols:widgets'"
                                                    class="widget-type-icon"
                                                />
                                                <span class="widget-type-label">{{ item.chart }}</span>
                                            </div>
                                            <div class="grid-item-actions">
                                                <Icon 
                                                    icon="material-symbols:edit" 
                                                    @click="editVisualization(item)"
                                                    class="action-icon edit-icon"
                                                />
                                                <Icon 
                                                    icon="material-symbols:delete" 
                                                    @click="deleteVisualization(item)"
                                                    class="action-icon delete-icon"
                                                />
                                            </div>
                                        </div>
                                        
                                        <div class="grid-item-body">
                                            <component 
                                                v-if="item.chart && componentMap[item.chart]"
                                                :is="componentMap[item.chart]"
                                                v-bind="item.chart === 'FreeTextField' ? {
                                                    canEdit: true,
                                                    attributes: item.attributes
                                                } : item.chart === 'Timeline' ? {
                                                    title: item.attributes.title,
                                                    attributes: item.attributes,
                                                    isEditMode: true
                                                } : item.attributes"
                                                :month-filter="globalMonthFilter"
                                                @edit="editVisualization(item)"
                                            />
                                        </div>
                                    </div>
                                </GridItem>
                            </GridLayout>
                        </div>
                    </div>

                    <!-- Edit Forms -->
                    <div class="edit-forms">
                        <KPIForm 
                            v-if="tableForm" 
                            @cancel="toggleKPIForm" 
                            @createVisualisation="createVisualization" 
                            :city="city"
                            :city-id="cityData?.id"
                            :chart="currentSelectedChart"
                        />
                        <LineChartForm 
                            v-if="lineChartBool" 
                            @cancel="closeAllForms" 
                            @updateChart="updateChart"
                            v-bind="currentItem.attributes"
                        />
                        <PieChartForm 
                            v-if="pieChartBool" 
                            @cancel="closeAllForms" 
                            @updateChart="updateChart"
                            :title="currentItem.attributes?.title"
                        />
                        <BarChartForm 
                            v-if="barChartBool" 
                            @cancel="closeAllForms" 
                            @updateChart="updateChart"
                            :title="currentItem.attributes?.title"
                        />
                        <StatChartForm 
                            v-if="statChartBool" 
                            @cancel="closeAllForms" 
                            @updateChart="updateChart"
                            :title="currentItem.attributes?.title"
                            :suffix="currentItem.attributes?.suffix"
                        />
                        <TableForm 
                            v-if="tableBool" 
                            @cancel="closeAllForms" 
                            @updateChart="updateChart"
                            :city="city"
                            v-bind="currentItem.attributes"
                        />
                        <TimelineForm 
                            v-if="showTimelineForm" 
                            :show="showTimelineForm"
                            :timeline="editingTimeline?.attributes || { description: '', events: [] }"
                            :availableKPIs="currentTimelineKPIs"
                            :isEdit="!!editingTimeline"
                            @close="closeTimelineForm"
                            @save="saveTimelineData"
                        />
                    </div>
                </div>

                <!-- View Mode -->
                <div v-else class="view-mode">
                    <div class="view-header">
                        <div class="view-header-content">
                            <div class="left-section">
                                <v-menu>
                                    <template v-slot:activator="{ props }">
                                        <v-btn v-bind="props" size="large" class="section-btn">
                                            {{ selectedSection.name }}
                                            <Icon icon="material-symbols:arrow-drop-down" />
                                        </v-btn>
                                    </template>
                                    <v-list>
                                        <v-list-item
                                            v-for="(section, index) in sections"
                                            :key="index"
                                            @click="setSection(section)"
                                            class="list-item-wrapper"
                                        >
                                            {{ section.name }}
                                        </v-list-item>
                                    </v-list>
                                </v-menu>
                            </div>
                            
                            <div class="right-section">
                                <MonthFilter 
                                    @monthChange="handleGlobalMonthChange"
                                    :value="globalMonthFilter"
                                    class="month-filter"
                                />
                                
                                <v-menu>
                                    <template v-slot:activator="{ props }">
                                        <v-btn v-bind="props" size="large" color="primary" class="action-btn">
                                            <Icon icon="material-symbols:download" />
                                            Export
                                        </v-btn>
                                    </template>
                                    <v-list>
                                        <v-list-item @click="exportToPNG">
                                            <Icon icon="material-symbols:image" />
                                            Export as PNG
                                        </v-list-item>
                                        <v-list-item @click="exportToPDF">
                                            <Icon icon="material-symbols:picture-as-pdf" />
                                            Export as PDF
                                        </v-list-item>
                                    </v-list>
                                </v-menu>
                                
                                <v-btn 
                                    v-if="canCreateDashboard"
                                    size="large" 
                                    @click="toggleEditMode" 
                                    color="primary"
                                    class="action-btn"
                                >
                                    <Icon icon="material-symbols:edit" />
                                    Edit Dashboard
                                </v-btn>
                            </div>
                        </div>
                    </div>

                    <!-- Dashboard Grid (View Mode) -->
                    <div v-if="selectedSection.layout.length > 0" class="dashboard-grid">
                        <div class="grid-space-static">
                            <GridLayout 
                                v-model:layout="selectedSection.layout" 
                                :col-num="12" 
                                :row-height="30"
                                :is-draggable="false" 
                                :is-resizable="false" 
                                is-bounded 
                                use-css-transforms 
                                restore-on-drag
                                :vertical-compact="false" 
                                class="static-grid-layout"
                            >
                                <GridItem
                                    v-for="item in selectedSection.layout"
                                    :key="item.i"
                                    :x="item.x"
                                    :y="item.y"
                                    :w="item.w"
                                    :h="item.h"
                                    :i="item.i"
                                    :id="item.i"
                                    class="static-grid-item"
                                >
                                    <div class="static-item-content">
                                        <component 
                                            :is="componentMap[item.chart]"
                                            v-bind="item.chart === 'FreeTextField' ? {
                                                canEdit: false,
                                                attributes: item.attributes
                                            } : item.chart === 'Timeline' ? {
                                                title: item.attributes.title,
                                                attributes: item.attributes,
                                                isEditMode: false
                                            } : item.attributes"
                                            :month-filter="globalMonthFilter"
                                        />
                                    </div>
                                </GridItem>
                            </GridLayout>
                        </div>
                    </div>
                    
                    <!-- Empty State -->
                    <div v-else class="empty-state">
                        <div class="empty-content">
                            <Icon icon="material-symbols:dashboard" class="empty-icon" />
                            <h3>No visualizations yet</h3>
                            <p>{{ canCreateDashboard ? 'Click "Edit Dashboard" to add your first visualization' : 'This dashboard is empty' }}</p>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Chat Popup -->
            <div v-if="chatMode" class="chat-popup">
                <div class="chat-popup-inner">
                    <div class="chat-header">
                        <h3>Dashboard Assistant</h3>
                        <v-btn icon="mdi-close" size="small" @click="toggleChat" />
                    </div>
                    <DashboardChat 
                        :city="city" 
                        @createVisualisation="createVisualization"
                    />
                </div>
            </div>
        </div>
        
        <!-- Delete Section Confirmation Dialog -->
        <v-dialog v-model="confirmDeleteSection.show" max-width="400">
            <v-card>
                <v-card-title>
                    <Icon icon="material-symbols:warning" color="orange" class="mr-2" />
                    Delete Section
                </v-card-title>
                <v-card-text>
                    <p>Are you sure you want to delete the section <strong>"{{ confirmDeleteSection.section?.name }}"</strong>?</p>
                    <p v-if="getSectionStats(confirmDeleteSection.section || {}).visualizations > 0" class="text-warning">
                        This will also delete {{ getSectionStats(confirmDeleteSection.section || {}).visualizations }} visualization(s).
                    </p>
                    <p class="text-caption text-disabled">This action cannot be undone.</p>
                </v-card-text>
                <v-card-actions>
                    <v-spacer />
                    <v-btn @click="confirmDeleteSection.show = false" text>Cancel</v-btn>
                    <v-btn 
                        @click="confirmSectionDeletion" 
                        color="error" 
                        :loading="sectionOperationInProgress"
                    >
                        Delete
                    </v-btn>
                </v-card-actions>
            </v-card>
        </v-dialog>
    </AuthRequired>
</template>

<style lang="scss" scoped>
.dashboard-container {
    padding: 20px;
    min-height: 100vh;
    background-color: #f5f5f5;
}

.loading-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 400px;
    
    .spinner {
        width: 40px;
        height: 40px;
        border: 4px solid #e3e3e3;
        border-top: 4px solid #3498db;
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }
    
    p {
        margin-top: 16px;
        color: #666;
        font-size: 16px;
    }
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

.error-banner {
    background-color: #ffebee;
    border: 1px solid #f44336;
    border-radius: 8px;
    margin-bottom: 16px;
    
    .error-content {
        display: flex;
        align-items: center;
        padding: 12px 16px;
        gap: 8px;
        
        .error-icon {
            color: #f44336;
        }
        
        span {
            flex: 1;
            color: #d32f2f;
            font-weight: 500;
        }
    }
}

.dashboard-header {
    margin-bottom: 24px;
    
    .city-title-container {
        display: flex;
        flex-direction: column;
        gap: 12px;
        
        .city-title {
            display: flex;
            align-items: center;
            gap: 16px;
            font-size: 32px;
            font-weight: 700;
            color: #333;
            margin: 0;
            
            .city-flag {
                width: 42px;
                height: 42px;
                border-radius: 50%;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
            }
        }
        
        .dashboard-meta {
            display: flex;
            align-items: center;
            gap: 16px;
            flex-wrap: wrap;
            
            .user-badge {
                display: inline-flex;
                align-items: center;
                gap: 6px;
                padding: 6px 14px;
                border-radius: 20px;
                font-size: 13px;
                font-weight: 600;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                
                &.badge-admin {
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                }
                
                &.badge-cityuser {
                    background: linear-gradient(135deg, #0177a9 0%, #06b6d4 100%);
                    color: white;
                }
            }
            
            .dashboard-info {
                display: inline-flex;
                align-items: center;
                gap: 6px;
                padding: 6px 14px;
                background: #f3f4f6;
                border-radius: 20px;
                font-size: 13px;
                font-weight: 500;
                color: #4b5563;
                
                svg {
                    font-size: 16px;
                    opacity: 0.7;
                }
            }
        }
    }
}

.edit-header, .view-header {
    background: white;
    border-radius: 12px;
    padding: 16px;
    margin-bottom: 20px;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
    
    .edit-header-content, .view-header-content {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 16px;
        
        .left-section, .right-section {
            display: flex;
            align-items: center;
            gap: 12px;
        }
        
        .section-btn {
            background-color: #f8f9fa;
            border: 1px solid #dee2e6;
        }
        
        .action-btn {
            display: flex;
            align-items: center;
            gap: 8px;
        }
    }
}

.edit-container {
    display: flex;
    background: white;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
    min-height: 800px;
}

.widget-sidebar {
    width: 250px;
    background: #0177a9;
    color: white;
    
    .widget-sidebar-content {
        padding: 20px;
        
        .widget-title {
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 20px;
            text-align: center;
        }
        
        .widget-grid {
            display: flex;
            flex-direction: column;
            gap: 12px;
        }
        
        .widget-item {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 12px;
            border-radius: 8px;
            cursor: grab;
            transition: all 0.2s ease;
            border: 2px dashed transparent;
            user-select: none;
            -webkit-user-select: none;
            -moz-user-select: none;
            -ms-user-select: none;
            
            &:hover {
                background-color: rgba(255, 255, 255, 0.1);
                border-color: rgba(255, 255, 255, 0.3);
                transform: translateX(4px);
            }
            
            &:active {
                cursor: grabbing;
            }
            
            .widget-icon {
                font-size: 24px;
                flex-shrink: 0;
            }
            
            span {
                font-weight: 500;
                flex: 1;
            }
        }
    }
}

.grid-space {
    flex: 1;
    padding: 20px;
    background: #fafafa;
    
    .grid-layout {
        min-height: 800px;
        position: relative;
        
        &::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background-image: 
                linear-gradient(to right, #e0e0e0 1px, transparent 1px),
                linear-gradient(to bottom, #e0e0e0 1px, transparent 1px);
            background-size: calc(100% / 12) 30px;
            background-repeat: repeat;
            z-index: 0;
        }
    }
    
    .grid-item {
        z-index: 1;
        
        .drop-placeholder {
            height: 100%;
            background: rgba(1, 119, 169, 0.1);
            border: 2px dashed #0177a9;
            border-radius: 8px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            gap: 8px;
            color: #0177a9;
            
            .drop-icon {
                font-size: 32px;
                animation: pulse 1.5s ease-in-out infinite;
            }
            
            span {
                font-weight: 500;
                font-size: 14px;
            }
        }
        
        .grid-item-content {
            height: 100%;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            border: 2px dashed #ccc;
            display: flex;
            flex-direction: column;
            
            &:hover {
                box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
            }
            
            .grid-item-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 8px 12px;
                border-bottom: 1px solid #eee;
                background: linear-gradient(to bottom, #fafafa 0%, #f5f5f5 100%);
                min-height: 40px;
                
                .grid-item-type {
                    display: flex;
                    align-items: center;
                    gap: 8px;
                    
                    .widget-type-icon {
                        font-size: 18px;
                        color: #0177a9;
                    }
                    
                    .widget-type-label {
                        font-size: 12px;
                        font-weight: 600;
                        color: #666;
                        text-transform: uppercase;
                        letter-spacing: 0.5px;
                    }
                }
                
                .grid-item-title {
                    font-size: 14px;
                    font-weight: 600;
                    margin: 0;
                    color: #333;
                    white-space: nowrap;
                    overflow: hidden;
                    text-overflow: ellipsis;
                    flex: 1;
                }
                
                .grid-item-actions {
                    display: flex;
                    gap: 8px;
                    
                    .action-icon {
                        cursor: pointer;
                        font-size: 24px;
                        color: #666;
                        transition: all 0.2s ease;
                        padding: 4px;
                        border-radius: 4px;
                        
                        &:hover {
                            background-color: rgba(0, 0, 0, 0.05);
                        }
                        
                        &.edit-icon:hover {
                            color: #0177a9;
                        }
                        
                        &.delete-icon:hover {
                            color: #f44336;
                        }
                    }
                }
            }
            
            .grid-item-body {
                flex: 1;
                padding: 12px;
                overflow: hidden;
            }
        }
    }
}

.dashboard-grid {
    .grid-space-static {
        .static-grid-layout {
            min-height: 600px;
        }
        
        .static-grid-item {
            .static-item-content {
                height: 100%;
                background: white;
                border-radius: 8px;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
                padding: 16px;
                overflow: hidden;
                
                &:hover {
                    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
                }
            }
        }
    }
}

.empty-state {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 400px;
    
    .empty-content {
        text-align: center;
        color: #666;
        
        .empty-icon {
            font-size: 64px;
            color: #ccc;
            margin-bottom: 16px;
        }
        
        h3 {
            font-size: 24px;
            margin-bottom: 8px;
        }
        
        p {
            font-size: 16px;
        }
    }
}

.list-item-wrapper {
    position: relative;
    border: 2px solid transparent;
    transition: all 0.2s ease;
    
    &:hover {
        background-color: rgba(0, 0, 0, 0.04);
    }
    
    &.active-section {
        border-left: 3px solid #1976d2;
        background-color: rgba(25, 118, 210, 0.08);
    }
    
    &.editing-section {
        background-color: rgba(255, 193, 7, 0.1);
        border-left: 3px solid #ffc107;
    }
    
    .list-item-content {
        display: flex;
        justify-content: space-between;
        align-items: center;
        width: 100%;
        padding: 8px 16px;
        
        .section-display {
            flex: 1;
            min-width: 0;
            
            .section-info {
                display: flex;
                flex-direction: column;
                gap: 4px;
                
                .section-name {
                    font-weight: 500;
                    color: #333;
                    display: flex;
                    align-items: center;
                    gap: 8px;
                    
                    .visualization-count {
                        background-color: #1976d2 !important;
                        color: white !important;
                        font-size: 10px !important;
                        height: 18px !important;
                        min-width: 18px !important;
                    }
                }
                
                .section-types {
                    display: flex;
                    gap: 4px;
                    align-items: center;
                    flex-wrap: wrap;
                    
                    .chart-type-chip {
                        font-size: 10px !important;
                        height: 16px !important;
                        color: #666 !important;
                        border-color: #ddd !important;
                    }
                    
                    .more-types {
                        font-size: 10px;
                        color: #999;
                        white-space: nowrap;
                    }
                }
            }
        }
        
        .section-actions {
            display: flex;
            gap: 6px;
            opacity: 0;
            transition: opacity 0.2s ease;
            flex-shrink: 0;
            
            .action-icon {
                cursor: pointer;
                font-size: 30px;
                padding: 6px;
                border-radius: 4px;
                transition: all 0.2s ease;
                
                &.disabled {
                    opacity: 0.3;
                    cursor: not-allowed;
                }
                
                &.edit-icon {
                    color: #1976d2;
                }
                
                &.delete-icon {
                    color: #d32f2f;
                }
                
                &.copy-icon {
                    color: #7b1fa2;
                }
                
                &.move-icon {
                    color: #388e3c;
                }
                
                &.save-icon {
                    color: #388e3c;
                }
                
                &.cancel-icon {
                    color: #757575;
                }
                
                &:not(.disabled):hover {
                    background-color: rgba(0, 0, 0, 0.08);
                    transform: scale(1.15);
                }
            }
        }
    }
    
    &:hover .section-actions,
    &.editing-section .section-actions {
        opacity: 1;
    }
}

.add-section-item {
    border-top: 1px solid #eee;
    color: #1976d2;
    font-weight: 500;
    
    &:hover {
        background-color: rgba(25, 118, 210, 0.04);
    }
    
    &:disabled {
        opacity: 0.6;
        cursor: not-allowed;
    }
    
    .add-section-content {
        display: flex;
        align-items: center;
        gap: 8px;
    }
}

.month-filter {
    margin-right: 12px;
}

.chat-popup {
    position: fixed;
    bottom: 20px;
    right: 20px;
    width: 400px;
    height: 600px;
    z-index: 9999;
    background: white;
    border-radius: 12px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
    display: flex;
    flex-direction: column;
    
    .chat-popup-inner {
        display: flex;
        flex-direction: column;
        height: 100%;
        
        .chat-header {
            height: 50px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0 20px;
            border-bottom: 1px solid #eee;
            background: #f8f9fa;
            border-radius: 12px 12px 0 0;
            
            h3 {
                margin: 0;
                color: #333;
                font-size: 16px;
            }
        }
    }
}

// Responsive design
@media (max-width: 768px) {
    .dashboard-container {
        padding: 10px;
    }
    
    .edit-header-content, .view-header-content {
        flex-direction: column;
        align-items: stretch;
        
        .left-section, .right-section {
            justify-content: center;
        }
    }
    
    .edit-container {
        flex-direction: column;
        
        .widget-sidebar {
            width: 100%;
            
            .widget-grid {
                flex-direction: row;
                flex-wrap: wrap;
                justify-content: center;
            }
            
            .widget-item {
                min-width: 120px;
            }
        }
    }
    
    .chat-popup {
        bottom: 10px;
        right: 10px;
        left: 10px;
        width: auto;
        height: 500px;
    }
}

// Dark mode support (if needed)
@media (prefers-color-scheme: dark) {
    .dashboard-container {
        background-color: #121212;
        color: #ffffff;
    }
    
    .edit-header, .view-header,
    .grid-item-content, .static-item-content {
        background-color: #1e1e1e;
        border-color: #333;
    }
    
    .grid-space {
        background-color: #181818;
    }
    
    .error-banner {
        background-color: #3c1518;
        border-color: #f44336;
    }
}

// Grid layout placeholder styling
:deep(.vgl-item--placeholder) {
    background: rgba(1, 119, 169, 0.2) !important;
    border: 2px dashed #0177a9 !important;
}

// Animations
@keyframes pulse {
    0%, 100% {
        opacity: 1;
        transform: scale(1);
    }
    50% {
        opacity: 0.6;
        transform: scale(1.1);
    }
}
</style>