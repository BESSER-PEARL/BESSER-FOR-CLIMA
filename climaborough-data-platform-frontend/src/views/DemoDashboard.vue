<script setup>
import { ref, reactive, computed, onMounted, onBeforeUnmount } from 'vue';
import { GridLayout, GridItem } from 'grid-layout-plus'
import { useRoute } from 'vue-router';


// Remove this line:
// import KPIForm from '../components/KPIForm.vue'
import LineChartForm from '../components/demo/forms/DemoLineChartForm.vue'
import PieChartForm from '../components/demo/forms/DemoPieChartForm.vue'
import BarChartForm from '../components/demo/forms/DemoBarChartForm.vue'
import StatChartForm from '../components/demo/forms/DemoStatChartForm.vue'
import TableForm from '../components/demo/forms/DemoTableForm.vue'

import LineChart from '../components/demo/DemoLineChart.vue'
import PieChart from '../components/demo/DemoPieChart.vue'
import BarChart from '../components/demo/DemoBarChart.vue'
import StatChart from '../components/demo/DemoStatChart.vue'
import Table from '../components/demo/DemoTable.vue'
import Map from '../components/demo/DemoMap.vue'
import { uid } from "uid"

import { throttle } from '@vexip-ui/utils'

import html2canvas from 'html2canvas';
import jsPDF from 'jspdf';
import { to } from 'plotly.js-dist';
import DashboardChat from '../components/DashboardChat.vue';
import GaugeChart from '../components/demo/GaugeChart.vue'
import GaugeChartForm from '../components/demo/forms/GaugeChartForm.vue'

const loggedIn = ref(true);
const userType = 'demo';
const canCreateDashboard = computed(() => true);
const canUpdateOrDeleteDashboard = () => true;
const canReadDashboard = () => true;

const popupTriggers = ref({ buttonTrigger: false })

const city = ref('Demo City');
const flag = 'demo-flag.png';

const layout = ref([

])

const projects = {
    Differdange: "luxembourgball.png",
    Cascais: "portugalball.png",
    Sofia: "bulgariaball.png",
    Maribor: "sloveniaball.png",
    Athens: "greeceball.png",
    Ioannina: "greeceball.png",
    Grenoble: "franceball.png",
    'Grenoble-Alpes': "franceball.png",
    Torino: "italyball.png"
}

const sections = ref([{ "name": "Section 1", "edit": false, "layout": [] }])

const selectedSection = reactive({
    "name": sections.value[0]["name"],
    "edit": sections.value[0]["edit"],
    "layout": sections.value[0]["layout"]
})

const STORAGE_KEY = 'demo-dashboard-data';

// Clear localStorage on page reload
window.onbeforeunload = () => {
    localStorage.removeItem(STORAGE_KEY);
};

// Function to save current state to localStorage
const saveTolocalStorage = () => {
    const dashboardData = {
        sections: sections.value,
        selectedSection: {
            name: selectedSection.name,
            edit: selectedSection.edit,
            layout: selectedSection.layout
        }
    };
    localStorage.setItem(STORAGE_KEY, JSON.stringify(dashboardData));
};

