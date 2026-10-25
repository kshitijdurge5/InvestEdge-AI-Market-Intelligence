from __future__ import annotations

import os
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, Optional

from dotenv import load_dotenv

try:
    import upstox_client
except ImportError as exc:
    raise RuntimeError(
        "Missing Upstox SDK. Install with: python -m pip install --upgrade upstox-python-sdk"
    ) from exc

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"
load_dotenv(dotenv_path=ENV_FILE, override=True)

DEFAULT_INSTRUMENTS: dict[str, str] = {
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
}


class MarketStreamManager:
    """Owns one Upstox V3 market-data WebSocket connection."""

    def __init__(self, instruments: Optional[dict[str, str]] = None,
                 mode: str = "ltpc",
                 on_tick: Optional[Callable[[dict[str, Any]], None]] = None) -> None:
        self.instruments = dict(instruments or DEFAULT_INSTRUMENTS)
        self.mode = mode
        self.on_tick = on_tick
        self.latest: Dict[str, dict[str, Any]] = {}
        self._streamer = None
        self._lock = threading.Lock()
        self._started = False

    @staticmethod
    def _get_access_token() -> str:
        token = (os.getenv("UPSTOX_ACCESS_TOKEN") or "").strip()
        if not token:
            raise RuntimeError(f"UPSTOX_ACCESS_TOKEN was not found in {ENV_FILE}")
        return token

    @staticmethod
    def _number(value: Any) -> Any:
        if value is None:
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return value

    def _normalise_feed(self, message: Any) -> list[dict[str, Any]]:
        if not isinstance(message, dict):
            return []
        feeds = message.get("feeds") or {}
        if not isinstance(feeds, dict):
            return []

        results: list[dict[str, Any]] = []
        for instrument_key, payload in feeds.items():
            if not isinstance(payload, dict):
                continue
            ltpc = payload.get("ltpc") or {}
            if not ltpc:
                full_feed = payload.get("fullFeed") or {}
                if isinstance(full_feed, dict):
                    ltpc = full_feed.get("ltpc") or {}
                    if not ltpc:
                        market_ff = full_feed.get("marketFF") or {}
                        if isinstance(market_ff, dict):
                            ltpc = market_ff.get("ltpc") or {}

            symbol = next((name for name, key in self.instruments.items()
                           if key == instrument_key), instrument_key)
            item = {
                "symbol": symbol,
                "instrument_key": instrument_key,
                "ltp": self._number(ltpc.get("ltp")),
                "ltq": self._number(ltpc.get("ltq")),
                "ltt": ltpc.get("ltt"),
                "cp": self._number(ltpc.get("cp")),
                "received_at": datetime.now(timezone.utc).isoformat(),
                "market_data": "LIVE",
                "provider": "Upstox",
                "provider_version": "V3",
                "raw": payload,
            }
            if item["ltp"] is not None:
                results.append(item)
        return results

    def _handle_open(self) -> None:
        print(f"[InvestEdge] Upstox V3 WebSocket connected. Subscribing to {len(self.instruments)} instruments...")
        self._streamer.subscribe(list(self.instruments.values()), self.mode)
        print(f"[InvestEdge] Subscription active: mode={self.mode}, instruments={', '.join(self.instruments.keys())}")

    def _handle_message(self, message: Any) -> None:
        for tick in self._normalise_feed(message):
            with self._lock:
                self.latest[tick["symbol"]] = tick
            if self.on_tick:
                try:
                    self.on_tick(tick)
                except Exception as callback_error:
                    print(f"[InvestEdge] on_tick callback error: {callback_error}")
            print(f"[LIVE] {tick['symbol']:<12} ₹{tick['ltp']:<10} CP={tick['cp']}")

    def _handle_error(self, error: Any) -> None:
        print(f"[InvestEdge] WebSocket error: {error}")

    def _handle_close(self, *args: Any) -> None:
        print(f"[InvestEdge] Upstox V3 WebSocket closed: {args}")

    def _handle_reconnecting(self, *args: Any) -> None:
        print(f"[InvestEdge] Upstox V3 reconnecting: {args}")

    def start(self) -> None:
        if self._started:
            return
        token = self._get_access_token()
        configuration = upstox_client.Configuration()
        configuration.access_token = token
        self._streamer = upstox_client.MarketDataStreamerV3(
            upstox_client.ApiClient(configuration)
        )
        self._streamer.on("open", self._handle_open)
        self._streamer.on("message", self._handle_message)
        self._streamer.on("error", self._handle_error)
        self._streamer.on("close", self._handle_close)
        self._streamer.on("reconnecting", self._handle_reconnecting)
        try:
            self._streamer.auto_reconnect(True, 5, 20)
        except Exception:
            pass
        self._started = True
        print("[InvestEdge] Starting Upstox V3 live market stream...")
        self._streamer.connect()

    def stop(self) -> None:
        if self._streamer is not None:
            try:
                self._streamer.disconnect()
            except Exception as exc:
                print(f"[InvestEdge] Stream disconnect warning: {exc}")
        self._started = False

    def get_latest(self, symbol: Optional[str] = None) -> Any:
        with self._lock:
            return self.latest.get(symbol.upper()) if symbol else dict(self.latest)

    def subscribe(self, symbols: Iterable[str]) -> None:
        if not self._streamer:
            raise RuntimeError("Market stream is not running.")
        keys = [self.instruments[s.upper()] for s in symbols if s.upper() in self.instruments]
        if keys:
            self._streamer.subscribe(keys, self.mode)


if __name__ == "__main__":
    manager = MarketStreamManager()
    manager.start()
    try:
        threading.Event().wait()
    except KeyboardInterrupt:
        print("\n[InvestEdge] Stopping live market stream...")
        manager.stop()
