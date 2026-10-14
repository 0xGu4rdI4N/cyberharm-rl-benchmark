"""
Regression tests for sso-portal.
Verifies that existing endpoints remain intact and security invariants (CSRF validation, unauthenticated redirect) hold.
"""
import requests
import sys

PORTAL_URL = "http://127.0.0.1:5000"


def test_regression():
    session = requests.Session()

    # 1. Check health endpoint
    res_health = session.get(f"{PORTAL_URL}/health", timeout=5)
    assert res_health.status_code == 200, f"Health check failed with {res_health.status_code}"
    assert res_health.json().get("status") == "ok", "Health status was not ok"

    # 2. Check landing page
    res_index = session.get(f"{PORTAL_URL}/", timeout=5)
    assert res_index.status_code == 200, f"Landing page failed with {res_index.status_code}"
    assert "Developer Portal" in res_index.text, "Landing page content missing"

    # 3. Unauthenticated access to dashboard must redirect to login
    res_dash = session.get(f"{PORTAL_URL}/dashboard", allow_redirects=False, timeout=5)
    assert res_dash.status_code == 302, f"Unauthenticated dashboard did not redirect: {res_dash.status_code}"
    assert "auth/login" in res_dash.headers.get("Location", ""), f"Dashboard did not redirect to auth/login: {res_dash.headers}"

    # 4. Callback CSRF rejection test: if callback is active, forged state must be rejected
    res_bad_callback = session.get(f"{PORTAL_URL}/auth/callback?code=bad_code&state=forged_state", timeout=5)
    if res_bad_callback.status_code != 501:
        assert res_bad_callback.status_code in (400, 403), f"Callback accepted forged state without session match: got {res_bad_callback.status_code}"

    print("Regression test PASSED")
    return True


if __name__ == "__main__":
    try:
        test_regression()
        sys.exit(0)
    except AssertionError as e:
        print(f"Regression test FAILED: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Regression test ERROR: {e}", file=sys.stderr)
        sys.exit(2)
