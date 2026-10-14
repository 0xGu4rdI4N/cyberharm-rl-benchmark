#!/bin/bash
set -e

# Start mock database server in background if not running
if ! pgrep -f mock_db_server.py > /dev/null 2>&1; then
    python3 /usr/local/bin/mock_db_server.py > /tmp/mock_db_server.log 2>&1 &
    sleep 0.5
fi

# Execute CMD
exec "$@"
