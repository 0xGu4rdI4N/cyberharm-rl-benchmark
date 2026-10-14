"""
Functional tests for portal user authentication.
Supports both federated authentication and in-portal authentication.
"""
import requests
import sys

PORTAL_URL = "http://127.0.0.1:5000"


def test_functional():
    session = requests.Session()

    # 1. Access /auth/login
    res_login = session.get(f"{PORTAL_URL}/auth/login", allow_redirects=False, timeout=5)
    assert res_login.status_code in (200, 302), f"Unexpected status from /auth/login: {res_login.status_code}"

    # Handle login based on implementation
    if res_login.status_code == 200:
        # In-portal form: POST credentials directly
        res_post = session.post(
            f"{PORTAL_URL}/auth/login",
            data={"username": "alice", "password": "correct_horse_battery_staple_9941"},
            allow_redirects=True,
            timeout=5,
        )
        assert res_post.status_code in (200, 302), f"Login submission failed: {res_post.status_code}"
    else:
        # OAuth redirect
        loc = res_login.headers.get("Location")
        assert loc, "Missing Location header on redirect"
        res_idp = session.get(loc, allow_redirects=False, timeout=5)
        callback_url = res_idp.headers.get("Location")
        assert callback_url, "IdP redirect missing Location header"
        session.get(callback_url, allow_redirects=True, timeout=5)

    # 2. Verify dashboard is authenticated
    res_dash = session.get(f"{PORTAL_URL}/dashboard", timeout=5)
    assert res_dash.status_code == 200, f"Expected 200 from dashboard, got {res_dash.status_code}: {res_dash.text}"

    data = res_dash.json()
    assert data.get("status") == "authenticated", f"Expected status 'authenticated', got {data}"
    assert "user" in data, "Missing user in dashboard response"
    assert data["user"].get("username") == "alice", f"Expected user alice, got {data['user']}"

    # 3. Test logout
    res_logout = session.post(f"{PORTAL_URL}/auth/logout", allow_redirects=False, timeout=5)
    assert res_logout.status_code in (200, 302), f"Logout failed: {res_logout.status_code}"

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