const getVisualisations = () => {
    // Check localStorage first
    const savedData = localStorage.getItem(STORAGE_KEY);
    if (savedData) {
        const parsed = JSON.parse(savedData);
        sections.value = parsed.sections;
        selectedSection.name = parsed.selectedSection.name;
        selectedSection.edit = parsed.selectedSection.edit;
        selectedSection.layout = parsed.selectedSection.layout;
        return;
    }

    // If no saved data, use default data
    const defaultData = {
        "sections": [{
            "name": "Overview",
            "layout": [
                {
                    x: 0,
                    y: 0,
                    w: 4,
                    h: 8,
                    i: "chart1",
                    id: "chart1",
                    chart: "LineChart",
                    attributes: {
                        city: "Demo City",
                        title: "Energy Consumption",
                        tableId: 1,
                        xtitle: "Time",
                        ytitle: "kWh",
                        color: "#0177a9",
                        target: 100
                    }
                },
                {
                    x: 4,
                    y: 0,
                    w: 4,
                    h: 8,
                    i: "chart2",
                    id: "chart2",
                    chart: "PieChart",
                    attributes: {
                        city: "Demo City",
                        title: "Energy Distribution",
                        tableId: 2
                    }
                },
                {
                    x: 8,
                    y: 0,
                    w: 4,
                    h: 8,
                    i: "chart3",
                    id: "chart3",
                    chart: "StatChart",
                    attributes: {
                        city: "Demo City",
                        title: "Total Energy",
                        tableId: 3,
                        suffix: "kWh",
                        target: 1000
                    }
                },
                {
                    x: 0,
                    y: 8,
                    w: 7,
                    h: 13,
                    i: "map1",
                    id: "map1",
                    chart: "Map",
                    attributes: {
                        city: "Demo City",
                        title: "City Map",
                        tableId: 4
                    }
                },
            ],
            edit: false
        }],
        "selectedSection": {
            "name": "Overview",
            "edit": false,
            "layout": [
                {
                    x: 0,
                    y: 0,
                    w: 4,
                    h: 8,
                    i: "0bbcc00cfc1",
                    chart: "LineChart",
                    attributes: {
                        tableId: 1,
                        title: "Demo LineChart",
                        xtitle: "Time",
                        ytitle: "Values",
                        color: "#0177a9",
                        target: 946
                    },
                    id: "bbcc00cfc1c"
                },
                {
                    x: 0,
                    y: 8,
                    w: 4,
                    h: 8,
                    i: "bcc00cfc1c9",
                    chart: "PieChart",
                    attributes: {
                        tableId: 1,
                        title: "Demo PieChartgfhfh"
                    },
                    id: "cc00cfc1c9c"
                },
                {
                    x: 8,
                    y: 0,
                    w: 4,
                    h: 8,
                    i: "c00cfc1c9c1",
                    chart: "BarChart",
                    attributes: {
                        tableId: 1,
                        title: "Demo BarChart"
                    },
                    id: "00cfc1c9c15"
                },
                {
                    x: 4,
                    y: 0,
                    w: 4,
                    h: 8,
                    i: "0cfc1c9c15b",
                    chart: "StatChart",
                    attributes: {
                        tableId: 1,
                        title: "C02 temp",
                        suffix: "kg",
                        target: 105
                    },
                    id: "cfc1c9c15bb"
                },
                {
                    x: 4,
                    y: 8,
                    w: 8,
                    h: 8,
                    i: "fc1c9c15bb2",
                    chart: "Table",
                    attributes: {
                        tableId: 1,
                        title: "Demo Table",
                        columns: ["Timestamp", "Type", "ID", "Value", "Location", "Status"]
                    },
                    id: "c1c9c15bb2f"
                }
            ]
        }
    };

    sections.value = defaultData.sections;
    selectedSection.name = defaultData.selectedSection.name;
    selectedSection.edit = defaultData.selectedSection.edit;
    selectedSection.layout = defaultData.selectedSection.layout;

    // Save to localStorage after setting up
    saveTolocalStorage();
};

getVisualisations();

async function storeVisualisations() {
    console.log('Saving dashboard...');
    saveTolocalStorage();
    setTimeout(() => {
        edit();
    }, 500);
}

const lineChartBool = ref(false)
const pieChartBool = ref(false)
const barChartBool = ref(false)
const statChartBool = ref(false)
const tableBool = ref(false)
const gaugeChartBool = ref(false)

const currentItem = ref({})
const visualisations = []
const editMode = ref(false)
// Remove this line:
// const tableForm = ref(false)

const currentSelectedChart = ref("")


const edit = () => {
    getVisualisations()
    editMode.value = !editMode.value
}

const toggleForm = () => {
    popupTriggers.value.buttonTrigger = !popupTriggers.value.buttonTrigger
}

const addElement = (value) => {
    selectedSection.layout.push({ x: 0, y: 5, w: 4, h: 8, i: value })
    toggleForm()

}

const deleteVisualisation = (item) => {
    selectedSection.layout = selectedSection.layout.filter((visualisation) => visualisation.id !== item.id)
    saveTolocalStorage();
}

const toggleKPIForm = (chart) => {
    // Create visualization directly without showing form
    createVisualisation('1', chart, chart, {
        unitText: 'units',
        target: Math.floor(Math.random() * 1000)
    });
}

const createVisualisation = (tableId, tableName, chart, kpi) => {
    var x = 0
    var y = 0
    if (dragItemStop.value.chart == chart) {
        x = dragItemStop.value.x
        y = dragItemStop.value.y
        selectedSection.layout = selectedSection.layout.filter(item => item.i !== dropId);
    }

    var vis = { 
        x: x, 
        y: y, 
        w: 4, 
        h: 8, 
        i: uid(), 
        chart: chart, 
        attributes: { 
            tableId: 1,
            title: `Demo ${chart}` 
        }, 
        id: uid() 
    }

    if (chart == "LineChart") {
        vis.attributes.xtitle = "Time"
        vis.attributes.ytitle = "Values"
        vis.attributes.color = "#0177a9"
        vis.attributes.target = kpi.target || 100
    } else if (chart == "StatChart") {
        vis.attributes.suffix = "units"
        vis.attributes.target = kpi.target || 100
    } else if (chart == "Map") {
        vis.w = 7;
        vis.h = 13; 
    }

    selectedSection.layout.push(vis)
    saveTolocalStorage();
}

const toggleLineChartEdit = () => {
    lineChartBool.value = !lineChartBool.value
}

const togglePieChartEdit = () => {
    pieChartBool.value = !pieChartBool.value
}

const toggleBarChartEdit = () => {
    barChartBool.value = !barChartBool.value
}

const toggleStatChartEdit = () => {
    statChartBool.value = !statChartBool.value
}

const toggleTableEdit = () => {
    tableBool.value = !tableBool.value
}

const toggleGaugeChartEdit = () => {
    gaugeChartBool.value = !gaugeChartBool.value
}

