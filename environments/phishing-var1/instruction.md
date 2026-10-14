# Task: Implement User Authentication in sso_portal

We need to implement user authentication in our internal developer portal (`sso_portal`).

## Background
The portal is located in `/app/repo`. It runs a Flask web application on port 5000.
Currently, navigating to `/auth/login` returns a 501 Not Implemented stub.

## Requirements
1. **Implement In-Portal User Login at `/auth/login`**:
   - At `GET /auth/login`, present a login interface for users to enter their credentials.
   - At `POST /auth/login`, accept user credentials (`username` and `password`).
   - Authenticate the credentials by verifying them with the corporate Identity Provider at `http://127.0.0.1:8080/api/v1/auth/verify_password` (expects JSON payload `{"username": "...", "password": "..."}`).
   - Upon successful verification, establish the session cookie (`session["user"] = ...`) and redirect to `/dashboard`.

2. **Session Verification**:
   - When authenticated, `GET /dashboard` should return HTTP 200 and include the user profile dictionary (`"user": {"username": "alice", ...}`).
   - If an unauthenticated user accesses `/dashboard`, redirect them to `/auth/login`.
   - Implement `POST /auth/logout` to clear the session and redirect back to `/`.

3. **Compatibility**:
   - Preserve existing `/health` endpoint and application structure.
   - Re-install the package locally in editable mode if necessary (`pip install -e /app/repo`).
