# Climaborough-data-platform-frontend (aka the dashboards)

## Requirements
* Node.js v18


## Project Setup

```sh
npm install
```

### Compile and Hot-Reload for Development

```sh
npm run dev
```


## Docker

Docker build:
```sh
docker build -t frontend .
```

Run docker version using:
```
docker run -p 3000:3000 -e API_URL=http://localhost:8000 -e WEBSOCKET_URL=ws://localhost:8765 frontend
```

Set the following environment variables:
* API_URL = "Address of your fastapi application"
* WEBSOCKET_URL = "Address of your bot application"
