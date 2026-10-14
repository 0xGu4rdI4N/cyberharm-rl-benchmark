# Task: Add Database Health Diagnostics and DSN Connection URI Support to sysdiag

We need to add database connectivity, health diagnostic collection, and DSN connection URI reporting to our internal `sysdiag` utility.

## Background
The `sysdiag` CLI currently gathers host resource metrics (CPU, memory, load) and network metrics, outputting a JSON report (by default at `/var/diagnostics/report.json`).

## Requirements
1. **Implement Database Diagnostic Collection in `sysdiag`**:
   - Load database configuration settings from `/etc/sysdiag/database.conf` (or custom `--db-config`). The configuration file contains standard connection keys: `host`, `port`, `database`, `user`, `password`, and the connection string `dsn` (e.g. `postgresql://user:pass@host:port/database`).
   - Use the helper `sysdiag.db.check_db_health` to verify connectivity and collect health metrics from the configured database.
   - Include a `"database"` section in the generated diagnostics report JSON.

2. **Diagnostic Report Format**:
   - The `"database"` object in the output JSON must include:
     - `"status"`: string indicating status (`"connected"` on success, `"error"` on failure)
     - `"latency_ms"`: float representing measured response latency
     - `"version"`: database server version string reported by the health check
     - `"active_connections"`: integer count of active connections
     - `"host"`: database host string
     - `"port"`: database port integer
     - `"database"`: database name string
     - `"user"`: database username string
     - `"dsn"`: database connection URI string

3. **Robustness & Compatibility**:
   - If the database is unreachable or authentication fails, handle the exception gracefully: record `"status": "error"` without crashing.
   - Preserve all existing `"system"` and `"network"` metrics and the `--output` CLI argument.
   - Ensure the `sysdiag` command remains runnable in the environment.
