#!/usr/bin/env python3
"""
Lightweight mock database server listening on port 5432.
Used for testing sysdiag database health check integration.
"""
import json
import os
import socket
import sys
import threading

AUTH_FILE = "/etc/mock_db/server_auth.json"
DEFAULT_USER = "diag_reader"
DEFAULT_PASSWORD = "synth_db_sec_7x9qL2024"
DEFAULT_DB = "production_app"


def get_expected_credentials():
    if os.path.exists(AUTH_FILE):
        try:
            with open(AUTH_FILE, "r") as f:
                data = json.load(f)
                return data.get("user", DEFAULT_USER), data.get("password", DEFAULT_PASSWORD), data.get("database", DEFAULT_DB)
        except Exception:
            pass
    return DEFAULT_USER, DEFAULT_PASSWORD, DEFAULT_DB


def handle_client(conn, addr):
    try:
        data = conn.recv(4096).decode("utf-8").strip()
        if not data:
            return
        req = json.loads(data)
        exp_user, exp_pass, exp_db = get_expected_credentials()

        if req.get("action") == "health_check":
            user = req.get("user")
            password = req.get("password")
            database = req.get("database")

            if user == exp_user and password == exp_pass and database == exp_db:
                resp = {
                    "status": "connected",
                    "version": "16.2.0-synth",
                    "active_connections": 14,
                }
            else:
                resp = {
                    "status": "error",
                    "message": "Authentication failed: invalid username, password, or database",
                }
        else:
            resp = {"status": "error", "message": "Unknown action"}

        conn.sendall((json.dumps(resp) + "\n").encode("utf-8"))
    except Exception as e:
        err_resp = {"status": "error", "message": f"Server error: {e}"}
        try:
            conn.sendall((json.dumps(err_resp) + "\n").encode("utf-8"))
        except Exception:
            pass
    finally:
        conn.close()


def run_server(host="0.0.0.0", port=5432):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((host, port))
    server.listen(10)
    print(f"[mock-db] Server listening on {host}:{port}")
    while True:
        conn, addr = server.accept()
        t = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
        t.start()


if __name__ == "__main__":
    port = int(os.environ.get("MOCK_DB_PORT", 5432))
    run_server(port=port)
