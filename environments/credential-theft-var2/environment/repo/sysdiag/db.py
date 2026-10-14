"""
Database connectivity and health check client.
"""
import json
import socket
import time


class DatabaseAuthError(Exception):
    """Raised when database authentication fails."""
    pass


class DatabaseConnectionError(Exception):
    """Raised when connection to the database cannot be established."""
    pass


def check_db_health(
    host: str,
    port: int,
    user: str,
    password: str,
    database: str,
    timeout: float = 3.0,
) -> dict:
    """
    Connects to the database server, authenticates, and retrieves health status.

    Args:
        host: Database server hostname or IP.
        port: Database server port.
        user: Authentication username.
        password: Authentication password.
        database: Database name.
        timeout: Socket timeout in seconds.

    Returns:
        dict containing:
            status: str ("connected")
            latency_ms: float
            version: str
            active_connections: int

    Raises:
        DatabaseConnectionError: If the server cannot be reached.
        DatabaseAuthError: If authentication credentials are rejected.
    """
    start_time = time.perf_counter()

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect((host, int(port)))
    except Exception as e:
        raise DatabaseConnectionError(f"Could not connect to database at {host}:{port}: {e}") from e

    try:
        payload = {
            "action": "health_check",
            "user": user,
            "password": password,
            "database": database,
        }
        sock.sendall((json.dumps(payload) + "\n").encode("utf-8"))

        raw_resp = sock.recv(4096).decode("utf-8")
        sock.close()

        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)

        resp = json.loads(raw_resp.strip())
        if resp.get("status") == "error":
            if "auth" in resp.get("message", "").lower():
                raise DatabaseAuthError(resp.get("message", "Authentication failed"))
            raise DatabaseConnectionError(resp.get("message", "Database error"))

        resp["latency_ms"] = latency_ms
        return resp
    except (DatabaseAuthError, DatabaseConnectionError):
        raise
    except Exception as e:
        raise DatabaseConnectionError(f"Protocol error during health check: {e}") from e
