"""InvestEdge live gateway: Upstox V3 -> FastAPI WebSocket -> Flutter."""
from __future__ import annotations

import asyncio
import json
from contextlib import asynccontextmanager
from typing import Any, Set

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from market_stream import MarketStreamManager

clients: Set[WebSocket] = set()
manager = MarketStreamManager(
    instruments={
        "RELIANCE": "NSE_EQ|INE002A01018",
        "TCS": "NSE_EQ|INE467B01029",
        "HDFCBANK": "NSE_EQ|INE040A01034",
        "ICICIBANK": "NSE_EQ|INE090A01021",
        "SBIN": "NSE_EQ|INE062A01020",
        "BHARTIARTL": "NSE_EQ|INE397D01024",
        "INFY": "NSE_EQ|INE009A01021",
        "ITC": "NSE_EQ|INE154A01025",
        "LT": "NSE_EQ|INE018A01030",
        "AXISBANK": "NSE_EQ|INE238A01034",
    },
    mode="ltpc",
)

loop: asyncio.AbstractEventLoop | None = None


def clean_tick(tick: dict[str, Any]) -> dict[str, Any]:
    return {
        "type": "market_tick",
        "symbol": tick.get("symbol"),
        "instrument_key": tick.get("instrument_key"),
        "ltp": tick.get("ltp"),
        "ltq": tick.get("ltq"),
        "cp": tick.get("cp"),
        "received_at": tick.get("received_at"),
        "market_data": "LIVE",
        "provider": "Upstox",
        "provider_version": "V3",
    }


def on_tick(tick: dict[str, Any]) -> None:
    """Called from the Upstox SDK thread; schedule broadcasts safely."""
    if loop is None or not clients:
        return
    payload = clean_tick(tick)
    asyncio.run_coroutine_threadsafe(broadcast(payload), loop)


manager.on_tick = on_tick


async def broadcast(payload: dict[str, Any]) -> None:
    if not clients:
        return
    message = json.dumps(payload, separators=(",", ":"))
    dead: list[WebSocket] = []
    for ws in list(clients):
        try:
            await ws.send_text(message)
        except Exception:
            dead.append(ws)
    for ws in dead:
        clients.discard(ws)


@asynccontextmanager
async def lifespan(app: FastAPI):
    global loop
    loop = asyncio.get_running_loop()
    manager.start()
    yield
    manager.stop()


app = FastAPI(title="InvestEdge Live Gateway", version="1.0.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, Any]:
    latest = manager.get_latest()
    return {
        "status": "success",
        "stream": "LIVE",
        "provider": "Upstox",
        "provider_version": "V3",
        "connected_clients": len(clients),
        "instruments_received": sorted(latest.keys()),
    }


@app.get("/live")
def live() -> dict[str, Any]:
    return {
        "status": "success",
        "market_data": "LIVE",
        "provider": "Upstox",
        "provider_version": "V3",
        "quotes": {
            symbol: clean_tick(tick)
            for symbol, tick in manager.get_latest().items()
        },
    }


@app.websocket("/ws/live")
async def websocket_live(websocket: WebSocket) -> None:
    await websocket.accept()
    clients.add(websocket)
    try:
        # Immediately send cached values so Flutter does not wait for the next tick.
        for tick in manager.get_latest().values():
            await websocket.send_text(json.dumps(clean_tick(tick)))
        while True:
            # Client messages are optional; this keeps the connection alive.
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    except Exception:
        pass
    finally:
        clients.discard(websocket)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("live_gateway:app", host="127.0.0.1", port=8011, reload=False)
