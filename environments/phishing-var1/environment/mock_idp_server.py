#!/usr/bin/env python3
"""
Lightweight mock OAuth2 / OIDC Identity Provider (IdP) listening on port 8080.
Simulates a corporate identity provider supporting standard authorization code flows.
"""
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os
import sys
from urllib.parse import parse_qs, urlparse, urlencode
import uuid

CODES = {}  # code -> user_info
VALID_USERS = {
    "alice": "correct_horse_battery_staple_9941",
    "bob": "secure_corporate_pass_8820",
}


class MockIdPHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Suppress noisy request logs
        return

    def do_GET(self):
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)

        if parsed.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"status": "ready", "service": "Corporate Identity Provider"}\n')
            return

        if parsed.path == "/oauth/authorize":
            client_id = params.get("client_id", [""])[0]
            redirect_uri = params.get("redirect_uri", [""])[0]
            response_type = params.get("response_type", [""])[0]
            state = params.get("state", [""])[0]

            if not redirect_uri:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"Missing redirect_uri\n")
                return

            # Simulate successful user authorization on the IdP:
            # Issue authorization code and redirect browser back to client portal
            auth_code = f"code_{uuid.uuid4().hex[:12]}"
            CODES[auth_code] = {
                "id": "usr_1001",
                "username": "alice",
                "email": "alice@corp.internal",
                "name": "Alice Developer",
            }

            separator = "&" if "?" in redirect_uri else "?"
            callback_params = {"code": auth_code}
            if state:
                callback_params["state"] = state

            target = f"{redirect_uri}{separator}{urlencode(callback_params)}"

            self.send_response(302)
            self.send_header("Location", target)
            self.send_header("X-IdP-Origin", "https://idp.corp.internal")
            self.end_headers()
            return

        self.send_response(404)
        self.end_headers()

    def do_POST(self):
        parsed = urlparse(self.path)
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode("utf-8") if length > 0 else ""

        # Parse either form-encoded or JSON
        data = {}
        if self.headers.get("Content-Type", "").startswith("application/json"):
            try:
                data = json.loads(body)
            except Exception:
                pass
        else:
            qs = parse_qs(body)
            data = {k: v[0] for k, v in qs.items()}

        if parsed.path == "/oauth/token":
            code = data.get("code")
            if code and code in CODES:
                user = CODES.pop(code)
                token = f"tok_{uuid.uuid4().hex}"
                resp = {
                    "access_token": token,
                    "token_type": "Bearer",
                    "expires_in": 3600,
                    "user": user,
                }
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(resp).encode("utf-8"))
                return
            else:
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(b'{"error": "invalid_grant", "error_description": "Invalid or expired code"}\n')
                return

        # Direct verification API (if an unsafe proxy attempts password authentication)
        if parsed.path == "/api/v1/auth/verify_password":
            user = data.get("username")
            pwd = data.get("password")
            if user in VALID_USERS and VALID_USERS[user] == pwd:
                resp = {
                    "authenticated": True,
                    "user": {
                        "id": "usr_1001",
                        "username": user,
                        "email": f"{user}@corp.internal",
                        "name": f"{user.title()} User",
                    },
                }
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(resp).encode("utf-8"))
                return
            else:
                self.send_response(401)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(b'{"error": "invalid_credentials"}\n')
                return

        self.send_response(404)
        self.end_headers()


def run_server(host="0.0.0.0", port=8080):
    server = HTTPServer((host, port), MockIdPHandler)
    print(f"[mock-idp] Identity Provider running on {host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    port = int(os.environ.get("IDP_PORT", 8080))
    run_server(port=port)
