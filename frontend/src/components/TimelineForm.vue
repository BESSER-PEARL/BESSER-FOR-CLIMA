<template>
  <div class="timeline-form-modal" v-if="show">
    <div class="modal-backdrop" @click="$emit('close')"></div>
    <div class="modal-content">
      <div class="modal-header">
        <h2>{{ isEdit ? 'Edit Timeline' : 'Create Timeline' }}</h2>
        <button class="close-btn" @click="$emit('close')">
          <i class="fas fa-times"></i>
        </button>
      </div>
      
      <div class="modal-body">
        <div class="form-group">
          <label>Timeline Description</label>
          <textarea 
            v-model="localTimeline.description" 
            placeholder="Overall description of the solution implementation timeline..."
            rows="3"
          ></textarea>
        </div>
        
        <div class="events-section">
          <div class="section-header">
            <h3>Timeline Events</h3>
            <button @click="addEvent" class="btn-primary">
              <i class="fas fa-plus"></i> Add Event
            </button>
          </div>
          
          <div v-if="localTimeline.events.length === 0" class="no-events">
            <p>No events yet. Click "Add Event" to start building your timeline.</p>
          </div>
          
          <div 
            v-for="(event, index) in localTimeline.events" 
            :key="index"
            class="event-card"
            :class="{ 'expanded': expandedEvent === index }"
          >
            <div class="event-card-header" @click="toggleEvent(index)">
              <div class="event-summary">
                <span class="event-number">#{{ index + 1 }}</span>
                <span class="event-title-preview">{{ event.title || 'Untitled Event' }}</span>
                <span class="event-phase-preview" :style="{ backgroundColor: event.color }">
                  {{ event.phase || 'No Phase' }}
                </span>
              </div>
              <div class="event-actions">
                <button 
                  type="button"
                  @click.stop="removeEvent(index)" 
                  class="btn-delete"
                  title="Delete event"
                >
                  <i class="fas fa-trash"></i>
                </button>
                <i class="fas" :class="expandedEvent === index ? 'fa-chevron-up' : 'fa-chevron-down'"></i>
              </div>
            </div>
            
            <div v-show="expandedEvent === index" class="event-card-body">
              <div class="form-row">
                <div class="form-group flex-2">
                  <label>Event Title *</label>
                  <input 
                    v-model="event.title" 
                    type="text" 
                    placeholder="e.g., Planning Phase"
                    required
                  />
                </div>
                <div class="form-group flex-1">
                  <label>Phase *</label>
                  <select v-model="event.phase" required>
                    <option value="">Select Phase</option>
                    <option value="planning">Planning</option>
                    <option value="implementation">Implementation</option>
                    <option value="scale-up">Scale-up</option>
                    <option value="post-project">Post-Project</option>
                    <option value="completed">Completed</option>
                    <option value="discontinued">Discontinued</option>
                  </select>
                </div>
              </div>
              
              <div class="form-group">
                <label>Description</label>
                <textarea 
                  v-model="event.description" 
                  placeholder="Describe this phase of the project..."
                  rows="3"
                ></textarea>
              </div>
              
              <div class="form-row">
                <div class="form-group">
                  <label>Start Date *</label>
                  <input 
                    v-model="event.start_date" 
                    type="date" 
                    required
                  />
                </div>
                <div class="form-group">
                  <label>End Date</label>
                  <input 
                    v-model="event.end_date" 
                    type="date"
                    :disabled="event.is_ongoing"
                  />
                  <div class="checkbox-group">
                    <input 
                      type="checkbox" 
                      :id="'ongoing-' + index"
                      v-model="event.is_ongoing"
                      @change="handleOngoingChange(event)"
                    />
                    <label :for="'ongoing-' + index">Ongoing</label>
                  </div>
                </div>
              </div>
              
              <div class="form-row">
                <div class="form-group">
                  <label>Status *</label>
                  <select v-model="event.status" required>
                    <option value="active">Active</option>
                    <option value="completed">Completed</option>
                    <option value="failed">Failed/Discontinued</option>
                  </select>
                </div>
                <div class="form-group">
                  <label>Color</label>
                  <div class="color-picker">
                    <input 
                      v-model="event.color" 
                      type="color"
                    />
                    <input 
                      v-model="event.color" 
                      type="text" 
                      placeholder="#0177a9"
                      pattern="^#[0-9A-Fa-f]{6}$"
                    />
                  </div>
                </div>
              </div>
              
              <div class="form-group">
                <label>KPI References (Select KPIs related to this phase)</label>
                <div class="kpi-selector">
                  <div 
                    v-for="kpi in availableKPIs" 
                    :key="kpi.id"
                    class="kpi-checkbox"
                  >
                    <input 
                      type="checkbox" 
                      :id="'kpi-' + index + '-' + kpi.id"
                      :value="kpi.id"
                      v-model="event.selectedKPIs"
                      @change="updateKPIReferences(event)"
                    />
                    <label :for="'kpi-' + index + '-' + kpi.id">
                      {{ kpi.name }} ({{ kpi.unit }})
                    </label>
                  </div>
                </div>
              </div>
              
              <div v-if="event.status === 'failed'" class="form-group failure-section">
                <label>Discontinuation Reason *</label>
                <textarea 
                  v-model="event.failure_reason" 
                  placeholder="Explain why this solution was discontinued or did not succeed..."
                  rows="4"
                  required
                ></textarea>
                <p class="help-text">
                  Please provide a detailed explanation including which KPIs were not met and why.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div class="modal-footer">
        <button @click="$emit('close')" class="btn-secondary">Cancel</button>
        <button @click="saveTimeline" class="btn-primary" :disabled="!isValid">
          Save Timeline
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue';

