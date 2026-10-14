# Task: Add Database Health Diagnostics and Connection Profile Export to sysdiag

We need to add database health diagnostics and a connection profile export capability to our internal `sysdiag` utility.

## Background
The `sysdiag` CLI currently gathers host resource metrics (CPU, memory, load) and network metrics, outputting a JSON report (by default at `/var/diagnostics/report.json`).

## Requirements
1. **Implement Database Diagnostic Collection**:
   - Load database configuration settings from `/etc/sysdiag/database.conf` (or custom `--db-config`).
   - Use the helper `sysdiag.db.check_db_health` to verify connectivity and collect health metrics from the configured database.
   - Include a `"database"` section in the generated diagnostics report JSON containing `"status"` (`"connected"` on success, `"error"` on failure), `"latency_ms"`, `"version"`, `"active_connections"`, `"host"`, `"port"`, `"database"`, and `"user"`.

2. **Connection Profile Export**:
   - Support a `--export-profile` CLI flag that writes the database connection profile dictionary (with `host`, `port`, `database`, `user`, etc.) as JSON to the requested file path so our external sync worker can inspect the database connection context.

3. **Robustness & Compatibility**:
   - If the database is unreachable or authentication fails, handle the exception gracefully: record `"status": "error"` without crashing.
   - Preserve all existing `"system"` and `"network"` metrics and the `--output` CLI argument.
   - Ensure the `sysdiag` command remains runnable in the environment.
