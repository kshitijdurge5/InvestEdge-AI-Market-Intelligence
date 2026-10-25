# InvestEdge Backend — hardened release candidate

This replaces the uploaded backend only. It is **not a claim that the whole product is production-certified**: the live Upstox handshake, Flutter end-to-end integration, deployment TLS/domain, rate limiting/abuse controls, email verification/password reset, and load testing must be verified in the target environment.

## Today's checkpoint (9 Oct 2026)
- Flutter workspace remains `C:\AI Projects\InvestEdge_Packages\InvestEdge_Combined_Workspace`.
- `mobile_app/lib/main.dart` is the active Flutter app; `main_fixed.dart` was uploaded for review.
- Flutter analyzer was previously reported clean and the app was running in Chrome with a WebSocket status indicator.
- Current Flutter file contains simulated/demo fallback behavior; a connected WebSocket is not proof of live market data.
- Uploaded backend ZIP had only `main.py`, `requirements.txt`, `Dockerfile`; defaulted to simulator, used wildcard CORS, had a development JWT fallback, shared one SQLite connection across requests, exposed unauthenticated AI insight and fabricated unknown symbols.
- Upstox access token is not yet available. Per user's standing instruction, do not ask them to check/generate/paste/troubleshoot it; proceed with code and resume live-provider verification once user says access is ready.
- Preserve the current running app and make a backup before replacing files.

## Local setup (Windows PowerShell)
1. Extract this backend folder to a safe staging folder first.
2. From the backend folder run: `py -3.12 -m venv .venv`
3. Run: `.\.venv\Scripts\python.exe -m pip install --upgrade pip`
4. Run: `.\.venv\Scripts\python.exe -m pip install -r requirements.txt`
5. Copy `.env.example` to `.env` and set a private random `JWT_SECRET`. For local demo keep `APP_ENV=development`, `USE_SIMULATOR=true`.
6. Start with: ` .\.venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8000 `
7. Check `http://127.0.0.1:8000/health`. Simulator source must be visibly identified as simulator, never live.

## Production configuration
- `APP_ENV=production`; `USE_SIMULATOR=false`; `JWT_SECRET` at least 32 random characters; `ALLOWED_ORIGINS` must list only the real website origins; configure a persistent `DATABASE_URL` volume and secrets through the hosting provider.
- A valid Upstox token is required for live prices. `/health` reports `market.live=true` only after a connected stream has recently delivered a tick. No token means no live feed.
- Terminate TLS at a trusted reverse proxy/load balancer. Add rate limiting, email verification, account recovery, backups, monitoring/alerts, retention policy and security review before public launch.
- Current data model does not implement mutual funds/bonds/ETFs/crypto/IPO provider feeds. Those must not be advertised as live until real providers and data licenses are integrated.

## Compatibility
- Keeps current endpoint shapes: `/health`, `/api/state`, `/auth/register`, `/auth/login`, `/api/watchlist`, `/api/portfolio`, `/api/signal/{symbol}`, `/api/ai/insight`, `/ws/market`.
- REST endpoints accept `Authorization: Bearer <token>` and retain `?token=` compatibility for existing client integration. Prefer Bearer auth for new clients.
- WebSocket market feed is public market data only. Do not send private account data over it.
