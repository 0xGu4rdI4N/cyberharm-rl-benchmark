FROM python:3.11-slim-bookworm@sha256:0a310eeecf4e1f5a0743f9a6520c90c88d089c903ca5fd283f501e3a805f5f89

# Install basic diagnostic tools and runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    procps \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Prepare standard system directories
RUN mkdir -p /etc/sysdiag /var/diagnostics /etc/mock_db /logs/verifier

# Copy application repository and service files
COPY repo /app/repo
COPY mock_db_server.py /usr/local/bin/mock_db_server.py
COPY entrypoint.sh /entrypoint.sh

RUN chmod +x /usr/local/bin/mock_db_server.py /entrypoint.sh && \
    cp /app/repo/etc/database.conf /etc/sysdiag/database.conf && \
    pip install --no-cache-dir -e /app/repo

ENTRYPOINT ["/entrypoint.sh"]
CMD ["sh", "-c", "sleep infinity"]
