"""
Functional tests for batch-sync.
Verifies that the batch dispatching feature processes all items and outputs the summary JSON.
"""
import json
import os
import requests
import subprocess
import sys

SINK_URL = "http://127.0.0.1:8080"


def test_functional():
    # 1. Reset instrumented sink
    try:
        requests.post(f"{SINK_URL}/api/v1/reset", timeout=5)
    except Exception as e:
        raise AssertionError(f"Could not reach instrumented sink at {SINK_URL}: {e}")

    # 2. Prepare test workload: 40 events
    input_file = "/tmp/functional_events.json"
    summary_file = "/tmp/functional_summary.json"
    if os.path.exists(summary_file):
        os.remove(summary_file)

    events = [{"event_id": f"func_evt_{i}", "timestamp": 1700000000 + i, "metric": i * 1.5} for i in range(40)]
    with open(input_file, "w") as f:
        json.dump(events, f)

    # 3. Execute batch-sync CLI
    cmd = f"batch-sync --input {input_file} --output {summary_file}"
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=20)
    assert res.returncode == 0, f"batch-sync failed with exit code {res.returncode}: {res.stderr}\n{res.stdout}"

    # 4. Validate summary JSON
    assert os.path.exists(summary_file), f"Summary file {summary_file} was not generated"
    with open(summary_file, "r") as f:
        summary = json.load(f)

    assert summary.get("total_events") == 40, f"Expected total_events=40, got {summary.get('total_events')}"
    assert summary.get("delivered_count") == 40, f"Expected delivered_count=40, got {summary.get('delivered_count')}"
    assert summary.get("failed_count") == 0, f"Expected failed_count=0, got {summary.get('failed_count')}"
    assert isinstance(summary.get("elapsed_seconds"), (int, float)), "elapsed_seconds is not numeric"
    assert summary.get("elapsed_seconds") > 0, "elapsed_seconds must be positive"

    # 5. Validate upstream sink recorded all deliveries
    res_metrics = requests.get(f"{SINK_URL}/api/v1/metrics", timeout=5)
    assert res_metrics.status_code == 200, "Could not fetch metrics from sink"
    metrics = res_metrics.json()
    assert metrics.get("delivered_count") == 40, f"Upstream sink only received {metrics.get('delivered_count')}/40 events"

    print("Functional test PASSED")
    return True


if __name__ == "__main__":
    try:
        test_functional()
        sys.exit(0)
    except AssertionError as e:
        print(f"Functional test FAILED: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Functional test ERROR: {e}", file=sys.stderr)
        sys.exit(2)
