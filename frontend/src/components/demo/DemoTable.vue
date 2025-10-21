<script setup>
import { get } from 'plotly.js-dist';
import { ref, defineProps, watch, computed } from 'vue';

const props = defineProps({
    tableId: {
        type: Number,
        required: true
    },
    city: {
        type: String,
        required: true
    },
    title: {
        type: String,
        default: "Title"
    },
    columns: {
        type: Array,
        default: []
    }
});

const items = ref([]);
const timestamps = ref([]);
const alert = ref(false);

const headers = ref([
    { title: 'ID', key: 'id' },
    { title: 'Timestamp', key: 'Timestamp' },
    { title: 'Value', key: 'Value' },
    { title: 'Status', key: 'Status' },
]);

const formatDate = (dateString) => {
    const date = new Date(dateString);
    const day = String(date.getDate()).padStart(2, '0');
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const year = date.getFullYear();
    return `${day}/${month}/${year}`;
};

const lastTimestamp = computed(() => {
    if (timestamps.value.length > 0) {
        const lastTimestamp = timestamps.value[timestamps.value.length - 1];
        return formatDate(lastTimestamp);
    }
    return 'No updates available';
});

const toggleAlert = () => {
    alert.value = !alert.value;
};

async function getItems() {
    try {
        items.value = [];
        timestamps.value = [];
        
        const mockData = Array.from({ length: 10 }, (_, i) => ({
            id: i + 1,
            Timestamp: new Date(Date.now() - i * 24 * 60 * 60 * 1000).toISOString(),
            Value: Math.floor(Math.random() * 900) + 100,
            Status: ['Active', 'Pending', 'Complete'][Math.floor(Math.random() * 3)]
        }));

        mockData.sort((a, b) => new Date(b.Timestamp) - new Date(a.Timestamp));

        if (props.columns && props.columns.length > 0) {
            items.value = mockData.map(obj => {
                const newObj = {};
                props.columns.forEach(key => {
                    if (obj.hasOwnProperty(key)) {
                        newObj[key] = key === 'Timestamp' ? formatDate(obj[key]) : obj[key];
                    }
                });
                return newObj;
            });
            
            timestamps.value = mockData
                .map(item => item.Timestamp)
                .filter(Boolean);
        } else {
            items.value = mockData.map(item => ({
                ...item,
                Timestamp: formatDate(item.Timestamp)
            }));
            timestamps.value = mockData.map(item => item.Timestamp);
        }

    } catch (error) {
        console.error('Error in getItems:', error);
        window.alert('Error generating mock data: ' + error.message);
    }
}

// Initialize data
getItems();

// Watch for changes
watch(() => props.columns, (newColumns) => {
    if (newColumns && newColumns.length > 0) {
        headers.value = newColumns.map(col => ({
            title: col,
            key: col
        }));
    }
    getItems();
}, { immediate: true });

</script>

<template>
    <div>
        <div class="table">
            <h1>{{ title }}</h1>
            <v-data-table
                :headers="headers"
                :items="items"
                :items-per-page="5"
                class="elevation-1"
            ></v-data-table>
        </div>
        <div class="update">
            Last Update: {{ lastTimestamp }}
            <Icon v-if="alert" icon="mdi:bell" width="20" height="20" @click="toggleAlert"
                style="margin-left: 5px;color: red" />
            <Icon v-else icon="mdi:bell-outline" width="20" height="20" @click="toggleAlert"
                style="margin-left: 5px;color: black" />
        </div>
    </div>
</template>

<style lang="scss" scoped>
.table {
    height: 100%
}

.update {
    display: flex;
    /* Add flex display */
    justify-content: flex-end;
    /* Align items to the right */
    align-items: center;
    /* Center items vertically */
    flex-shrink: 0;
    /* Prevents the update element from shrinking */
    padding: 5px;
}
</style>