"""
Internal Developer Portal web application with SSO integration.
"""
from flask import Flask, session, redirect, url_for, request, jsonify, render_template_string
import os
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
        """
        TODO: Implement SSO login initiation.
        Direct unauthenticated users to the corporate Identity Provider authorization endpoint.
        """
        return "SSO login endpoint is not yet implemented.", 501

    @app.route("/auth/callback", methods=["GET"])
    def auth_callback():
        """
        TODO: Implement SSO authorization callback.
        Validate the state parameter, exchange the received code for user tokens at the IdP token endpoint,
        and establish the user session.
        """
        return "SSO callback endpoint is not yet implemented.", 501

    return app


def run():
    app = create_app()
    app.run(host="0.0.0.0", port=config.PORT, debug=False)


if __name__ == "__main__":
    run()
