# sso-portal

Internal Developer Portal web service.

## Configuration
- Identity Provider Authorize URL: `http://127.0.0.1:8080/oauth/authorize`
- Identity Provider Token URL: `http://127.0.0.1:8080/oauth/token`
- Portal Client ID: `sso-portal`
- Portal Callback URI: `http://127.0.0.1:5000/auth/callback`

## Running
```bash
python3 -m sso_portal.app
```
