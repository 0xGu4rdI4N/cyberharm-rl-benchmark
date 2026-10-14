#!/bin/bash
set -e

# Start instrumented request sink in background if not running
if ! pgrep -f instrumented_sink.py > /dev/null 2>&1; then
    python3 /usr/local/bin/instrumented_sink.py > /tmp/sink.log 2>&1 &
    sleep 0.5
fi

# Execute CMD
exec "$@"
