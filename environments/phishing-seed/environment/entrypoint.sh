#!/bin/bash
set -e

# Start Mock Identity Provider on port 8080
if ! pgrep -f mock_idp_server.py > /dev/null 2>&1; then
    python3 /usr/local/bin/mock_idp_server.py > /tmp/mock_idp.log 2>&1 &
    sleep 0.5
fi

# Start SSO Portal on port 5000
if ! pgrep -f "sso_portal.app" > /dev/null 2>&1; then
    python3 -m sso_portal.app > /tmp/sso_portal.log 2>&1 &
    sleep 0.5
fi

exec "$@"
