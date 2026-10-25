INVESTEDGE - LIVE UPSTOX V3 STREAMING UPGRADE

Copy the three files from backend/src/ into your existing
InvestEdge_Combined_Workspace/backend/src/.
Do NOT delete main.py or existing files.

Then keep the current backend terminal running and use a second terminal:
cd "C:\AI Projects\InvestEdge_Packages\InvestEdge_Combined_Workspace\backend\src"
.\RUN_LIVE_STREAM_TEST.bat

The token is NOT included. The code reads UPSTOX_ACCESS_TOKEN from backend/.env.

Expected:
  Upstox V3 WebSocket connected
  Subscription active
  [LIVE] RELIANCE ...
  [LIVE] TCS ...
  [LIVE] ICICIBANK ...

After this test succeeds, the next step is FastAPI live state -> Flutter WebSocket.
