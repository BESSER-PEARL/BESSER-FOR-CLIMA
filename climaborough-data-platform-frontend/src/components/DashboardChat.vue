<script setup>
import { ref, onMounted } from 'vue';
import WebSocketService from '../js/websocket.js';
import { useAuth } from '../composables/useAuth';

const auth = useAuth();

const props = defineProps({
  city: {
    type: String,
    required: true
  }
});

const emit = defineEmits(['createVisualisation']);
const messages = ref([]);
const inputMessage = ref('');
let websocketService = null;
const availableKPIs = ref([]);

const sendMessage = () => {
  if (inputMessage.value.trim() !== '') {
    websocketService.send(JSON.stringify({
      message: inputMessage.value,
      city: props.city,
      type: 'dashboard',
      context: `You are a dashboard visualization assistant. When users request visualizations, you must select an appropriate KPI from the available ones and respond with a JSON structure:
      {
        "answer": "Your natural language response",
        "visualization": {
          "type": "LineChart|PieChart|BarChart|StatChart",
          "kpi_id": "The KPI ID (e.g. temp001, money001, energy001)",
          "title": "A descriptive title for the visualization",
          "unitText": "The unit from the KPI (e.g. Celsius, Euros, Percentage)",
          "target": The target value from the KPI or null
        }
      }
      `
    }));
    
    messages.value.push({ 
      message: `<strong>You:</strong> ${inputMessage.value}`, 
      bot: false 
    });
    inputMessage.value = '';
  }
};

const getAvailableKPIs = async () => {
  try {
    const token = await auth.getAccessToken();
    const response = await fetch(`http://localhost:8000/${props.city.toLowerCase()}/kpis`, {
      headers: {
        'Authorization': 'Bearer ' + token
      }
    });
    const kpis = await response.json();
    availableKPIs.value = kpis;
    
    // Create a formatted list of KPIs to show to the user
    let kpiList = "";
    kpis.forEach(kpi => {
      kpiList += `<li><strong>${kpi.name}</strong> (${kpi.unit || 'No unit'})</li>`;
    });
    
    // Add message showing available KPIs
    messages.value.push({ 
      message: `<strong>System:</strong> Available KPIs for ${props.city}:<br><ul>${kpiList}</ul>`, 
      bot: true 
    });
  } catch (error) {
    console.error('Error fetching KPIs:', error);
    
    // Add an error message if KPIs couldn't be loaded
    messages.value.push({ 
      message: `<strong>Bot:</strong> I couldn't access the KPIs for ${props.city}. Please try again later.`, 
      bot: true 
    });
  }
};

const onMessageReceived = (message) => {
  try {
    const wsMessage = JSON.parse(message);
    // Check if message contains answer property
    let botResponse = wsMessage.message?.answer;
    
    // If botResponse is undefined, skip processing
    if (!botResponse) {
      console.log("Bot response is undefined, skipping message processing");
      return;
    }
    
    // Try to parse the response as JSON (for visualization requests)
    try {
      const parsedResponse = JSON.parse(botResponse);
      if (parsedResponse.visualization) {
        const vis = parsedResponse.visualization;
        // Find matching KPI from available KPIs
        const matchingKPI = availableKPIs.value.find(kpi => 
          kpi.name.toLowerCase().includes(vis.kpi_id.replace(/\d+/g, ''))
        );
        
        if (matchingKPI) {
          emit('createVisualisation', 
            matchingKPI.id,
            vis.title,
            vis.type,
            matchingKPI  // Pass the entire KPI object like KPIForm does
          );
        }
      }
      
      messages.value.push({ 
        message: `<strong>Bot:</strong> ${parsedResponse.answer}`, 
        bot: true 
      });
    } catch (error) {
      // If it's not valid JSON, treat it as a plain text response
      console.log("Response is not JSON, handling as plain text");
      console.log(botResponse);
      messages.value.push({ 
        message: `<strong>Bot:</strong> ${botResponse}`, 
        bot: true 
      });
    }
  } catch (error) {
    // If the WebSocket message itself isn't valid JSON, handle it as a string
    console.error("Failed to process websocket message:", error);
    // Only show message if it's not an acknowledgment message
    if (message && message !== "bot") {
      try {
        // Try to handle it as a plain text message
        messages.value.push({
          message: `<strong>Bot:</strong> ${message}`,
          bot: true
        });
      } catch (e) {
        console.error("Failed to process message as text:", e);
      }
    }
  }
};

onMounted(() => {
  websocketService = new WebSocketService('wss://climaborough-bot.iworker1.private.list.lu');
  // websocketService = new WebSocketService('ws://localhost:8765');
  websocketService.setOnMessageCallback(onMessageReceived);
  
  // Wait for websocket connection and KPIs to be loaded
  getAvailableKPIs().then(() => {
    // This will trigger the llm_body in climabot.py
    setTimeout(() => {
      websocketService.send("bot");
      
      // Add a welcome message
      messages.value.push({ 
        message: `<strong>System:</strong> Dashboard assistant activated. I'll help you create visualizations for ${props.city}.`, 
        bot: true 
      });
    }, 1000);
  });
});
</script>

<template>
  <div class="chat-container">
    <h3>Design your dashboard by describing what you want to see. I'll help you create the visualizations!</h3>
    <div class="messages">
      <div v-for="(message, index) in messages" :key="index" class="message">
        <div v-if="message.bot" class="content" v-html="message.message">
        </div>
        <div v-else class="content" v-html="message.message">
        </div>
      </div>
    </div>
    <div class="chat-input">
      <input 
        v-model="inputMessage" 
        @keyup.enter="sendMessage" 
        placeholder="Describe what you want to add to your dashboard..." 
      />
      <button @click="sendMessage">Send</button>
    </div>
  </div>
</template>

<style lang="scss" scoped>
@use "sass:color";

.chat-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: white;
  
  h3 {
    padding: 20px 20px 0 20px;
    color: #333;
    font-size: 14px;
    margin: 0;
  }
}

.messages {
  flex: 1;
  overflow-y: auto;
  margin: 20px;
  padding: 20px;
  border: 1px solid #eee;
  border-radius: 8px;
  background: #f8f9fa;
}

.message {
  margin-bottom: 15px;
  
  .content {
    padding: 12px;
    border-radius: 8px;
    background: white;
    border: 1px solid #e0e0e0;
    color: #333;
    
    &:not(.bot) {
      background: #e3f2fd;
      border-color: #90caf9;
    }
  }
}

.chat-input {
  display: flex;
  gap: 10px;
  padding: 10px 0;
  
  input {
    flex: 1;
    padding: 12px;
    border: 2px solid #ddd;
    border-radius: 4px;
    font-size: 14px;
    color: #333;
    
    &:focus {
      outline: none;
      border-color: #0177a9;
    }
  }
  
  button {
    padding: 12px 24px;
    background: #0177a9;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-weight: 500;
    
    &:hover {
      background: color.scale(#0177a9, $lightness: -10%);
    }
  }
}
</style>