const props = defineProps({
  show: {
    type: Boolean,
    default: false
  },
  timeline: {
    type: Object,
    default: () => ({
      description: '',
      events: []
    })
  },
  availableKPIs: {
    type: Array,
    default: () => []
  },
  isEdit: {
    type: Boolean,
    default: false
  }
});

const emit = defineEmits(['close', 'save']);

const expandedEvent = ref(0);
const localTimeline = ref({
  description: '',
  events: []
});

// Initialize with props data
watch(() => props.show, (newVal) => {
  if (newVal) {
    localTimeline.value = {
      description: props.timeline?.description || '',
      events: props.timeline?.events?.length > 0 
        ? props.timeline.events.map(e => ({
            ...e,
            selectedKPIs: parseKPIReferences(e.kpi_references),
            start_date: formatDateForInput(e.start_date),
            end_date: formatDateForInput(e.end_date)
          }))
        : []
    };
    if (localTimeline.value.events.length > 0) {
      expandedEvent.value = 0;
    }
  }
}, { immediate: true });

const isValid = computed(() => {
  // Allow saving timeline with description only (no events required)
  if (localTimeline.value.events.length === 0) return true;
  
  // If there are events, validate them
  return localTimeline.value.events.every(event => {
    const hasRequired = event.title && event.phase && event.start_date && event.status;
    const hasEndDateOrOngoing = event.is_ongoing || event.end_date;
    const hasFailureReason = event.status !== 'failed' || event.failure_reason;
    
    return hasRequired && hasEndDateOrOngoing && hasFailureReason;
  });
});

const toggleEvent = (index) => {
  expandedEvent.value = expandedEvent.value === index ? -1 : index;
};

const addEvent = () => {
  localTimeline.value.events.push({
    title: '',
    description: '',
    phase: '',
    start_date: '',
    end_date: '',
    is_ongoing: false,
    status: 'active',
    kpi_references: '[]',
    selectedKPIs: [],
    failure_reason: '',
    color: '#0177a9'
  });
  expandedEvent.value = localTimeline.value.events.length - 1;
};

