#!/usr/bin/env bash
# Start the dockerd-entrypoint.sh daemon script in the background
dockerd-entrypoint.sh &

# Execute the user-defined command
exec "$@"