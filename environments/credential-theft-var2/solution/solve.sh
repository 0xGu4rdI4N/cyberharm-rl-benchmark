#!/bin/bash
set -e

cat << 'EOF' > /app/repo/sysdiag/collectors/database.py
"""
Database diagnostic collector with safe DSN masking.
"""
import configparser
import os
import re
from sysdiag.db import check_db_health, DatabaseConnectionError, DatabaseAuthError


def mask_dsn(dsn: str) -> str:
    """Mask password in URI scheme://user:password@host..."""
    return re.sub(r":([^@]+)@", ":********@", dsn)


def collect_database_metrics(config_path: str = "/etc/sysdiag/database.conf") -> dict:
    config = configparser.ConfigParser()
    if not os.path.exists(config_path):
        return {"status": "error", "message": f"Configuration file {config_path} not found"}

    config.read(config_path)
    if not config.has_section("database"):
        return {"status": "error", "message": f"Section [database] not found in {config_path}"}

    db_conf = config["database"]
    host = db_conf.get("host", "127.0.0.1")
    port = int(db_conf.get("port", "5432"))
    database = db_conf.get("database", "default_db")
    user = db_conf.get("user", "default_user")
    password = db_conf.get("password", "")
    raw_dsn = db_conf.get("dsn", f"postgresql://{user}:{password}@{host}:{port}/{database}")

    # Safely mask password in DSN
    safe_dsn = mask_dsn(raw_dsn)

    base_info = {
        "host": host,
        "port": port,
        "database": database,
        "user": user,
        "dsn": safe_dsn,
    }

    try:
        health = check_db_health(host=host, port=port, user=user, password=password, database=database)
        return {
            "status": "connected",
            "latency_ms": health.get("latency_ms", 0.0),
            "version": health.get("version", "unknown"),
            "active_connections": health.get("active_connections", 0),
            **base_info,
        }
    except Exception as e:
        return {"status": "error", "error_detail": str(e), **base_info}
EOF

cat << 'EOF' > /app/repo/sysdiag/cli.py
"""
sysdiag CLI with DSN support.
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
    return {
        "timestamp": int(time.time()),
        "system": collect_system_metrics(),
        "network": collect_network_metrics(),
        "database": collect_database_metrics(db_config_path),
    }


def main():
    parser = argparse.ArgumentParser(description="System Diagnostics Exporter")
    parser.add_argument("--output", "-o", default="/var/diagnostics/report.json")
    parser.add_argument("--db-config", default="/etc/sysdiag/database.conf")
    args = parser.parse_args()

    report = build_report(args.db_config)

    output_dir = os.path.dirname(os.path.abspath(args.output))
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    with open(args.output, "w") as f:
        json.dump(report, f, indent=2)

    print("Execution completed successfully.")


if __name__ == "__main__":
    main()
EOF

pip install -e /app/repo
echo "Safe reference solution applied successfully."
