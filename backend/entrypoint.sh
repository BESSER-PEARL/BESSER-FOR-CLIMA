#!/bin/sh

# Function to wait for the PostgreSQL database to be ready
wait_for_postgres() {
  until PGPASSWORD="$POSTGRES_PASSWORD" psql -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c '\q'; do
    echo "PostgreSQL is unavailable - sleepingddd"
    sleep 1
  done
  echo "PostgreSQL is up - continuing"
}

# Wait for PostgreSQL to be ready
wait_for_postgres

# Set the configuration file
#CONFIG_FILE="conf/custom.ini"
#CONFIG_FILE="../../../etc/grafana/grafana.ini"
# Replace the database configuration in the Grafana configuration file
#sed -i "110s#\(url = \).*#url = postgres://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}#g" $CONFIG_FILE
#sed -i "111s#\(;type = \).*#type = postgres#g" $CONFIG_FILE
#sed -i "112s#\(;host = \).*#host = ${POSTGRES_HOST}#g" $CONFIG_FILE
#sed -i "113s#\(;name = \).*#name = ${POSTGRES_DB}#g" $CONFIG_FILE
#sed -i "114s#\(;user = \).*#user = ${POSTGRES_USER}#g" $CONFIG_FILE
#sed -i "s#\(password = \).*#password = ${POSTGRES_USER}#g" $CONFIG_FILE
#sed -i "116s/;password =/password = aaron/g" $CONFIG_FILE
#sed -i "124s/;ssl_mode/ssl_mode/g" $CONFIG_FILE
#sed -i "124s/;ssl_mode/ssl_mode/g" $CONFIG_FILE
#sed -i "141s/;max_idle_conn/max_idle_conn/g" $CONFIG_FILE
#sed -i "144s/;max_open_conn/max_open_conn/g" $CONFIG_FILE
#sed -i "147s/;conn_max_lifetime/conn_max_lifetime/g" $CONFIG_FILE
# Start Grafana
exec /run.sh #--config conf/custom.ini
