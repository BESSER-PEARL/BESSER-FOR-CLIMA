<script setup>
import { ref, defineEmits, inject } from 'vue';

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

// Function to sort KPIs based on chart type using has_category_label
const sortKPIsForChart = (kpis, chartType) => {
    const isBarOrPieChart = chartType.toLowerCase() === 'barchart' || chartType.toLowerCase() === 'piechart';

    return kpis.sort((a, b) => {
        if (isBarOrPieChart) {
          //console.log("Sorting for Bar/Pie chart");
          //console.log("KPI A:", a);
          //console.log("KPI B:", b);
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
        let recommendation = '';

        if (isBarOrPieChart) {
            if (hasCategoryLabel) {
                recommendation = ' ✅ (Recommended)';
            } else {
                recommendation = ' ⚠️ (Not recommended - no category label)';
            }
        } else {
            if (!hasCategoryLabel) {
                recommendation = ' ✅ (Recommended)';
            } else {
                recommendation = ' ⚠️ (Better for Bar/Pie charts)';
            }
        }

        return {
            ...kpi,
            displayName: kpi.name + recommendation
        };
    });
}

async function getItem(){
    try{
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
    }
}
getItem()


const createVisualisation = () => {    
    emit('createVisualisation', table.value.id, table.value.name, props.chart, table.value)
}

</script>

<template>
  <div class="popup">
    <div class="popup-inner">
      <label style="padding:5px" for="data-source-select">Select the data you want to display</label>
        <v-select
        v-model="table"
        :items="items"
        item-title="displayName"
        item-value="id"
        density="comfortable"
        :label="label"
        style="margin-top:10px"
        :menu="true"
        return-object
      ></v-select>
        <p v-if="error" style="color: red;"> Please choose a value! </p>
      <v-btn class="popup-button" @click="$emit('cancel')">Cancel</v-btn>
      <v-btn class="popup-button" @click="createVisualisation">Add Element</v-btn>
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
  z-index: 99;
  background-color: rgba(0, 0, 0, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;

  .popup-inner {
    background: #ffffff;
    padding: 50px;
  }

  #label {
    font-weight: bold;
  }
  
  .label {
    font-weight: bold;
    margin-bottom: 5px;
  }

  #inputField {
    border: 3px solid #555;
    padding: 8px;
    font-size: 14px;
    display: flex;
  }

  .popup-button {
    margin: 5px; 
  }

}



</style>