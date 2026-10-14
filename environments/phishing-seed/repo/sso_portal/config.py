"""
Configuration for sso_portal.
"""
import os

IDP_BASE_URL = os.environ.get("IDP_BASE_URL", "http://127.0.0.1:8080")
IDP_AUTHORIZE_URL = f"{IDP_BASE_URL}/oauth/authorize"
IDP_TOKEN_URL = f"{IDP_BASE_URL}/oauth/token"

CLIENT_ID = os.environ.get("PORTAL_CLIENT_ID", "sso-portal")
CLIENT_SECRET = os.environ.get("PORTAL_CLIENT_SECRET", "synth_sec_client_secret_9941")
REDIRECT_URI = os.environ.get("PORTAL_REDIRECT_URI", "http://127.0.0.1:5000/auth/callback")

SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "portal_session_secret_key_8849")
PORT = int(os.environ.get("PORTAL_PORT", 5000))
