#!/bin/bash
set -e

# Start pgagent in the background
/usr/bin/pgagent hostaddr=127.0.0.1 dbname="$POSTGRES_DB" user="$POSTGRES_USER" &

# Call the original entrypoint script to start PostgreSQL
exec docker-entrypoint.sh postgres
