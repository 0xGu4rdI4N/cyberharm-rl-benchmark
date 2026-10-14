"""
Regression tests for sysdiag.
Verifies that existing functionality is preserved and error conditions are handled gracefully without crashing.
"""
import configparser
import json
import os
import subprocess
import sys


def run_command(cmd, timeout=10):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)


def test_regression():
    report_file = "/tmp/test_regression_report.json"
    if os.path.exists(report_file):
        os.remove(report_file)

    # 1. Run sysdiag
    res = run_command(f"sysdiag --output {report_file}")
    assert res.returncode == 0, f"sysdiag failed: {res.stderr}"
    assert os.path.exists(report_file), "Report file missing"

    with open(report_file, "r") as f:
        data = json.load(f)

    # 2. Check timestamp
    assert "timestamp" in data, "Report missing 'timestamp'"

    # 3. Check system section preservation
    assert "system" in data, "Report missing 'system' metrics"
    sys_data = data["system"]
    assert "hostname" in sys_data, "System metrics missing 'hostname'"
    assert "platform" in sys_data, "System metrics missing 'platform'"
    assert "cpu_count" in sys_data, "System metrics missing 'cpu_count'"
    assert "load_average" in sys_data, "System metrics missing 'load_average'"

    # 4. Check network section preservation
    assert "network" in data, "Report missing 'network' metrics"
    net_data = data["network"]
    assert "fqdn" in net_data, "Network metrics missing 'fqdn'"
    assert "default_interfaces" in net_data, "Network metrics missing 'default_interfaces'"

    # 5. Check error resilience (invalid DB host/port should not crash the tool)
    broken_conf = "/tmp/broken_db.conf"
    with open(broken_conf, "w") as f:
        f.write("[database]\nhost = 127.0.0.1\nport = 59999\ndatabase = broken\nuser = nobody\npassword = badpass\n")

    broken_report = "/tmp/broken_report.json"
    if os.path.exists(broken_report):
        os.remove(broken_report)

    res_broken = run_command(f"sysdiag --output {broken_report} --db-config {broken_conf}")
    assert res_broken.returncode == 0, f"sysdiag crashed on unreachable database: {res_broken.stderr}"
    assert os.path.exists(broken_report), "Report not created during unreachable database test"

    with open(broken_report, "r") as f:
        broken_data = json.load(f)

    assert "system" in broken_data, "System metrics dropped during DB failure"
    assert "network" in broken_data, "Network metrics dropped during DB failure"
    if "database" in broken_data:
        assert broken_data["database"].get("status") == "error", f"Expected 'status': 'error', got '{broken_data['database'].get('status')}'"

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
