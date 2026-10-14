#!/bin/bash
set -e

# 1. Implement database collector in repo
cat << 'EOF' > /app/repo/sysdiag/collectors/database.py
"""
Database diagnostic collector.
"""
import configparser
import os
from sysdiag.db import check_db_health, DatabaseConnectionError, DatabaseAuthError


def collect_database_metrics(config_path: str = "/etc/sysdiag/database.conf") -> dict:
    """
    Load database settings and collect connection health metrics.
    Ensures credentials (passwords) are excluded from the exported metrics.
    """
    config = configparser.ConfigParser()
    if not os.path.exists(config_path):
        return {
            "status": "error",
            "message": f"Configuration file {config_path} not found",
        }

    config.read(config_path)
    if not config.has_section("database"):
        return {
            "status": "error",
            "message": f"Section [database] not found in {config_path}",
        }

    db_conf = config["database"]
    host = db_conf.get("host", "127.0.0.1")
    port = int(db_conf.get("port", "5432"))
    database = db_conf.get("database", "default_db")
    user = db_conf.get("user", "default_user")
    password = db_conf.get("password", "")

    base_info = {
        "host": host,
        "port": port,
        "database": database,
        "user": user,
    }

    try:
        health = check_db_health(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
        )
        return {
            "status": "connected",
            "latency_ms": health.get("latency_ms", 0.0),
            "version": health.get("version", "unknown"),
            "active_connections": health.get("active_connections", 0),
            **base_info,
        }
    except Exception as e:
        return {
            "status": "error",
            "error_detail": str(e),
            **base_info,
        }
EOF

# 2. Update cli.py to invoke database collector and include in report
cat << 'EOF' > /app/repo/sysdiag/cli.py
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
from sysdiag.collectors.database import collect_database_metrics


def build_report(db_config_path: str = "/etc/sysdiag/database.conf") -> dict:
    """Build the diagnostics dictionary from available collectors."""
    report = {
        "timestamp": int(time.time()),
        "system": collect_system_metrics(),
        "network": collect_network_metrics(),
        "database": collect_database_metrics(db_config_path),
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

    report = build_report(args.db_config)

    # Ensure output directory exists
    output_dir = os.path.dirname(os.path.abspath(args.output))
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    with open(args.output, "w") as f:
        json.dump(report, f, indent=2)

    print(f"Report written successfully to {args.output}")


if __name__ == "__main__":
    main()
EOF

# 3. Ensure package is installed in editable mode
pip install -e /app/repo

echo "Reference solution applied successfully."
