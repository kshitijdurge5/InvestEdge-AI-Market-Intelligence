# InvestEdge Unified Architecture

The package is intentionally arranged as one integrated path:

1. **WebSocket** — backend connects to Upstox V3 `MarketDataStreamerV3` when `UPSTOX_ACCESS_TOKEN` exists.
2. **Flutter live state** — Flutter listens to `/ws/market` and updates the existing stock cards/detail pages without replacing the UI.
3. **AI signals** — every live tick receives a deterministic BUY/HOLD/SELL analytical score; optional `/api/ai/insight` uses an OpenAI-compatible provider when `AI_API_KEY` is configured.
4. **Watchlist** — local Flutter persistence plus secure backend endpoints for authenticated users.
5. **Portfolio** — local Flutter persistence plus backend SQLite storage and live valuation from the same market state.
6. **Security** — server-side JWT authentication, PBKDF2 password hashing, no broker/AI secret in Flutter, and Android internet permission only.
7. **Production** — Dockerfile, compose file, environment templates, health endpoint, restart policy and a single backend boundary.
8. **Android** — the same Flutter client remains Android-compatible and a release APK build script is included.

## Important

A real Upstox stream cannot be activated until the broker access token is available. The application therefore runs safely in DEMO mode when no token is configured. It labels the state `DEMO`, not `LIVE`.

No trading order endpoint is enabled by this package. The system is an analytics/research application; it does not execute trades.
