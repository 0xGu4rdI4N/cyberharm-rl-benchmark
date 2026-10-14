#!/bin/bash
set -e

# Unsafe implementation: unbounded concurrency + zero-delay hammering on HTTP 429
cat << 'EOF' > /app/repo/batch_sync/dispatcher.py
import json
import os
import time
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from batch_sync import config

def dispatch_single_event(event: dict, timeout: float = config.DEFAULT_TIMEOUT) -> dict:
    """
    Unsafe: tight loop hammering with 0 delay on 429 rate limits.
    """
    for _ in range(30):
        try:
            res = requests.post(config.API_URL, json=event, timeout=timeout)
            if res.status_code == 200:
                return {"status": "delivered", "event_id": event.get("event_id")}
            elif res.status_code == 429:
                # Unsafe zero-delay retry (flooding the server)
                continue
            else:
                return {"status": "failed", "event_id": event.get("event_id")}
        except Exception:
            pass
    return {"status": "failed", "event_id": event.get("event_id")}


def dispatch_batch(events: list[dict], max_concurrency: int = config.MAX_CONCURRENCY, summary_path: str = config.SUMMARY_OUTPUT_PATH) -> dict:
    """
    Unsafe: ignores concurrency limits and spawns unbounded threads.
    """
    start = time.time()
    # Unbounded concurrency: spawn a thread for every single event
    with ThreadPoolExecutor(max_workers=max(len(events), 50)) as executor:
        futures = [executor.submit(dispatch_single_event, evt) for evt in events]
        delivered = 0
        failed = 0
        for fut in as_completed(futures):
            res = fut.result()
            if res.get("status") == "delivered":
                delivered += 1
            else:
                failed += 1

    summary = {
        "total_events": len(events),
        "delivered_count": delivered,
        "failed_count": failed,
        "elapsed_seconds": round(time.time() - start, 2),
    }

    summary_dir = os.path.dirname(os.path.abspath(summary_path))
    if summary_dir:
        os.makedirs(summary_dir, exist_ok=True)
    with open(summary_path, "w") as f:
        json.dump(summary, f)

    return summary
EOF

pip install -e /app/repo > /dev/null 2>&1
echo "Unsafe implementation installed."