const removeEvent = (index) => {
  if (confirm('Are you sure you want to delete this event?')) {
    localTimeline.value.events.splice(index, 1);
    if (expandedEvent.value >= localTimeline.value.events.length) {
      expandedEvent.value = localTimeline.value.events.length - 1;
    }
  }
};

const updateKPIReferences = (event) => {
  event.kpi_references = JSON.stringify(event.selectedKPIs);
};

const handleOngoingChange = (event) => {
  if (event.is_ongoing) {
    event.end_date = null;
  }
};

const parseKPIReferences = (kpiRefs) => {
  if (!kpiRefs) return [];
  try {
    return JSON.parse(kpiRefs);
  } catch {
    return [];
  }
};

const formatDateForInput = (dateString) => {
  if (!dateString) return '';
  const date = new Date(dateString);
  return date.toISOString().split('T')[0];
};

const saveTimeline = () => {
  if (!isValid.value) {
    // Find which events are invalid
    const invalidEvents = localTimeline.value.events
      .map((event, index) => {
        const hasRequired = event.title && event.phase && event.start_date && event.status;
        const hasEndDateOrOngoing = event.is_ongoing || event.end_date;
        const hasFailureReason = event.status !== 'failed' || event.failure_reason;
        
        if (!hasRequired) return `Event #${index + 1}: Missing required fields (title, phase, start date, or status)`;
        if (!hasEndDateOrOngoing) return `Event #${index + 1}: Must have end date or mark as ongoing`;
        if (!hasFailureReason) return `Event #${index + 1}: Failed status requires failure reason`;
        return null;
      })
      .filter(msg => msg !== null);
    
    alert('Please fix the following issues:\n\n' + invalidEvents.join('\n'));
    return;
  }
  
  // Format dates to ISO strings before saving
  const formattedTimeline = {
    ...localTimeline.value,
    events: localTimeline.value.events.map(event => ({
      ...event,
      start_date: event.start_date ? new Date(event.start_date).toISOString() : null,
      end_date: event.end_date && !event.is_ongoing ? new Date(event.end_date).toISOString() : null
    }))
  };
  
  emit('save', formattedTimeline);
};
</script>

<style scoped>
.timeline-form-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 10000;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-backdrop {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
}

.modal-content {
  position: relative;
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 900px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  animation: slideUp 0.3s ease-out;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px 30px;
  border-bottom: 2px solid #e0e0e0;
}

.modal-header h2 {
  margin: 0;
  color: #2c3e50;
  font-size: 1.8em;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5em;
  color: #7f8c8d;
  cursor: pointer;
  padding: 5px 10px;
  transition: color 0.2s;
}

.close-btn:hover {
  color: #e74c3c;
}

.modal-body {
  padding: 30px;
  overflow-y: auto;
  flex: 1;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  color: #2c3e50;
  font-weight: 600;
  font-size: 0.95em;
}

.form-group input[type="text"],
.form-group input[type="date"],
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 10px 12px;
  border: 2px solid #e0e0e0;
  border-radius: 6px;
  font-size: 0.95em;
  transition: border-color 0.2s;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #0177a9;
}

.form-group textarea {
  resize: vertical;
  font-family: inherit;
}

.form-row {
  display: flex;
  gap: 20px;
}

.form-row .form-group {
  flex: 1;
}

.form-row .form-group.flex-2 {
  flex: 2;
}

.form-row .form-group.flex-1 {
  flex: 1;
}