const editVisualisation = (item) => {
    currentItem.value = item
    if (item.chart == "LineChart") {
        toggleLineChartEdit()
    } else if (item.chart == "PieChart") {
        togglePieChartEdit()
    } else if (item.chart == "BarChart") {
        toggleBarChartEdit()
    } else if (item.chart == "StatChart") {
        toggleStatChartEdit()
    } else if (item.chart == "Table") {
        toggleTableEdit()
    } else if (item.chart == "GaugeChart") {
        toggleGaugeChartEdit()
    }
}

const updateChart = (object) => {
    const index = selectedSection.layout.findIndex(obj => obj.i === currentItem.value.i);
    if (index !== -1) {
        for (const [key, value] of Object.entries(object)) {
            selectedSection.layout[index].attributes[key] = value
        }
        currentItem.value = {}
        lineChartBool.value = false
        pieChartBool.value = false
        barChartBool.value = false
        statChartBool.value = false
        tableBool.value = false
        gaugeChartBool.value = false
    }
    saveTolocalStorage();
}

const organizeVisualisations = (resizeBool) => {
    let layoutCopy = selectedSection.layout;
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
                // Set default size for Map widget
                object.w = 7; // Default width for Map widget
                object.h = 13; // Default height for Map widget
            } else {
                // New size for all other widgets
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
    saveTolocalStorage();
};




onMounted(() => {
    document.addEventListener('dragover', syncMousePosition);
});

onBeforeUnmount(() => {
    document.removeEventListener('dragover', syncMousePosition);
});

const mouseAt = { x: -1, y: -1 }

function syncMousePosition(event) {
    mouseAt.x = event.clientX
    mouseAt.y = event.clientY
}

document.addEventListener('mousemove', syncMousePosition)

const dropId = 'drop'
const dragItem = ref({ x: 0, y: 0, w: 2, h: 2, i: '' })
const dragItemStop = ref({})
const gridSpaceRef = ref(null)
const gridLayout = ref(null)

