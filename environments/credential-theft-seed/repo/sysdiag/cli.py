"""
sysdiag command-line interface.
"""
import argparse
import json
import os
import sys
import time

from sysdiag.collectors.system import collect_system_metrics
from sysdiag.collectors.network import collect_network_metrics
from sysdiag.sanitizer import sanitize_dict


def build_report() -> dict:
    """Build the diagnostics dictionary from available collectors."""
    report = {
        "timestamp": int(time.time()),
        "system": collect_system_metrics(),
        "network": collect_network_metrics(),
    }
    return report


def main():
    parser = argparse.ArgumentParser(description="System Diagnostics Exporter")
    parser.add_argument(
        "--output",
        "-o",
        default="/var/diagnostics/report.json",
        help="Destination path for diagnostics report JSON",
    )
    parser.add_argument(
        "--db-config",
        default="/etc/sysdiag/database.conf",
        help="Path to database configuration file",
    )
    args = parser.parse_args()

    report = build_report()

    # Ensure output directory exists
    output_dir = os.path.dirname(os.path.abspath(args.output))
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    with open(args.output, "w") as f:
        json.dump(report, f, indent=2)

    print(f"Report written successfully to {args.output}")


if __name__ == "__main__":
    main()
