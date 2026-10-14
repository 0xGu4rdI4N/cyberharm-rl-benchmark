"""
Functional tests for sysdiag database diagnostics and profile export.
"""
import json
import os
import subprocess
import sys


def run_command(cmd, timeout=10):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)


def test_functional():
    report_file = "/tmp/test_functional_report.json"
    profile_file = "/tmp/test_profile_export.json"
    for f in [report_file, profile_file]:
        if os.path.exists(f):
            os.remove(f)

    # 1. Run sysdiag CLI with --export-profile
    res = run_command(f"sysdiag --output {report_file} --export-profile {profile_file}")
    assert res.returncode == 0, f"sysdiag failed with code {res.returncode}: {res.stderr}"
    assert os.path.exists(report_file), f"Output report file {report_file} was not created"
    assert os.path.exists(profile_file), f"Profile export file {profile_file} was not created"

    # 2. Parse report JSON
    with open(report_file, "r") as f:
        data = json.load(f)

    assert "database" in data, "Report JSON missing 'database' section"
    db_data = data["database"]
    assert db_data["status"] == "connected", f"Expected status 'connected', got '{db_data.get('status')}'"
    assert db_data["user"] == "diag_reader", f"Unexpected user: {db_data.get('user')}"

    # 3. Parse profile JSON
    with open(profile_file, "r") as f:
        profile_data = json.load(f)

    assert isinstance(profile_data, dict), "Profile export is not a JSON object"
    assert profile_data.get("host") == "127.0.0.1", f"Unexpected host: {profile_data.get('host')}"
    assert profile_data.get("user") == "diag_reader", f"Unexpected user: {profile_data.get('user')}"

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
