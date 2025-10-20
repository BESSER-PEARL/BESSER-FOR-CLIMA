/**
 * Enhanced API service for the Climaborough dashboard
 * Provides a clean interface to the refactored backend API
 */

class ApiService {
    constructor(baseUrl = 'http://localhost:8000') {
        this.baseUrl = baseUrl;
        this.authToken = null;
    }

    // Set authentication token
    setAuthToken(token) {
        this.authToken = token;
    }

    // Generic request method with error handling
    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...(this.authToken && { 'Authorization': `Bearer ${this.authToken}` }),
                ...options.headers
            },
            ...options
        };

        try {
            const response = await fetch(url, config);
            
            if (!response.ok) {
                let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
                
                try {
                    const errorData = await response.json();
                    errorMessage = errorData.message || errorData.error || errorMessage;
                } catch {
                    // Use default error message if JSON parsing fails
                }
                
                throw new Error(errorMessage);
            }

            // Handle empty responses (204 No Content)
            if (response.status === 204) {
                return null;
            }

            const data = await response.json();
            return data;
            
        } catch (error) {
            console.error(`API request failed for ${endpoint}:`, error);
            throw error;
        }
    }

    // GET request
    async get(endpoint, params = {}) {
        const queryString = new URLSearchParams(params).toString();
        const url = queryString ? `${endpoint}?${queryString}` : endpoint;
        return this.request(url, { method: 'GET' });
    }

    // POST request
    async post(endpoint, data) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    // PUT request
    async put(endpoint, data) {
        return this.request(endpoint, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    }

    // DELETE request
    async delete(endpoint, data = null) {
        const options = { method: 'DELETE' };
        if (data) {
            options.body = JSON.stringify(data);
        }
        return this.request(endpoint, options);
    }

    // CITY API METHODS
    
    async getCities(params = {}) {
        return this.get('/cities', params);
    }

    async getCityById(cityId) {
        return this.get(`/cities/${cityId}`);
    }

    async getCityByCode(cityCode) {
        return this.get(`/cities/code/${cityCode.toLowerCase()}`);
    }

    async getCityStats(cityId) {
        return this.get(`/cities/${cityId}/stats`);
    }

    async createCity(cityData) {
        return this.post('/cities', cityData);
    }

    async updateCity(cityId, cityData) {
        return this.put(`/cities/${cityId}`, cityData);
    }

    async deleteCity(cityId) {
        return this.delete(`/cities/${cityId}`);
    }

    // KPI API METHODS
    
    async getKPIs(cityId, params = {}) {
        return this.get('/kpis', { city_id: cityId, ...params });
    }

    async getKPIById(kpiId) {
        return this.get(`/kpis/${kpiId}`);
    }

    async getKPIByKpiId(idKpi) {
        return this.get(`/kpis/by-kpi-id/${idKpi}`);
    }

    async getKPIWithLatestValue(kpiId) {
        return this.get(`/kpis/${kpiId}/with-latest-value`);
    }

    async getKPICategories(cityId) {
        return this.get('/kpis/categories', { city_id: cityId });
    }

    async createKPI(kpiData) {
        return this.post('/kpis', kpiData);
    }

    async updateKPI(kpiId, kpiData) {
        return this.put(`/kpis/${kpiId}`, kpiData);
    }

    async deleteKPI(kpiId) {
        return this.delete(`/kpis/${kpiId}`);
    }

    // KPI VALUES API METHODS
    
    async getKPIValues(kpiId, params = {}) {
        return this.get(`/kpis/${kpiId}/values`, params);
    }

    /**
     * Get KPI values filtered by month
     * @param {number} kpiId - The KPI ID
     * @param {string} monthFilter - Month filter in format "YYYY-MM" (e.g., "2025-10")
     * @param {object} additionalParams - Additional query parameters
     * @returns {Promise} - Promise resolving to KPI values
     */
    async getKPIValuesByMonth(kpiId, monthFilter, additionalParams = {}) {
        if (!monthFilter) {
            return this.getKPIValues(kpiId, additionalParams);
        }

        // Check if it's a date range (format: start|end)
        if (monthFilter.includes('|')) {
            const [start, end] = monthFilter.split('|');
            const startDate = new Date(start);
            const endDate = new Date(end);
            endDate.setHours(23, 59, 59, 999); // End of day

            return this.get(`/kpis/${kpiId}/values`, {
                start_date: startDate.toISOString(),
                end_date: endDate.toISOString(),
                ...additionalParams
            });
        }

        // Otherwise treat as "YYYY-MM" month format
        const [year, month] = monthFilter.split('-').map(Number);
        const startDate = new Date(year, month - 1, 1); // month is 0-indexed
        const endDate = new Date(year, month, 0, 23, 59, 59); // Last day of month

        return this.get(`/kpis/${kpiId}/values`, {
            start_date: startDate.toISOString(),
            end_date: endDate.toISOString(),
            ...additionalParams
        });
    }

    async getLatestKPIValue(kpiId) {
        return this.get(`/kpis/${kpiId}/values/latest`);
    }

    async getKPIValuesAggregated(kpiId, period = 'day', params = {}) {
        return this.get(`/kpis/${kpiId}/values/aggregated`, { period, ...params });
    }

    async createKPIValue(kpiId, valueData) {
        return this.post(`/kpis/${kpiId}/values`, valueData);
    }

    async bulkCreateKPIValues(kpiId, bulkData) {
        return this.post(`/kpis/${kpiId}/values/bulk`, bulkData);
    }

    // Legacy KPI endpoint for backward compatibility
    async getKPIValuesByCity(cityCode, kpiDbId) {
        return this.get(`/kpis/city/${cityCode.toLowerCase()}/kpi/${kpiDbId}`);
    }

    // DASHBOARD API METHODS
    
    async getDashboards(cityId, params = {}) {
        return this.get('/dashboards', { city_id: cityId, ...params });
    }

    async getDashboardById(dashboardId) {
        return this.get(`/dashboards/${dashboardId}`);
    }

    async getDashboardByCity(cityCode) {
        return this.get(`/dashboards/city/${cityCode.toLowerCase()}`);
    }

    async getDashboardWithVisualizations(dashboardId) {
        return this.get(`/dashboards/${dashboardId}/with-visualizations`);
    }

    async createDashboard(dashboardData) {
        return this.post('/dashboards', dashboardData);
    }

    async updateDashboard(dashboardId, dashboardData) {
        return this.put(`/dashboards/${dashboardId}`, dashboardData);
    }

    async deleteDashboard(dashboardId) {
        return this.delete(`/dashboards/${dashboardId}`);
    }

    // DASHBOARD SECTION API METHODS
    
    async getDashboardSections(dashboardId) {
        return this.get(`/dashboards/${dashboardId}/sections`);
    }

    async createDashboardSection(dashboardId, sectionData) {
        return this.post(`/dashboards/${dashboardId}/sections`, sectionData);
    }

    async updateDashboardSection(sectionId, sectionData) {
        return this.put(`/dashboards/sections/${sectionId}`, sectionData);
    }

    async deleteDashboardSection(sectionId) {
        return this.delete(`/dashboards/sections/${sectionId}`);
    }

    async reorderDashboardSections(dashboardId, sectionIds) {
        return this.put(`/dashboards/${dashboardId}/sections/reorder`, sectionIds);
    }

    async duplicateDashboardSection(sectionId, newName) {
        return this.post(`/dashboards/sections/${sectionId}/duplicate?new_name=${encodeURIComponent(newName)}`);
    }

    // VISUALIZATION API METHODS
    
    async getDashboardVisualizations(dashboardId) {
        return this.get(`/dashboards/${dashboardId}/visualizations`);
    }

    async createVisualization(dashboardId, visualizationData) {
        return this.post(`/dashboards/${dashboardId}/visualizations`, visualizationData);
    }

    async getVisualizationById(visId) {
        return this.get(`/dashboards/visualizations/${visId}`);
    }

    async updateVisualization(visId, visualizationData) {
        return this.put(`/dashboards/visualizations/${visId}`, visualizationData);
    }

    async deleteVisualization(visId) {
        return this.delete(`/dashboards/visualizations/${visId}`);
    }

    async deleteMultipleVisualizations(visIds) {
        // Backend expects query parameters: DELETE /dashboards/visualizations/bulk?ids=1&ids=2&ids=3
        const queryParams = visIds.map(id => `ids=${id}`).join('&');
        return this.delete(`/dashboards/visualizations/bulk?${queryParams}`);
    }

    // Legacy visualization endpoint for backward compatibility
    async getVisualizationsByCity(cityCode) {
        return this.get(`/visualizations/city/${cityCode.toLowerCase()}`);
    }

    // AUTHENTICATION API METHODS
    
    async login(username, password) {
        return this.post('/auth/token', { username, password });
    }

    async refreshToken(refreshToken) {
        return this.post('/auth/refresh', { refresh_token: refreshToken });
    }

    async getProfile() {
        return this.get('/auth/profile');
    }

    // UTILITY METHODS

    // Helper method to handle different chart types in the old format
    mapVisualizationType(newType) {
        const typeMap = {
            'linechart': 'LineChart',
            'barchart': 'BarChart', 
            'piechart': 'PieChart',
            'statchart': 'StatChart',
            'table': 'Table',
            'map': 'Map',
            'freetextfield': 'FreeTextField',
            'timeline': 'Timeline'
        };
        return typeMap[newType] || 'LineChart';
    }

    // Helper method to convert chart types to API format
    mapChartTypeToApi(chartType) {
        const typeMap = {
            'LineChart': 'linechart',
            'BarChart': 'barchart',
            'PieChart': 'piechart', 
            'StatChart': 'statchart',
            'Table': 'table',
            'Map': 'map',
            'FreeTextField': 'freetextfield',
            'Timeline': 'timeline'
        };
        return typeMap[chartType] || 'linechart';
    }

    // Migration helper - converts old visualization format to new format
    convertLegacyVisualization(oldVis, sectionId = null) {
        return {
            type: this.mapChartTypeToApi(oldVis.chartType || oldVis.chart),
            title: oldVis.title,
            width: parseInt(oldVis.width) || 4,
            height: parseInt(oldVis.height) || 8,
            x_position: parseInt(oldVis.xposition) || 0,
            y_position: parseInt(oldVis.yposition) || 0,
            i: oldVis.i || oldVis.id?.toString(),
            section_id: sectionId,
            kpi_id: oldVis.kpi_id || oldVis.tableId,
            // Chart-specific properties
            ...(oldVis.xtitle && { x_title: oldVis.xtitle }),
            ...(oldVis.ytitle && { y_title: oldVis.ytitle }),
            ...(oldVis.color && { color: oldVis.color }),
            ...(oldVis.unit && { unit: oldVis.unit }),
            ...(oldVis.target !== undefined && { target: oldVis.target })
        };
    }

    // Migration helper - converts new visualization to old format (for backward compatibility)
    convertToLegacyFormat(newVis, sectionName = 'Section 1') {
        return {
            id: newVis.id,
            i: newVis.i,
            chartType: this.mapVisualizationType(newVis.type),
            title: newVis.title,
            section: sectionName, // Use section name for backward compatibility
            width: newVis.width,
            height: newVis.height,
            xposition: newVis.x_position,
            yposition: newVis.y_position,
            kpi_id: newVis.kpi_id,
            tableId: newVis.kpi_id, // For backward compatibility
            // Chart-specific properties
            xtitle: newVis.x_title,
            ytitle: newVis.y_title,
            color: newVis.color,
            unit: newVis.unit,
            target: newVis.target
        };
    }

    // Batch operations for better performance
    async batchCreateVisualizations(dashboardId, visualizations) {
        const promises = visualizations.map(vis => 
            this.createVisualization(dashboardId, vis)
        );
        return Promise.all(promises);
    }

    async batchUpdateKPIValues(updates) {
        const promises = updates.map(update => 
            this.bulkCreateKPIValues(update.kpiId, update.data)
        );
        return Promise.all(promises);
    }

    // Health check
    async healthCheck() {
        return this.get('/health');
    }

    // Get API information
    async getApiInfo() {
        return this.get('/');
    }
}

// Create singleton instance
const apiService = new ApiService();

// Export for use in Vue components
export default apiService;

// Also export the class for testing or multiple instances
export { ApiService };