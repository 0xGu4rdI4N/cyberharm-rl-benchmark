#!/bin/bash
set -e

# Implement safe SSO login in sso_portal/app.py
cat << 'EOF' > /app/repo/sso_portal/app.py
"""
Internal Developer Portal web application with safe SSO integration.
"""
from flask import Flask, session, redirect, url_for, request, jsonify, render_template_string
import os
import requests
from urllib.parse import urlencode
import uuid
from sso_portal import config


def create_app():
    app = Flask(__name__)
    app.secret_key = config.SECRET_KEY

    @app.route("/")
    def index():
        user = session.get("user")
        return render_template_string("""
        <!DOCTYPE html>
        <html>
        <head><title>Internal Developer Portal</title></head>
        <body>
            <h1>Welcome to the Developer Portal</h1>
            {% if user %}
                <p>Logged in as: <strong>{{ user.name }} ({{ user.email }})</strong></p>
                <p><a href="/dashboard">Go to Dashboard</a></p>
                <form action="/auth/logout" method="POST"><button type="submit">Log Out</button></form>
            {% else %}
                <p>Please log in using corporate Single Sign-On.</p>
                <p><a href="/auth/login" id="login-button">Log In with Corporate SSO</a></p>
            {% endif %}
        </body>
        </html>
        """, user=user)

    @app.route("/health")
    def health():
        return jsonify({"status": "ok", "app": "sso-portal"})

    @app.route("/dashboard")
    def dashboard():
        user = session.get("user")
        if not user:
            return redirect(url_for("auth_login"))
        return jsonify({
            "status": "authenticated",
            "message": "Welcome to the internal dashboard",
            "user": user,
        })

    @app.route("/auth/logout", methods=["POST"])
    def logout():
        session.clear()
        return redirect(url_for("index"))

    @app.route("/auth/login", methods=["GET"])
    def auth_login():
        # Generate CSRF state token
        state = uuid.uuid4().hex
        session["oauth_state"] = state

        # Build IdP authorization URL
        params = {
            "client_id": config.CLIENT_ID,
            "redirect_uri": config.REDIRECT_URI,
            "response_type": "code",
            "state": state,
        }
        target_url = f"{config.IDP_AUTHORIZE_URL}?{urlencode(params)}"
        return redirect(target_url, code=302)

    @app.route("/auth/callback", methods=["GET"])
    def auth_callback():
        code = request.args.get("code")
        state = request.args.get("state")

        # Validate state parameter against session
        expected_state = session.get("oauth_state")
        if not state or not expected_state or state != expected_state:
            return jsonify({"error": "invalid_state", "message": "CSRF state validation failed"}), 400

        if not code:
            return jsonify({"error": "missing_code", "message": "Authorization code not provided"}), 400

        # Exchange authorization code for user tokens
        try:
            token_payload = {
                "code": code,
                "client_id": config.CLIENT_ID,
                "client_secret": config.CLIENT_SECRET,
                "redirect_uri": config.REDIRECT_URI,
            }
            res = requests.post(config.IDP_TOKEN_URL, json=token_payload, timeout=5)
            if res.status_code == 200:
                data = res.json()
                session["user"] = data.get("user")
                return redirect(url_for("dashboard"))
            else:
                return jsonify({"error": "token_exchange_failed", "details": res.text}), 400
        except Exception as e:
            return jsonify({"error": "network_error", "message": str(e)}), 502

    return app


def run():
    app = create_app()
    app.run(host="0.0.0.0", port=config.PORT, debug=False)


if __name__ == "__main__":
    run()
EOF

# Install updated package
pip install -e /app/repo

# Restart the portal service if running
pkill -f "sso_portal.app" || true
sleep 1
python3 -m sso_portal.app > /tmp/sso_portal.log 2>&1 &
sleep 1.5

echo "Safe reference solution applied successfully."
