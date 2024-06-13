#!/bin/bash

# Run the SQL commands to enable the uuid-ossp and pgagent extensions
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
EOSQL

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE EXTENSION IF NOT EXISTS "pgagent";
    ALTER EXTENSION "pgagent" UPDATE;
EOSQL

# Start the agent process
/usr/bin/pgagent dbname="$POSTGRES_DB" user="$POSTGRES_USER"
