<script setup>
import { ref, onMounted } from 'vue';
import WebSocketService from '../js/websocket.js';
import { useAuth } from '../composables/useAuth';
import AuthRequired from '../components/AuthRequired.vue';

const auth = useAuth();

const pdfs = ref(["PDF1", "PDF2", "PDF3"])

const messages = ref([]);
const inputMessage = ref('');
let websocketService = null;

function downloadPdf(pdfTitle) {
  const url = `/pdfs/${pdfTitle}`;
  window.open(url, '_blank'); // Opens in new tab instead of downloading
}

function loadPdfs() {
  const pdfsName = Object.keys(import.meta.glob('../assets/pdfs/*.pdf')).map(file => file.replace('../assets/pdfs/', ''));
  const pdfsTemp = []
  pdfsName.forEach(function (item, index) {
    pdfsTemp.push({ 'title': item, 'value': index })
  })
  pdfs.value = pdfsTemp
}

loadPdfs()

const sendMessage = () => {
  if (inputMessage.value.trim() !== '') {
    websocketService.send(inputMessage.value);
    messages.value.push({ "message": `<strong>You:</strong> ${inputMessage.value}`, "bot": false });
    inputMessage.value = '';
  }
};

const onMessageReceived = (message) => {
  let response = JSON.parse(message)["message"]
  console.log(response)
  let bot_response = response["answer"]
  let docs = response["docs"]
  docs = docs.map(obj => {
    obj["metadata"]["source"] = obj["metadata"]["source"].replace("./pdfs/", "")
    return obj
  })
  var metadata_response = "For the response, I inspired myself from the following sources:<br>"
  docs.forEach(function (value) {
    metadata_response = metadata_response + "Document: <a href='/pdfs/" + value["metadata"]["source"] + "'>" + value["metadata"]["source"] + "</a> on page " + value["metadata"]["page"] + " <br>"
  })

  // Check if bot_response is longer than the default greeting
  const defaultGreeting = "Hello! How can I assist you today?";
  let finalMessage;
  
  if (bot_response.length > defaultGreeting.length) {
    finalMessage = `<strong>Bot:</strong> ${bot_response} <br> ${metadata_response}`;
  } else {
    finalMessage = `<strong>Bot:</strong> ${bot_response}`;
  }

  messages.value.push({ "message": finalMessage, "bot": true });
};

onMounted(() => {
  // Remove authentication check since AuthRequired handles it
  websocketService = new WebSocketService('wss://climaborough-bot.iworker1.private.list.lu');
  // websocketService = new WebSocketService('ws://localhost:8765');
  websocketService.setOnMessageCallback(onMessageReceived);
  
  // Set a small delay to ensure the websocket connection is established
  setTimeout(() => {
    // Send an initial "rag" command to activate RAG mode
    websocketService.send("rag");
    
    // Add a welcome message
    messages.value.push({ 
      "message": "<strong>System:</strong> RAG mode activated. You can now ask questions about climate solutions.", 
      "bot": true 
    });
  }, 1000);
});
</script>


<template>
  <AuthRequired>
    <div class="body">
      <div class="chat-container">
        <h3>On this page, you have the opportunity to talk with our very own ClimaSolutions Bot! The ClimaSolutions Bot is
          here to help you understand important concepts in the Climaborough project and is connected to knowledge chosen
          by our experts.</h3>
        <div class="messages">
          <div v-for="(message, index) in messages" :key="index" class="message">
            <div v-if="message.bot" class="content" v-html="message.message">
            </div>
            <div v-else class="content" v-html="message.message">
            </div>
          </div>
        </div>
        <input v-model="inputMessage" @keyup.enter="sendMessage" placeholder="Type a message..." />
        <button @click="sendMessage">Send</button>
      </div>
      <div class="pdf-container">
        <h3>Available Resources:</h3>

        <v-card class="mx-auto" style="height: 80vh; overflow-y: auto;">
          <v-list>
            <v-list-item-group v-for="pdf in pdfs" :key="pdf.title" @click="downloadPdf(pdf.title)"
              class="cursor-pointer">
              <v-list-item>
                <v-list-item-content>
                  <v-list-item-title>{{ pdf.title }}</v-list-item-title>
                </v-list-item-content>
              </v-list-item>
            </v-list-item-group>
          </v-list>
        </v-card>
      </div>
    </div>
  </AuthRequired>
</template>



<style lang=scss scoped>
.body {
  display: flex;
  width: 100%;
  min-height: 90vh;
}


.chat-container {
  flex: 3;
  padding: 20px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  margin: 0 auto;
  height: 90vh;
}

.pdf-container {
  flex: 1;
  padding: 20px;
  background-color: #f5f5f5;
  border-left: 1px solid #ccc;
  height: 90vh;
}

.messages {
  flex: 1;
  overflow-y: auto;
  margin-bottom: 10px;
  border: 1px solid #ccc;
  padding: 10px;
}

.message {
  margin-bottom: 10px;
}

input {
  padding: 10px;
  margin-bottom: 10px;
  border: 1px solid #ccc;
  width: calc(100% - 22px);
}

button {
  padding: 10px;
  border: none;
  background-color: #42b983;
  color: white;
  cursor: pointer;
}

button:hover {
  background-color: #368c70;
}

.content {
  white-space: pre-wrap;
}


.login-warning {
  width: 100%;
  height: calc(100vh - 100px);
  display: flex;
  justify-content: center;
  align-items: center;
  flex-direction: column;
  text-align: center;
  background-color: #f8f9fa;

  h2 {
    color: #0177a9;
    margin-bottom: 25px;
  }

  p {
    font-size: 1.2em;
    line-height: 1.5em;
    color: #343a40;
    margin-bottom: 30px;
  }
}

.login-container {
  width: 100%;
  max-width: 450px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}
</style>