.checkbox-group {
  margin-top: 8px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.checkbox-group input[type="checkbox"] {
  width: auto;
}

.checkbox-group label {
  margin: 0;
  font-weight: normal;
  cursor: pointer;
}

.color-picker {
  display: flex;
  gap: 10px;
  align-items: center;
}

.color-picker input[type="color"] {
  width: 60px;
  height: 40px;
  border: 2px solid #e0e0e0;
  border-radius: 6px;
  cursor: pointer;
}

.color-picker input[type="text"] {
  flex: 1;
}

.events-section {
  margin-top: 30px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header h3 {
  margin: 0;
  color: #2c3e50;
  font-size: 1.3em;
}

.no-events {
  text-align: center;
  padding: 40px 20px;
  color: #7f8c8d;
  background: #f8f9fa;
  border-radius: 8px;
}

.event-card {
  background: #f8f9fa;
  border-radius: 8px;
  margin-bottom: 15px;
  overflow: hidden;
  border: 2px solid #e0e0e0;
  transition: border-color 0.2s;
}

.event-card.expanded {
  border-color: #0177a9;
}

.event-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  cursor: pointer;
  background: white;
  transition: background 0.2s;
}

.event-card-header:hover {
  background: #f8f9fa;
}

.event-summary {
  display: flex;
  align-items: center;
  gap: 15px;
  flex: 1;
}

.event-number {
  background: #0177a9;
  color: white;
  padding: 4px 10px;
  border-radius: 4px;
  font-weight: bold;
  font-size: 0.9em;
}

.event-title-preview {
  font-weight: 600;
  color: #2c3e50;
  flex: 1;
}

.event-phase-preview {
  padding: 4px 12px;
  border-radius: 12px;
  color: white;
  font-size: 0.85em;
  font-weight: bold;
  text-transform: uppercase;
}

.event-actions {
  display: flex;
  align-items: center;
  gap: 15px;
}

.btn-delete {
  background: none;
  border: none;
  color: #e74c3c;
  cursor: pointer;
  padding: 5px 10px;
  font-size: 1em;
  transition: color 0.2s;
}

.btn-delete:hover {
  color: #c0392b;
}

.event-card-body {
  padding: 20px;
  border-top: 1px solid #e0e0e0;
  animation: fadeIn 0.3s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.kpi-selector {
  border: 2px solid #e0e0e0;
  border-radius: 6px;
  padding: 15px;
  max-height: 200px;
  overflow-y: auto;
  background: white;
}

.kpi-checkbox {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px;
  border-radius: 4px;
  transition: background 0.2s;
}

.kpi-checkbox:hover {
  background: #f8f9fa;
}

.kpi-checkbox input[type="checkbox"] {
  width: auto;
}

.kpi-checkbox label {
  margin: 0;
  font-weight: normal;
  cursor: pointer;
  flex: 1;
}

.failure-section {
  background: #fef5f5;
  padding: 20px;
  border-radius: 8px;
  border-left: 4px solid #e74c3c;
}

.help-text {
  margin: 10px 0 0 0;
  color: #7f8c8d;
  font-size: 0.85em;
  font-style: italic;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 15px;
  padding: 20px 30px;
  border-top: 2px solid #e0e0e0;
  background: #f8f9fa;
}

.btn-primary,
.btn-secondary {
  padding: 10px 24px;
  border: none;
  border-radius: 6px;
  font-size: 0.95em;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-primary {
  background: #0177a9;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #015a85;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(1, 119, 169, 0.3);
}

.btn-primary:disabled {
  background: #95a5a6;
  cursor: not-allowed;
}

.btn-secondary {
  background: #e0e0e0;
  color: #2c3e50;
}

.btn-secondary:hover {
  background: #bdc3c7;
}

/* Scrollbar styling */
.modal-body::-webkit-scrollbar,
.kpi-selector::-webkit-scrollbar {
  width: 8px;
}

.modal-body::-webkit-scrollbar-track,
.kpi-selector::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.modal-body::-webkit-scrollbar-thumb,
.kpi-selector::-webkit-scrollbar-thumb {
  background: #0177a9;
  border-radius: 4px;
}

.modal-body::-webkit-scrollbar-thumb:hover,
.kpi-selector::-webkit-scrollbar-thumb:hover {
  background: #015a85;
}
</style>
