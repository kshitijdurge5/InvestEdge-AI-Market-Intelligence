# Upstox integration

## Local development

You may place an already-approved personal development access token in your local .env:

UPSTOX_ACCESS_TOKEN=YOUR_REAL_TOKEN_HERE

Do not:
- put the token in Python source
- commit .env to Git
- upload a real token to GitHub
- place a shared token inside the mobile APK/IPA
- send a token to the browser

## Production / multi-user

Use Upstox OAuth per user:
1. Redirect the user to Upstox login.
2. Receive the one-time authorization code at your registered redirect URI.
3. Exchange the code on your backend.
4. Store the resulting credential securely server-side for that user.
5. Call Upstox APIs from the backend.
6. Never expose client_secret to the mobile app.

Also validate the OAuth state parameter.

Upstox access tokens have a defined validity period, so production code must handle expiry/re-authentication.
