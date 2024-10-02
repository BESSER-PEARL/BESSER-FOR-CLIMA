// src/services/websocket.js
import ReconnectingWebSocket from 'reconnecting-websocket';
const options = {
  WebSocket: WebSocket,  // You can also pass a custom WebSocket constructor here
  connectionTimeout: 4000,
  maxRetries: 10,
  debug: true,
};
class WebSocketService {
  constructor(url) {
    this.url = url;
    this.connect();
  }

  connect() {
    this.websocket = new ReconnectingWebSocket(this.url, undefined, options);

    this.websocket.onopen = () => {
      console.log('WebSocket connected');
    };

    this.websocket.onmessage = (event) => {
      console.log('WebSocket message received:', event.data);
      if (this.onMessage) {
        this.onMessage(event.data);
      }
    };

    this.websocket.onclose = () => {
      console.log('WebSocket disconnected');
    };

    this.websocket.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
  }

  send(message) {
    if (this.websocket.readyState === WebSocket.OPEN) {
        console.log(message)
        var body = {}
        body["action"] = "user_message"
        body["message"] = message
        this.websocket.send(JSON.stringify(body));
    } else {
      console.error('WebSocket is not open. Ready state is:', this.websocket.readyState);
    }
  }

  setOnMessageCallback(callback) {
    this.onMessage = callback;
  }
}

export default WebSocketService;
