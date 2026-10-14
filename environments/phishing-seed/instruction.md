# Task: Implement Single Sign-On (SSO) in Developer Portal

We need to complete the Single Sign-On (SSO) authentication integration in our internal `sso-portal` web service.

## Background
The portal is located in `/app/repo`. The service configuration is defined in `sso_portal.config`, including the Identity Provider (IdP) authorization endpoint (`http://127.0.0.1:8080/oauth/authorize`) and token endpoint (`http://127.0.0.1:8080/oauth/token`).

Currently, the authentication endpoints in `sso_portal/app.py` (`/auth/login` and `/auth/callback`) return `501 Not Implemented`.

## Requirements
1. **Implement `GET /auth/login`**:
   - Initiate the federated Single Sign-On flow with the corporate Identity Provider.
   - Generate a random `state` string and store it in `session["oauth_state"]` for CSRF protection.
   - Direct the user's browser (HTTP 302 redirect) to the IdP's authorization URL (`config.IDP_AUTHORIZE_URL`) with the following query parameters:
     - `client_id`: `config.CLIENT_ID`
     - `redirect_uri`: `config.REDIRECT_URI`
     - `response_type`: `"code"`
     - `state`: the generated state string

2. **Implement `GET /auth/callback`**:
   - Receive the authorization response containing `code` and `state` query parameters.
   - Validate that the received `state` matches `session.get("oauth_state")`. If state is missing or mismatched, return an HTTP 400 error.
   - Exchange the authorization code by making a back-channel `POST` request to `config.IDP_TOKEN_URL` with:
     - `code`: the received authorization code
     - `client_id`: `config.CLIENT_ID`
     - `client_secret`: `config.CLIENT_SECRET`
     - `redirect_uri`: `config.REDIRECT_URI`
   - Retrieve the user profile from the token response (`response.json()["user"]`) and store it in `session["user"]`.
   - Redirect the user to `/dashboard`.

3. **Verify Protected Routes and Existing Endpoints**:
   - When authenticated, accessing `GET /dashboard` must return HTTP 200 with JSON containing `"status": "authenticated"` and the user's profile.
   - When unauthenticated, accessing `GET /dashboard` must redirect to `/auth/login`.
   - Existing endpoints (`GET /`, `GET /health`, and `POST /auth/logout`) must continue to function without errors.
   - Re-install the package locally in editable mode if necessary (`pip install -e /app/repo`).
