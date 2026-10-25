InvestEdge All Stages Complete v3

This revision fixes the Research search crash caused by null catalog entries, uses a persistent search controller, safely searches the full NSE equity catalogue, and cleans up Flutter resources on exit.

# InvestEdge — All Stages Complete Upgrade

This is the integrated replacement package for the InvestEdge Flutter project.

## Included path
WebSocket → live state → AI/rule signals → full NSE equity catalog → Watchlist → Portfolio → Security → Production → Android.

## What is now integrated
- Flutter UI preserved and improved.
- Detail-page score cards are compact, readable and visually filled instead of large blank white blocks.
- Backend WebSocket connection with a clear distinction between DEMO and real UPSTOX LIVE.
- Full NSE equity catalog is refreshed from Upstox's official daily NSE instrument JSON. The app can search the complete available NSE equity universe, not just a hard-coded shortlist.
- With a valid Upstox access token, the backend can subscribe to the NSE equity catalog using the V3 LTPC stream (within the documented subscription limits) and route live prices to Flutter.
- Without the token, the app remains safely in DEMO mode.
- Selected/watchlist symbols are subscribed dynamically.
- Watchlist and portfolio persistence remain enabled.
- Broker/AI secrets remain backend-only.
- Android build script and production Docker files remain included.

## Apply
Run `setup_all.ps1` from this package using PowerShell Bypass. It creates a timestamped backup and applies the integrated files to the existing Flutter project.

## Run backend
`powershell -ExecutionPolicy Bypass -File .\scripts\start_backend.ps1`

## Run Flutter
Use Antigravity Run → Dart & Flutter → Chrome.

## Important
A package cannot create a real broker credential. Until Upstox provides a valid access token, the market source is DEMO. Once the token is configured in `backend/.env`, the backend is designed to switch to the Upstox V3 feed. The Flutter app never receives that secret.


## FINAL ALL-IN-ONE BUILD
This package is the consolidated final integration payload. It applies WebSocket live state, AI signals, watchlist, portfolio, security, production assets and Android build support together. The v4 client removes the risky null assertions that caused the Research runtime crash and includes the complete NSE catalog search path. Real Upstox streaming activates only after a valid server-side access token is configured; until then the app is explicitly DEMO.

After applying setup_all.ps1, you can use RUN_FINAL_ALL.ps1 to start the backend and Flutter Chrome together.
