#!/bin/sh

# Check if required environment variables are set
if [ -z "$DB_NAME" ]; then
    echo "DB_NAME variable not set. Exiting"
    exit 1
fi

# Check if required environment variables are set
if [ -z "$DB_PASSWORD" ] ; then
    echo "DB_PASSWORD variable not set. Exiting."
    exit 1
fi

# Check if required environment variables are set
if  [ -z "$DB_USER" ] ; then
    echo "DB_USER variable not set. Exiting."
    exit 1
fi

# Check if required environment variables are set
if  [ -z "$DB_HOST" ]; then
    echo "DB_HOST variable not set. Exiting."
    exit 1
fi

# Execute uvicorn with the specified arguments
exec uvicorn api_interface_objects:app --host 0.0.0.0 --port 8000