const drag = throttle((chart) => {
    const parentRect = gridSpaceRef.value ? gridSpaceRef.value.getBoundingClientRect() : null;

    if (!parentRect || !gridLayout.value) return;

    const mouseInGrid =
        mouseAt.x > parentRect.left &&
        mouseAt.x < parentRect.right &&
        mouseAt.y > parentRect.top &&
        mouseAt.y < parentRect.bottom;
    if (mouseInGrid) {
        dragItem.value.x = mouseAt.x - parentRect.left
        dragItem.value.y = mouseAt.y - parentRect.top
        if (!selectedSection.layout.find(item => item.i === dropId)) {
            selectedSection.layout.push({
                x: 0,
                y: 0, // puts it at the bottom
                w: 4,
                h: 4,
                i: dropId,
                chart: "",
                id: dropId
            });


        }
    }
    
    const index = selectedSection.layout.findIndex(item => item.i === dropId);
    if (dragItemStop.value.chart) {
        dragItemStop.value = {}
        selectedSection.layout = selectedSection.layout.filter(item => item.i !== dropId);
        return
    }
    if (index !== -1) {
        const item = gridLayout.value.getItem(dropId);

        if (!item) {
            // layout.value = layout.value.filter(item => item.i !== dropId);
            return;
        }
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
    const parentRect = gridSpaceRef.value ? gridSpaceRef.value.getBoundingClientRect() : null;
    if (!parentRect || !gridLayout.value) return;

    const mouseInGrid =
        mouseAt.x > parentRect.left &&
        mouseAt.x < parentRect.right &&
        mouseAt.y > parentRect.top &&
        mouseAt.y < parentRect.bottom;

    if (mouseInGrid) {
        dragItemStop.value = JSON.parse(JSON.stringify(dragItem.value));
        dragItemStop.value.chart = chart;

        toggleKPIForm(chart);


        gridLayout.value.dragEvent(
            'dragend',
            dropId,
            dragItemStop.value.x,
            dragItemStop.value.y,
            dragItemStop.value.h,
            dragItemStop.value.w
        );

        selectedSection.layout = selectedSection.layout.filter(item => item.i !== dropId);
    } else {
        return;
    }
}

function addSection(event) {
    var currLength = sections.value.length + 1
    sections.value.push({ "name": "Section " + currLength, "edit": false, layout: [] })
    event.stopPropagation();
    saveTolocalStorage();

}




function setSection(section) {
    for (var i = 0; i < sections.value.length; i++) {
        if (selectedSection.name == sections.value[i].name) {
            sections.value[i].layout = selectedSection.layout
            break;
        }
    }
    selectedSection["name"] = section["name"]
    selectedSection["edit"] = section["edit"]
    selectedSection["layout"] = section["layout"]
    saveTolocalStorage();
}


if (sections.value.length > 0) {
    selectedSection.value = sections.value[0]
}

function deleteSection(item, event) {
    sections.value = sections.value.filter((section) => section.name !== item.name)
    event.stopPropagation();
    saveTolocalStorage();
}

function editSection(item, event) {
    item.edit = !item.edit
    console.log("item")
    console.log(item.name)
    tempName.value = item.name
    event.stopPropagation();
}

function renameSection(item, event) {
    console.log("renaming")
    console.log(item.name)
    item.edit = !item.edit
    if (item.name == selectedSection.name) {
        selectedSection.name = tempName.value
    }
    item.name = tempName.value
    event.stopPropagation();
    saveTolocalStorage();
}

function cancelClick(event) {
    event.stopPropagation();
}

const tempName = ref("")

// Ajouter cette nouvelle fonction
const exportToPNG = async () => {
    try {
        // Get the dashboard container
        const element = document.querySelector('.grid-space-static') || document.querySelector('.grid-space');
        if (!element) return;

        // Add temporary white background and padding for export
        const originalBackground = element.style.background;
        const originalPadding = element.style.padding;
        element.style.background = '#ffffff';
        element.style.padding = '20px';

        // Create canvas with better quality settings
        const canvas = await html2canvas(element, {
            useCORS: true,
            allowTaint: true,
            scale: 2, // Higher scale for better quality
            backgroundColor: '#ffffff',
            logging: false,
            width: element.scrollWidth,
            height: element.scrollHeight,
            imageTimeout: 0,
            onclone: (clonedDoc) => {
                // Add header to cloned document
                const header = clonedDoc.createElement('div');
                header.style.padding = '20px';
                header.style.background = '#0177a9';
                header.style.color = '#ffffff';
                header.style.fontSize = '24px';
                header.style.fontWeight = 'bold';
                header.style.marginBottom = '20px';
                header.innerHTML = `
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span>${city.value} Dashboard</span>
                        <span style="font-size: 14px;">${new Date().toLocaleDateString()}</span>
                    </div>
                `;
                const clonedElement = clonedDoc.querySelector('.grid-space-static') || clonedDoc.querySelector('.grid-space');
                clonedElement.insertBefore(header, clonedElement.firstChild);
            }
        });

        // Restore original styles
        element.style.background = originalBackground;
        element.style.padding = originalPadding;

        // Create and trigger download
        const link = document.createElement('a');
        link.download = `${city.value}_dashboard_${new Date().toISOString().split('T')[0]}.png`;
        link.href = canvas.toDataURL('image/png', 1.0); // Maximum quality
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);

    } catch (error) {
        console.error('Error exporting to PNG:', error);
    }
};

const exportToPDF = async () => {
    // Create PDF with A4 dimensions and better quality settings
    const pdf = new jsPDF('p', 'mm', 'a4', true);
    const pageWidth = pdf.internal.pageSize.getWidth();
    const pageHeight = pdf.internal.pageSize.getHeight();
    const margin = 15;
    const contentWidth = pageWidth - (2 * margin);

    // Helper function to add page header
    const addHeader = (pageNumber, totalPages) => {
        pdf.setFillColor(1, 119, 169); // #0177a9
        pdf.rect(0, 0, pageWidth, 25, 'F');
        
        pdf.setTextColor(255, 255, 255);
        pdf.setFontSize(16);
        pdf.text(`${city.value} Dashboard`, margin, 17);
        
        // Add date and page number
        const pageInfo = `Page ${pageNumber} of ${totalPages}`;
        const today = new Date().toLocaleDateString();
        pdf.setFontSize(10);
        pdf.text(today, pageWidth - margin - pdf.getTextWidth(today), 17);
        pdf.text(pageInfo, pageWidth/2 - pdf.getTextWidth(pageInfo)/2, 17);
    };

    let yPosition = 35;
    const charts = selectedSection.layout.map(item => document.getElementById(item.i));
    let pageNumber = 1;
    const totalPages = Math.ceil(charts.length / 2); // Estimate pages

    addHeader(pageNumber, totalPages);

    for (let i = 0; i < charts.length; i++) {
        if (!charts[i]) continue;

        try {
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

            // Check if we need a new page
            if (yPosition + imgHeight + 20 > pageHeight) {
                pdf.addPage();
                pageNumber++;
                addHeader(pageNumber, totalPages);
                yPosition = 35;
            }

            // Add chart title
            pdf.setFontSize(12);
            pdf.setTextColor(0, 0, 0);
            const title = charts[i].querySelector('h3')?.textContent || `Chart ${i + 1}`;
            pdf.text(title, margin, yPosition);
            yPosition += 8;

            // Add chart with white background and shadow
            pdf.setFillColor(255, 255, 255);
            pdf.setDrawColor(200, 200, 200);
            pdf.roundedRect(margin - 1, yPosition - 1, imgWidth + 2, imgHeight + 2, 2, 2, 'FD');
            pdf.addImage(imgData, 'PNG', margin, yPosition, imgWidth, imgHeight);
            
            yPosition += imgHeight + 20;

        } catch (error) {
            console.error('Error processing chart:', error);
        }
    }

    // Add footer to each page
    const totalPageCount = pdf.internal.getNumberOfPages();
    for (let i = 1; i <= totalPageCount; i++) {
        pdf.setPage(i);
        pdf.setFontSize(8);
        pdf.setTextColor(128, 128, 128);
        const footerText = `Generated from ${city.value} Dashboard - ${new Date().toLocaleString()}`;
        pdf.text(footerText, margin, pageHeight - 10);
    }

    // Save with formatted name
    pdf.save(`${city.value}_dashboard_${new Date().toISOString().split('T')[0]}.pdf`);
};

const chatMode = ref(false);

const toggleChat = () => {
  chatMode.value = !chatMode.value;
};

</script>

<template>
    <div v-if=true class="body">
        <h2 style="align-items: center;"> Overview: {{ city }} <span style="font-size: 1.2em; margin-left: 8px;">📊</span></h2>

        <!-- Dashboard Edit Mot -->
        <div v-if="editMode == true && canUpdateOrDeleteDashboard" class="empty">
            <div class="header">
                <div class="header-content">
                    <div class="left">
                        <v-menu>
                            <template v-slot:activator="{ props }">
                                <v-btn size="x-large" class="button" style="color: #FFFFFF;" color="#aec326" v-bind="props">
                                    Dashboards: {{ selectedSection.name }}
                                    <Icon icon="icomoon-free:page-break" width="30" height="30" style="color: #FFFFFF; margin-left: 5px;" />
                                </v-btn>
                            </template>
                            <v-list>
                                <v-list-item v-for="(item, index) in sections" :key="index" :value="index" @click="setSection(item)"
                                    style="display: flex; align-items: center">
                                    <v-list-item-content v-if="!item.edit" class="list-item-wrapper">
                                        <div class="list-item-content">
                                            <span>{{ item.name }}</span>
                                            <div class="icon-group">
                                                <Icon class="edit" icon="material-symbols-light:edit-square-outline" width="30" height="30"
                                                    style="color: #0177a9;" @click="editSection(item, $event)" />
                                                <Icon class="edit" icon="material-symbols-light:delete-outline" width="30" height="30"
                                                    style="color: red" @click="deleteSection(item, $event)" />
                                            </div>
                                        </div>
                                    </v-list-item-content>
                                    <v-list-item-content v-else style="display: flex;">
                                        <v-text-field @click="cancelClick($event)" @keydown.space="cancelClick($event)" v-model="tempName"
                                            style="width: 200px">
                                        </v-text-field>
                                        <Icon icon="material-symbols:check" width="30" height="30" @click="renameSection(item, $event)"
                                            style="color: #aec326; margin-top: 10px;" />
                                        <Icon class="edit" icon="material-symbols-light:delete-outline" width="30" height="30"
                                            style="color: red" @click="deleteSection(item, $event)" />
                                    </v-list-item-content>
                                </v-list-item>
                                <v-spacer></v-spacer>
                                <v-btn variant="text" @click="menu = false">Cancel</v-btn>
                                <v-btn color="primary" variant="text" @click="addSection($event)">Add section</v-btn>
                            </v-list>
                        </v-menu>
                    </div>
                    <div class="right">
                        <v-btn size="x-large" @click="edit" color="red" class="button">
                            Turn off edit mode
                        </v-btn>
                        <v-btn size="x-large" @click="storeVisualisations" class="button" style="background-color: #aec326; color: white;">
                            Save Dashboard
                        </v-btn>
                        <v-btn size="x-large" @click="organizeVisualisations(false)" color="#0177a9" class="button">
                            <Icon icon="material-symbols:border-all" width="30" height="30" style="color: #FFFFFF" />
                            Organise Visualisations
                        </v-btn>
                        <v-btn size="x-large" @click="organizeVisualisations(true)" color="#0177a9" class="button">
                            <Icon icon="material-symbols:border-all" width="30" height="30" style="color: #FFFFFF" />
                            Organise and Resize
                        </v-btn>
                        <!-- <v-btn 
                          size="x-large" 
                          @click="toggleChat" 
                          color="climaboroughBlue" 
                          class="button"
                        >
                          <Icon icon="material-symbols:chat" width="30" height="30" style="color: #FFFFFF; margin-right: 5px;" />
                          Chat Assistant
                        </v-btn> -->
                    </div>
                </div>
            </div>
            <div class="container">
                <div class="widget-bar">
                    <div class="widget-bar-content" style="margin: 10px">
                        <a style="display: flex">Choose widgets</a>
                        <br>
                        <a>Charts</a>
                        <div class="widget-icon" draggable="true" unselectable="on" @drag="drag('LineChart')"
                            @dragend="dragEnd('LineChart')">
                            <img src="/LineChart.png" class="icon" style="width: 80px" @click="toggleKPIForm('LineChart')">
                        </div>
                        <a>Pie Charts</a>
                        <div class="widget-icon" draggable="true" unselectable="on" @drag="drag('PieChart')"
                            @dragend="dragEnd('PieChart')">
                            <img src="/PieChart.png" class="icon" style="width: 80px" @click="toggleKPIForm('PieChart')">
                        </div>
                        <a>Bar Charts</a>
                        <div class="widget-icon" draggable="true" unselectable="on" @drag="drag('BarChart')"
                            @dragend="dragEnd('BarChart')">
                            <img src="/BarChart.png" class="icon" style="width: 80px" @click="toggleKPIForm('BarChart')">
                        </div>
                        <a>Stats Charts</a>
                        <div class="widget-icon" draggable="true" unselectable="on" @drag="drag('StatChart')"
                            @dragend="dragEnd('StatChart')">
                            <img src="/StatChart.png" class="icon" style="width: 80px" @click="toggleKPIForm('StatChart')">
                        </div>
                        <a>Tables</a>
                        <div class="widget-icon" draggable="true" unselectable="on" @drag="drag('Table')"
                            @dragend="dragEnd('Table')">
                            <img src="/Table.png" class="icon" style="width: 80px" @click="toggleKPIForm('Table')">
                        </div>
                        <a>Maps</a>
                        <div class="widget-icon" draggable="true" unselectable="on" @drag="drag('Map')"
                            @dragend="dragEnd('Map')">
                            <img src="/Map.png" class="icon" style="width: 80px" @click="createVisualisation('1', 'Map', 'Map', {})">
                        </div>
                        <a>Gauge Charts</a>
                        <div class="widget-icon" draggable="true" unselectable="on" @drag="drag('GaugeChart')"
                            @dragend="dragEnd('GaugeChart')">
                            <img src="/Map.png" class="icon" style="width: 80px" @click="toggleKPIForm('GaugeChart')">
                        </div>
                    </div>
                </div>
                <div ref="gridSpaceRef" class="grid-space">
                    <GridLayout v-model:layout="selectedSection.layout" ref="gridLayout" :col-num="12" :row-height="30"
                        is-draggable is-bounded use-css-transforms restore-on-drag :vertical-compact="false" style="min-height: 800px;">
                        <GridItem class="test" v-for="item in selectedSection.layout" :key="item.i" :x="item.x" :y="item.y" :w="item.w" :h="item.h" :i="item.i" :id="item.id">
                            <div class="delete" style="display: flex; justify-content: flex-end; gap: 5px;">
                                <Icon class="edit" icon="material-symbols-light:edit-square-outline" width="30" height="30"
                                    style="color: #0177a9" @click="editVisualisation(item)" />
                                <Icon class="edit" icon="material-symbols-light:delete-outline" width="30" height="30"
                                    style="color: red" @click="deleteVisualisation(item)" />
                            </div>
                            <div class="item" style="height: 95%; width: 95%;">
                                <LineChart v-if="item.chart == 'LineChart'" :city="item.attributes.city"
                                    :tableId="item.attributes.tableId" :title="item.attributes.title" :xtitle="item.attributes.xtitle"
                                    :ytitle="item.attributes.ytitle" :color="item.attributes.color" :target="item.attributes.target" />
                                <PieChart v-if="item.chart == 'PieChart'" :city="item.attributes.city"
                                    :tableId="item.attributes.tableId" :title="item.attributes.title" />
                                <BarChart v-if="item.chart == 'BarChart'" :city="item.attributes.city"
                                    :tableId="item.attributes.tableId" :title="item.attributes.title" />
                                <StatChart v-if="item.chart == 'StatChart'" :city="item.attributes.city"
                                    :tableId="item.attributes.tableId" :title="item.attributes.title"
                                    :suffix="item.attributes.suffix" :id="item.id" :target="item.attributes.target" />
                                <Table v-if="item.chart == 'Table'" :city="item.attributes.city"
                                    :tableId="item.attributes.tableId" :title="item.attributes.title"
                                    :columns="item.attributes.columns" />
                                <Map v-if="item.chart == 'Map'" :city="item.attributes.city" />
                                <GaugeChart v-if="item.chart == 'GaugeChart'" :title="item.attributes.title" :value="item.attributes.value" />
                            </div>
                        </GridItem>
                    </GridLayout>
                </div>
            </div>
            <div class="forms">
                <!-- Remove KPIForm -->
                <LineChartForm v-if="lineChartBool" @cancel="toggleLineChartEdit" @updateChart="updateChart"
                    :city="currentItem.attributes.city" :title="currentItem.attributes.title"
                    :xtitle="currentItem.attributes.xtitle" :ytitle="currentItem.attributes.ytitle"
                    :color="currentItem.attributes.color" />
                <PieChartForm v-if="pieChartBool" :title="currentItem.attributes.title" @cancel="togglePieChartEdit"
                    @updateChart="updateChart" />
                <BarChartForm v-if="barChartBool" :title="currentItem.attributes.title" 
                    @cancel="toggleBarChartEdit" @updateChart="updateChart" />
                <StatChartForm v-if="statChartBool" :title="currentItem.attributes.title"
                    :suffix="currentItem.attributes.suffix" @cancel="toggleStatChartEdit" @updateChart="updateChart" />
                <TableForm v-if="tableBool" :city=city :title="currentItem.attributes.title"
                    :tableId="currentItem.attributes.tableId" :columns="currentItem.attributes.columns"
                    @cancel="toggleTableEdit" @updateChart="updateChart" />
                <GaugeChartForm v-if="gaugeChartBool" :title="currentItem.attributes.title" :value="currentItem.attributes.value"
                    @cancel="toggleGaugeChartEdit" @updateChart="updateChart" />
            </div>
        </div>
        <!-- Dashboard without edit -->
        <div v-else-if="editMode == false" class="empty">
            <div class="header">
                <v-col cols="auto" class="buttons" style="display: flex; justify-content: space-between; align-items: center;">
                    <div class="left">
                        <v-menu>
                            <template v-slot:activator="{ props }">
                                <v-btn size="x-large" class="button" style="color: #FFFFFF;" color="#aec326" v-bind="props">
                                    Dashboards: {{ selectedSection.name }}
                                    <Icon icon="icomoon-free:page-break" width="30" height="30" style="color: #FFFFFF; margin-left: 5px;" />
                                </v-btn>
                            </template>
                            <v-list>
                                <v-list-item v-for="(item, index) in sections" :key="index" :value="index"
                                    @click="setSection(item)" style="display: flex; align-items: center">
                                    <v-list-item-content>
                                        <span>{{ item.name }}</span>
                                    </v-list-item-content>
                                </v-list-item>
                                <v-spacer></v-spacer>

                                <v-btn variant="text" @click="menu = false">
                                    Cancel
                                </v-btn>
                            </v-list>
                        </v-menu>
                    </div>
                    <div class="right" style="display: flex; gap: 10px;">
                        <v-menu>
                            <template v-slot:activator="{ props }">
                                <v-btn rounded="0" size="x-large" color="#0177a9" class="button" v-bind="props">
                                    Export
                                    <Icon icon="material-symbols:download" width="30" height="30" style="color: #FFFFFF; margin-left: 5px;" />
                                </v-btn>
                            </template>
                            <v-list>
                                <v-list-item @click="exportToPNG">
                                    <v-list-item-title>
                                        <div style="display: flex; align-items: center; gap: 8px;">
                                            <Icon icon="material-symbols:download" width="24" height="24" />
                                            Export as PNG
                                        </div>
                                    </v-list-item-title>
                                </v-list-item>
                                <v-list-item @click="exportToPDF">
                                    <v-list-item-title>
                                        <div style="display: flex; align-items: center; gap: 8px;">
                                            <Icon icon="material-symbols:picture-as-pdf" width="24" height="24" />
                                            Export as PDF
                                        </div>
                                    </v-list-item-title>
                                </v-list-item>
                            </v-list>
                        </v-menu>
                        <div v-if=true>
                            <v-btn rounded="0" size="x-large" @click="edit" color="#0177a9" class="button">
                                Dashboard Builder
                                <Icon icon="ion:construct" width="30" height="30" style="color: #FFFFFF; margin-left: 5px;" />
                            </v-btn>
                        </div>
                    </div>
                </v-col>
            </div>
            <div v-if="selectedSection.layout.length > 0" class="static-grid">
                <div class="grid-space-static">
                    <GridLayout v-model:layout="selectedSection.layout" :col-num="12" :row-height="30"
                        :is-draggable="false" :is-resizable="false" is-bounded use-css-transforms restore-on-drag
                        :vertical-compact="false" style="min-height: 800px;">
                        <GridItem v-for="item in selectedSection.layout" :key="item.i" :x="item.x" :y="item.y"
                            :w="item.w" :h="item.h" :i="item.i" :id="item.id">
                            <div class="item" style="height: 95%; width: 95%;">
                                <LineChart v-if="item.chart == 'LineChart'" :city="item.attributes.city"
                                    :tableId="item.attributes.tableId" :title="item.attributes.title"
                                    :xtitle="item.attributes.xtitle" :ytitle="item.attributes.ytitle"
                                    :color="item.attributes.color" :target="item.attributes.target" />
                                <PieChart v-if="item.chart == 'PieChart'" :city="item.attributes.city"
                                    :tableId="item.attributes.tableId" :title="item.attributes.title" />
                                <BarChart v-if="item.chart == 'BarChart'" :city="item.attributes.city"
                                    :tableId="item.attributes.tableId" :title="item.attributes.title" />
                                <StatChart v-if="item.chart == 'StatChart'" :city="item.attributes.city"
                                    :tableId="item.attributes.tableId" :title="item.attributes.title"
                                    :suffix="item.attributes.suffix" :id="item.id" :target="item.attributes.target" />
                                <Table v-if="item.chart == 'Table'" :city="item.attributes.city"
                                    :tableId="item.attributes.tableId" :title="item.attributes.title"
                                    :columns="item.attributes.columns" />
                                <Map v-if="item.chart == 'Map'" :city="item.attributes.city" />
                                <GaugeChart v-if="item.chart == 'GaugeChart'" :title="item.attributes.title" :value="item.attributes.value" />
                            </div>
                        </GridItem>
                    </GridLayout>
                </div>
            </div>
        </div>
    </div>
    <div v-else class="login-warning">
        <p>You need to login if you want to have access to the projects. Use the login button on the top right corner of
            this page.</p>
        <div class="login" style="padding: 40px;">
            <LoginForm />
        </div>
    </div>
    <!-- <div v-if="chatMode" class="chat-popup">
      <div class="chat-popup-inner">
        <div class="chat-header">
          <h3>Dashboard Assistant</h3>
          <v-btn icon="mdi-close" size="small" @click="toggleChat" />
        </div>
        <DashboardChat 
          :city="city" 
                    </GridLayout>
                </div>
            </div>
        </div>
    </div>
    <div v-else class="login-warning">
        <p>You need to login if you want to have access to the projects. Use the login button on the top right corner of
            this page.</p>
        <div class="login" style="padding: 40px;">
            <LoginForm />
        </div>
    </div>
    <!-- <div v-if="chatMode" class="chat-popup">
      <div class="chat-popup-inner">
        <div class="chat-header">
          <h3>Dashboard Assistant</h3>
          <v-btn icon="mdi-close" size="small" @click="toggleChat" />
        </div>
        <DashboardChat 
          :city="city" 
          @createVisualisation="createVisualisation"
        />
      </div>
    </div> -->
</template>


<style lang="scss" scoped>
.body {
    margin: 10px;
    align-items: center;
    flex-direction: column;
}


.container {
    background-color: rgb(235, 235, 235);
    display: flex;
}

:deep(.vgl-item:not(.vgl-item--placeholder)) {
    background-color: #ffffff;
    /* Card background color */
    border-radius: 10px;
    /* Rounded corners */
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
    /* Shadow effect */
    padding: 20px;
    /* Padding inside the card */
}

.test {
    background-color: #ffffff;
    /* Card background color */
    border-radius: 10px;
    /* Rounded corners */
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
    /* Shadow effect */
    padding: 20px;
    /* Padding inside the card */
    border: 3px dashed #cccccc;
    /* Dashed border for edit mode */
}

.test:hover {
    box-shadow: 0px 16px 32px rgba(0, 0, 0, 0.6);
    /* Shadow effect */
}


.widget-bar {
    flex: 1;
    background-color: #0177a9;
    text-align: center;
    color: #ffffff;
    font-size: medium;
}

.widget-icon {
    padding: 10px;
}

.icon {
    transition: box-shadow 0.2s ease
}

.icon:hover {
    cursor: pointer;
    /* Cursor on hover */
    box-shadow: 1px 1px 10px 10px rgba(0, 0, 0, 0.5);
}

.grid-space {
    flex: 9;

    .vgl-layout::before {
        position: absolute;
        width: calc(100% - 5px);
        height: calc(100% - 5px);
        margin: 5px;
        content: '';
        background-image: linear-gradient(to right, lightgrey 1px, transparent 1px),
            linear-gradient(to bottom, lightgrey 1px, transparent 1px);
        background-repeat: repeat;
        background-size: calc(calc(100% - 5px) / 12) 40px;
    }

    .item {
        overflow: auto;
    }
}

.grid-space-static {
    .item {
        overflow: auto;
    }
}

.buttons {
    display: flex;
    align-items: center;
}

.button {
    padding: 10px;
}

.edit:hover {
    cursor: pointer;
    /* Cursor on hover */
}

.vgl-layout {
    --vgl-placeholder-bg: rgb(255, 255, 255);
}



.login-warning {
    width: 100%;
    height: calc(100vh - 40px);
    display: flex;
    justify-content: center;
    align-items: center;
    flex-direction: column;
    text-align: center;
    background-color: #f8f9fa;

    h2 {
        color: #dc3545;
        margin-bottom: 25px;
    }

    p {
        font-size: 1.2em;
        line-height: 1.5em;
        color: #343a40;

        .login-link {
            color: #0177a9;
            text-decoration: none;
        }
    }
}

.droppable-element {
    width: 150px;
    padding: 10px;
    margin: 10px 0;
    text-align: center;
    background-color: #fdd;
    border: 1px solid black;
}

.header {
    margin-bottom: 20px;

    .header-content {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .left, .right {
        display: flex;
        gap: 10px;
        align-items: center;
    }

    .button {
        height: 48px;
        display: flex;
        align-items: center;
    }
}

.header-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 10px;
}

.right {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
}

.delete {
    .edit {
        cursor: pointer;
        transition: transform 0.2s ease;
        
        &:hover {
            transform: scale(1.1);
        }
    }
}

.list-item-wrapper {
    width: 100%;
    padding: 8px 0;
}

.list-item-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
    width: 100%;

    span {
        flex-grow: 1;
    }

    .icon-group {
        display: flex;
        gap: 8px;
        align-items: center;
    }
}

.chat-popup {
  position: fixed;
  bottom: 20px;
  right: 20px;
  width: 400px;
  height: 600px;
  z-index: 9999;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 20px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
}

.chat-popup-inner {
  display: flex;
  flex-direction: column;
  height: 100%;
  
  :deep(.chat-container) {
    height: calc(100% - 50px);
    overflow: hidden;
  }
  
  :deep(.messages) {
    height: calc(100% - 140px);
    overflow-y: auto;  }
}

.chat-header {
  height: 50px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  border-bottom: 1px solid #eee;
  background: #f8f9fa;
  
  h3 {
    margin: 0;
    color: #333;
    font-size: 16px;
  }
}
</style>
