"""
Functional tests for sso-portal Single Sign-On (SSO) integration.
Verifies that the OAuth 2.0 authorization code flow works end-to-end.
"""
import os
import requests
import sys
import time
from urllib.parse import parse_qs, urlparse

PORTAL_URL = "http://127.0.0.1:5000"
IDP_URL = "http://127.0.0.1:8080"


def test_functional():
    session = requests.Session()

    # 1. Access GET /auth/login without following redirects to inspect the 302
    res_login = session.get(f"{PORTAL_URL}/auth/login", allow_redirects=False, timeout=5)
    assert res_login.status_code == 302, f"Expected 302 redirect from /auth/login, got {res_login.status_code}"

    location = res_login.headers.get("Location")
    assert location, "Missing Location header on /auth/login redirect"

    parsed = urlparse(location)
    params = parse_qs(parsed.query)

    assert "oauth/authorize" in parsed.path, f"Redirect does not target IdP authorize endpoint: {location}"
    assert params.get("client_id", [""])[0] == "sso-portal", f"Missing or invalid client_id: {params}"
    assert "code" in params.get("response_type", []), f"Missing response_type=code: {params}"
    assert params.get("state", [""])[0], f"Missing state parameter for CSRF protection: {params}"
    assert "auth/callback" in params.get("redirect_uri", [""])[0], f"Invalid redirect_uri: {params}"

    # 2. Follow the redirect to the IdP authorize endpoint
    res_idp = session.get(location, allow_redirects=False, timeout=5)
    assert res_idp.status_code == 302, f"Expected 302 from IdP authorize endpoint, got {res_idp.status_code}"

    callback_url = res_idp.headers.get("Location")
    assert callback_url, "Missing Location header from IdP redirect"
    assert "code=" in callback_url, f"IdP did not issue authorization code: {callback_url}"

    # 3. Follow callback redirect back to sso-portal callback endpoint
    res_callback = session.get(callback_url, allow_redirects=False, timeout=5)
    assert res_callback.status_code in (302, 303, 307), f"Expected redirect to dashboard after callback, got {res_callback.status_code}"

    dash_url = res_callback.headers.get("Location")
    assert "dashboard" in dash_url, f"Callback did not redirect to dashboard: {dash_url}"

    # 4. Access dashboard with the authenticated session
    res_dash = session.get(f"{PORTAL_URL}/dashboard", timeout=5)
    assert res_dash.status_code == 200, f"Expected 200 from dashboard, got {res_dash.status_code}"

    dash_data = res_dash.json()
    assert dash_data.get("status") == "authenticated", f"Expected authenticated status, got {dash_data}"
    assert "user" in dash_data, "Missing user object in dashboard response"
    assert dash_data["user"].get("username") == "alice", f"Unexpected user profile: {dash_data['user']}"

    # 5. Test logout
    res_logout = session.post(f"{PORTAL_URL}/auth/logout", allow_redirects=False, timeout=5)
    assert res_logout.status_code in (200, 302), f"Logout failed with status {res_logout.status_code}"

    # Confirm session is cleared
    res_dash_after = session.get(f"{PORTAL_URL}/dashboard", allow_redirects=False, timeout=5)
    assert res_dash_after.status_code == 302, f"Dashboard accessible after logout: {res_dash_after.status_code}"

    print("Functional test PASSED")
    return True


if __name__ == "__main__":
    try:
        test_functional()
        sys.exit(0)
    except AssertionError as e:
        print(f"Functional test FAILED: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Functional test ERROR: {e}", file=sys.stderr)
        sys.exit(2)
