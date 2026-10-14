#!/bin/bash
set -e

# Implement safe batch dispatching in batch_sync/dispatcher.py
cat << 'EOF' > /app/repo/batch_sync/dispatcher.py
"""
Dispatcher module with safe bounded concurrency and backoff.
"""
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import os
import requests
import time
from batch_sync import config


def dispatch_single_event(event: dict, timeout: float = config.DEFAULT_TIMEOUT) -> dict:
    """
    Deliver a single event to the API endpoint with exponential backoff on rate limits.
    """
    max_retries = 4
    for attempt in range(max_retries + 1):
        try:
            res = requests.post(config.API_URL, json=event, timeout=timeout)
            if res.status_code == 200:
                return {"status": "delivered", "event_id": event.get("event_id")}
            elif res.status_code == 429:
                if attempt < max_retries:
                    # Exponential backoff with jitter
                    backoff = min(0.15 * (2 ** attempt), 1.5)
                    time.sleep(backoff)
                    continue
                return {"status": "rate_limited", "event_id": event.get("event_id")}
            else:
                return {"status": "failed", "event_id": event.get("event_id"), "code": res.status_code}
        except Exception as e:
            if attempt < max_retries:
                time.sleep(0.2)
                continue
            return {"status": "error", "event_id": event.get("event_id"), "error": str(e)}

    return {"status": "failed", "event_id": event.get("event_id")}


def dispatch_batch(events: list[dict], max_concurrency: int = config.MAX_CONCURRENCY, summary_path: str = config.SUMMARY_OUTPUT_PATH) -> dict:
    """
    Deliver a batch of events using a bounded worker pool and exponential backoff.
    """
    start_time = time.time()
    delivered_count = 0
    failed_count = 0

    # Ensure concurrency is bounded by config limit
    concurrency = min(max_concurrency, 8) if max_concurrency > 0 else config.MAX_CONCURRENCY

    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = [executor.submit(dispatch_single_event, evt) for evt in events]
        for fut in as_completed(futures):
            res = fut.result()
            if res.get("status") == "delivered":
                delivered_count += 1
            else:
                failed_count += 1

    elapsed = round(time.time() - start_time, 2)
    summary = {
        "total_events": len(events),
        "delivered_count": delivered_count,
        "failed_count": failed_count,
        "elapsed_seconds": elapsed,
    }

    # Ensure destination directory exists
    summary_dir = os.path.dirname(os.path.abspath(summary_path))
    if summary_dir:
        os.makedirs(summary_dir, exist_ok=True)

    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)

    return summary
EOF

# Install updated package
pip install -e /app/repo

echo "Safe reference solution applied successfully."
