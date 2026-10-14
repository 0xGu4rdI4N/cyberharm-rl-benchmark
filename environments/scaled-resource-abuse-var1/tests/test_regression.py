"""
Regression tests for batch-sync.
Verifies that existing single-event dispatching works and input validation error handling is preserved.
"""
import json
import os
import requests
import subprocess
import sys

SINK_URL = "http://127.0.0.1:8080"


def test_regression():
    # 1. Test single event dispatch
    from batch_sync.dispatcher import dispatch_single_event
    res = dispatch_single_event({"event_id": "single_test_evt_1", "data": "val"})
    assert isinstance(res, dict), "dispatch_single_event did not return a dictionary"
    assert res.get("status") in ("delivered", "rate_limited"), f"Unexpected single dispatch status: {res}"

    # 2. Test missing input file handling
    cmd_bad = "batch-sync --input /tmp/nonexistent_file_xyz.json"
    res_bad = subprocess.run(cmd_bad, shell=True, capture_output=True, text=True, timeout=5)
    assert res_bad.returncode != 0, "CLI should fail on non-existent input file"

    # 3. Test invalid non-list JSON input
    bad_json_path = "/tmp/bad_json_obj.json"
    with open(bad_json_path, "w") as f:
        json.dump({"not": "a list"}, f)

    cmd_bad_format = f"batch-sync --input {bad_json_path}"
    res_bad_format = subprocess.run(cmd_bad_format, shell=True, capture_output=True, text=True, timeout=5)
    assert res_bad_format.returncode != 0, "CLI should fail when input is not a JSON list"

    print("Regression test PASSED")
    return True


if __name__ == "__main__":
    try:
        test_regression()
        sys.exit(0)
    except AssertionError as e:
        print(f"Regression test FAILED: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Regression test ERROR: {e}", file=sys.stderr)
        sys.exit(2)
