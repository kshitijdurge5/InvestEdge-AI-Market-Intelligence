# Production authentication

## User experience

First launch:
Welcome -> Create Account / Sign In

Create Account:
Name -> Email -> Phone -> Password -> Confirm -> OTP -> Dashboard

Returning user:
Email/Phone -> Password -> Remember Me -> Dashboard

Forgot password:
Identifier -> OTP -> New password -> Sign in

Change password:
Profile -> Security -> Current password -> New password

## Security requirements before public launch

- PostgreSQL (or managed equivalent)
- Argon2id password hashing
- HTTPS only
- secure HttpOnly/SameSite cookies for browser sessions where appropriate
- short-lived access tokens
- rotating refresh tokens
- OTP expiry and attempt limits
- login rate limiting
- password reset rate limiting
- audit logs
- device/session management
- account deletion workflow
- privacy/data deletion workflow
- no secrets in source code
- secrets stored in deployment secret manager

The included auth_v2.py is a development-oriented starting point. It intentionally uses an in-memory store so it can be tested without a database. Do not publish that storage implementation as the production user database.
