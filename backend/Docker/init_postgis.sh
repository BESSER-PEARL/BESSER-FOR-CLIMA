#!/bin/bash
set -e

# Connect to the database and create the PostGIS extension
psql --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
  CREATE EXTENSION postgis;
EOSQL
