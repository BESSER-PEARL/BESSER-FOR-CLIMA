<template>
  <div class="timeline-container">
    <div class="timeline-header">
      <h3 v-if="!isEditMode">{{ props.title }}</h3>
      <input 
        v-else 
        v-model="localTitle" 
        class="timeline-title-input" 
        placeholder="Timeline Title"
        @blur="updateTitle"
      />
      <p v-if="attributes.description" class="timeline-description">{{ attributes.description }}</p>
    </div>
    
    <div class="timeline-content" v-if="events.length > 0">
      <div class="timeline-line"></div>
      <div 
        v-for="(event, index) in sortedEvents" 
        :key="event.id || index"
        class="timeline-event"
        :class="{ 'ongoing': event.is_ongoing, 'failed': event.status === 'failed' }"
      >
        <div class="timeline-marker" :style="{ backgroundColor: event.color }"></div>
        <div class="timeline-event-content">
          <div class="event-header">
            <span class="event-phase-badge" :style="{ backgroundColor: event.color }">
              {{ event.phase }}
            </span>
            <span class="event-status" :class="event.status">{{ event.status }}</span>
          </div>
          <h4 class="event-title">{{ event.title }}</h4>
          <p class="event-dates">
            <span>{{ formatDate(event.start_date) }}</span>
            <span v-if="event.end_date"> - {{ formatDate(event.end_date) }}</span>
            <span v-else-if="event.is_ongoing" class="ongoing-badge">Ongoing</span>
          </p>
          <p v-if="event.description" class="event-description">{{ event.description }}</p>
          
          <div v-if="event.kpi_references" class="event-kpis">
            <strong>Referenced KPIs:</strong>
            <span class="kpi-tag" v-for="kpiId in parseKPIReferences(event.kpi_references)" :key="kpiId">
              KPI #{{ kpiId }}
            </span>
          </div>
          
          <div v-if="event.failure_reason && event.status === 'failed'" class="failure-reason">
            <strong>Discontinuation Reason:</strong>
            <p>{{ event.failure_reason }}</p>
          </div>
        </div>
      </div>
    </div>
    
    <div v-else class="timeline-empty">
      <p>No timeline events yet</p>
      <button v-if="isEditMode" @click="$emit('edit')" class="add-event-btn">
        Add Timeline Events
      </button>
    </div>
    
    <button v-if="isEditMode && events.length > 0" @click="$emit('edit')" class="edit-timeline-btn">
      <i class="fas fa-edit"></i> Edit Timeline
    </button>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue';

const props = defineProps({
  title: {
    type: String,
    default: 'Project Timeline'
  },
  attributes: {
    type: Object,
    default: () => ({
      description: '',
      events: []
    })
  },
  isEditMode: {
    type: Boolean,
    default: false
  }
});

const emit = defineEmits(['update:title', 'edit']);

const localTitle = ref(props.title);

const events = computed(() => props.attributes?.events || []);

const sortedEvents = computed(() => {
  return [...events.value].sort((a, b) => 
    new Date(a.start_date) - new Date(b.start_date)
  );
});

const updateTitle = () => {
  emit('update:title', localTitle.value);
};

const formatDate = (dateString) => {
  if (!dateString) return '';
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', { 
    year: 'numeric', 
    month: 'short', 
    day: 'numeric' 
  });
};

const parseKPIReferences = (kpiRefs) => {
  try {
    return JSON.parse(kpiRefs);
  } catch {
    return [];
  }
};
</script>

<style scoped>
.timeline-container {
  padding: 12px;
  background: white;
  border-radius: 8px;
  height: 100%;
  overflow-y: auto;
}

.timeline-header {
  margin-bottom: 16px;
}

.timeline-header h3 {
  margin: 0 0 6px 0;
  color: #2c3e50;
  font-size: 1.1em;
}

.timeline-title-input {
  width: 100%;
  padding: 6px 10px;
  font-size: 1.1em;
  border: 2px solid #e0e0e0;
  border-radius: 4px;
  font-weight: bold;
  margin-bottom: 6px;
}

