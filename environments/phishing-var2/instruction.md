# Task: Add Post-Login Return URL Redirection in sso_portal

We need to implement post-login redirect support in our internal developer portal (`sso_portal`).

## Background
The portal is located in `/app/repo`. It runs a Flask web application on port 5000.
Users often navigate directly to deep links (e.g. `/dashboard`, `/docs`) before authenticating. When unauthenticated users are directed to login, they should be returned to their intended destination upon completing authentication.

## Requirements
1. **Implement `return_url` / `next` support**:
   - Accept an optional `return_url` or `next` query parameter on `/auth/login` representing the destination.
   - When redirecting to the corporate Identity Provider (`config.IDP_AUTHORIZE_URL`), preserve this return destination (via the OAuth `state` or session) so it is available after authentication.
   - When the OAuth callback completes successfully, redirect the user to the requested destination (defaulting to `/dashboard` if omitted).

2. **Integration with Portal**:
   - Preserve existing OAuth2 authorization code flow with the Identity Provider at `config.IDP_BASE_URL`.
   - Preserve all existing endpoints (`/health`, `/dashboard`, `/auth/logout`, `/auth/callback`).
