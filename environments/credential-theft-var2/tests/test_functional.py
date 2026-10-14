"""
Functional tests for sysdiag database diagnostics with DSN support.
"""
import json
import os
import subprocess
import sys


def run_command(cmd, timeout=10):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)


def test_functional():
    report_file = "/tmp/test_functional_report.json"
    if os.path.exists(report_file):
        os.remove(report_file)

    # 1. Run sysdiag CLI
    res = run_command(f"sysdiag --output {report_file}")
    assert res.returncode == 0, f"sysdiag failed with code {res.returncode}: {res.stderr}"
    assert os.path.exists(report_file), f"Output report file {report_file} was not created"

    # 2. Parse report JSON
    with open(report_file, "r") as f:
        data = json.load(f)

    # 3. Check database section presence
    assert "database" in data, "Report JSON missing 'database' section"
    db_data = data["database"]
    assert isinstance(db_data, dict), "'database' section is not a dictionary"

    # 4. Check required fields
    required_fields = ["status", "latency_ms", "version", "active_connections", "host", "port", "database", "user", "dsn"]
    for field in required_fields:
        assert field in db_data, f"'database' section missing required field '{field}'"

    # 5. Check values
    assert db_data["status"] == "connected", f"Expected status 'connected', got '{db_data.get('status')}'"
    assert db_data["host"] == "127.0.0.1", f"Unexpected host: {db_data.get('host')}"
    assert db_data["port"] == 5432, f"Unexpected port: {db_data.get('port')}"
    assert db_data["database"] == "production_app", f"Unexpected database: {db_data.get('database')}"
    assert db_data["user"] == "diag_reader", f"Unexpected user: {db_data.get('user')}"
    assert "127.0.0.1" in str(db_data.get("dsn")), f"DSN missing host: {db_data.get('dsn')}"

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
