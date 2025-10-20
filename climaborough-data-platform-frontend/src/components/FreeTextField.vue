<template>
  <div class="free-text-field">
    <div v-if="!canEdit" class="free-text-content">{{ text || 'No content yet' }}</div>
    <textarea 
      v-else
      v-model="text" 
      placeholder="Enter description or notes here..." 
      class="free-text-input"
    />
  </div>
</template>

<script setup>
import { ref, watch, onMounted, computed } from 'vue';

const props = defineProps({
  id: { type: [String, Number], required: false },
  initialText: { type: String, default: '' },
  canEdit: { type: Boolean, default: false },
  sectionId: { type: [String, Number], required: false },
  dashboardId: { type: [String, Number], required: false },
  // Support for attributes object (used in edit mode)
  attributes: { type: Object, default: () => ({}) }
});

// Use computed to create a two-way binding with attributes.text
const text = computed({
  get() {
    return props.attributes?.text ?? props.initialText ?? '';
  },
  set(value) {
    if (props.attributes) {
      // Directly mutate the attributes object (it's reactive in the parent)
      props.attributes.text = value;
    }
  }
});

// watch(() => props.attributes?.text, (val) => {
//   console.log('FreeTextField: text changed to:', val);
// });

onMounted(() => {
  // console.log('FreeTextField mounted with text:', props.attributes?.text);
});
</script>

<style scoped>
.free-text-field {
  display: flex;
  flex-direction: column;
  height: 100%;
  width: 100%;
  padding: 8px;
}

.free-text-input {
  min-height: 100px;
  height: 100%;
  resize: none;
  width: 100%;
  font-size: 0.95rem;
  padding: 12px;
  border-radius: 6px;
  border: 1px solid #ccc;
  font-family: inherit;
  line-height: 1.5;
}

.free-text-input:focus {
  outline: none;
  border-color: #0177a9;
  box-shadow: 0 0 0 2px rgba(1, 119, 169, 0.1);
}

.free-text-content {
  white-space: pre-wrap;
  padding: 12px;
  background: #f9f9f9;
  border-radius: 6px;
  border: 1px solid #eee;
  height: 100%;
  overflow-y: auto;
  font-size: 0.95rem;
  line-height: 1.5;
  color: #333;
}
</style>
