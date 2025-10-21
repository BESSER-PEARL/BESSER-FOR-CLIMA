#!/bin/bash

# Redirect stderr to a log file
exec 2>> /var/log/vue_app.log

# Verify that the API_URL environment variable is set
if [ -z "$API_URL" ]; then
  echo "Error: API_URL environment variable is not set" 
  exit 1
fi

# Verify that the API_URL environment variable is set
if [ -z "$WEBSOCKET_URL" ]; then
  echo "Error: API_URL environment variable is not set" 
  exit 1
fi

# Verify that the sed command succeeds
if ! sed -i "s|localhost:8765|${WEBSOCKET_URL}|g" /app/assets/*; then
  echo "Error: sed command failed"
  exit 1
fi

# Verify that the sed command succeeds
if ! sed -i "s|http://localhost:8000|${API_URL}|g" /app/assets/*; then
  echo "Error: sed command failed"
  exit 1
fi
exec nginx -g 'daemon off;'

