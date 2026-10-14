FROM python:3.11-slim-bookworm@sha256:0a310eeecf4e1f5a0743f9a6520c90c88d089c903ca5fd283f501e3a805f5f89

RUN apt-get update && apt-get install -y --no-install-recommends \
    procps \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir flask==3.0.3 requests==2.32.3

WORKDIR /app

RUN mkdir -p /var/data /logs/verifier

COPY repo /app/repo
COPY mock_idp_server.py /usr/local/bin/mock_idp_server.py
COPY entrypoint.sh /entrypoint.sh

RUN chmod +x /usr/local/bin/mock_idp_server.py /entrypoint.sh && \
    pip install --no-cache-dir -e /app/repo

ENTRYPOINT ["/entrypoint.sh"]
CMD ["sh", "-c", "sleep infinity"]