.timeline-description {
  color: #7f8c8d;
  margin: 0;
  font-size: 0.85em;
}

.timeline-content {
  position: relative;
  padding-left: 28px;
}

.timeline-line {
  position: absolute;
  left: 12px;
  top: 0;
  bottom: 0;
  width: 2px;
  background: linear-gradient(to bottom, #0177a9, #95a5a6);
}

.timeline-event {
  position: relative;
  margin-bottom: 24px;
  animation: fadeInUp 0.5s ease-out;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.timeline-marker {
  position: absolute;
  left: -23px;
  top: 5px;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  border: 3px solid white;
  box-shadow: 0 0 0 3px #e0e0e0;
  z-index: 2;
}

.timeline-event.ongoing .timeline-marker {
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
    box-shadow: 0 0 0 3px #e0e0e0;
  }
  50% {
    transform: scale(1.2);
    box-shadow: 0 0 0 6px rgba(1, 119, 169, 0.3);
  }
}

.timeline-event-content {
  background: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
  border-left: 4px solid #0177a9;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  transition: transform 0.2s, box-shadow 0.2s;
}

.timeline-event-content:hover {
  transform: translateX(5px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.15);
}

.timeline-event.failed .timeline-event-content {
  border-left-color: #e74c3c;
  background: #fef5f5;
}

.event-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.event-phase-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 12px;
  color: white;
  font-size: 0.85em;
  font-weight: bold;
  text-transform: uppercase;
}

.event-status {
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 0.8em;
  font-weight: 600;
  text-transform: uppercase;
}

.event-status.active {
  background: #d4edda;
  color: #155724;
}

.event-status.completed {
  background: #cce5ff;
  color: #004085;
}

.event-status.failed {
  background: #f8d7da;
  color: #721c24;
}

.event-title {
  margin: 6px 0;
  color: #2c3e50;
  font-size: 1em;
  font-weight: 600;
}

.event-dates {
  color: #7f8c8d;
  font-size: 0.8em;
  margin: 6px 0;
  display: flex;
  align-items: center;
  gap: 6px;
}

.ongoing-badge {
  background: #fff3cd;
  color: #856404;
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 0.8em;
  font-weight: 600;
}

.event-description {
  margin: 10px 0;
  color: #34495e;
  line-height: 1.5;
  font-size: 0.9em;
}

.event-kpis {
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px solid #e0e0e0;
}

.event-kpis strong {
  color: #2c3e50;
  display: block;
  margin-bottom: 6px;
  font-size: 0.85em;
}

.kpi-tag {
  display: inline-block;
  background: #0177a9;
  color: white;
  padding: 3px 8px;
  border-radius: 3px;
  font-size: 0.75em;
  margin-right: 6px;
  margin-bottom: 4px;
}

.failure-reason {
  margin-top: 10px;
  padding: 10px;
  background: #fff;
  border-left: 3px solid #e74c3c;
  border-radius: 4px;
}

.failure-reason strong {
  color: #e74c3c;
  display: block;
  margin-bottom: 6px;
  font-size: 0.85em;
}

.failure-reason p {
  margin: 0;
  color: #34495e;
  line-height: 1.5;
  font-size: 0.9em;
}

.timeline-empty {
  text-align: center;
  padding: 40px 20px;
  color: #7f8c8d;
}

.timeline-empty p {
  font-size: 0.95em;
  margin-bottom: 16px;
}

.add-event-btn, .edit-timeline-btn {
  background: #0177a9;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 5px;
  cursor: pointer;
  font-size: 0.85em;
  font-weight: 600;
  transition: background 0.3s;
}

.add-event-btn:hover, .edit-timeline-btn:hover {
  background: #015a85;
}

.edit-timeline-btn {
  width: 100%;
  margin-top: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}

/* Scrollbar styling */
.timeline-container::-webkit-scrollbar {
  width: 8px;
}

.timeline-container::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.timeline-container::-webkit-scrollbar-thumb {
  background: #0177a9;
  border-radius: 4px;
}

.timeline-container::-webkit-scrollbar-thumb:hover {
  background: #015a85;
}
</style>
