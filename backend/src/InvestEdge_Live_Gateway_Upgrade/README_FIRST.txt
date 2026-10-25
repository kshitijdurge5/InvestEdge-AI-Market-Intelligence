INVESTEDGE - LIVE GATEWAY UPGRADE

This is the next layer after the successful Upstox V3 WebSocket test.
It does NOT replace main.py and does NOT change Flutter yet.

It creates:
Upstox V3 WebSocket -> FastAPI Live Gateway -> local WebSocket /ws/live

Files:
backend/src/live_gateway.py
backend/src/RUN_LIVE_GATEWAY.bat

Copy both files into:
C:\AI Projects\InvestEdge_Packages\InvestEdge_Combined_Workspace\backend\src

Then run RUN_LIVE_GATEWAY.bat in a split backend terminal.

Expected:
Uvicorn running on http://127.0.0.1:8011

After it starts, test in a browser:
http://127.0.0.1:8011/health

The existing backend on port 8010 remains untouched.
Flutter remains untouched until this gateway is verified.
