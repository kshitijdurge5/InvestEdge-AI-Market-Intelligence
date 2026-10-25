import time
from market_stream import MarketStreamManager


def main() -> None:
    print("=" * 72)
    print("INVESTEDGE - UPSTOX V3 LIVE STREAM TEST")
    print("=" * 72)
    print("Token: loaded from backend/.env (hidden)")
    print()

    instruments = {
        "RELIANCE": "NSE_EQ|INE002A01018",
        "TCS": "NSE_EQ|INE467B01029",
        "ICICIBANK": "NSE_EQ|INE090A01021",
    }
    manager = MarketStreamManager(instruments=instruments, mode="ltpc")
    manager.start()
    print("\nWaiting for live ticks...")
    print("You should see [LIVE] lines when market data is delivered.")
    print("Press Ctrl+C to stop.\n")
    try:
        while True:
            time.sleep(5)
            latest = manager.get_latest()
            print("[STATUS] cached live instruments: " + ", ".join(sorted(latest.keys()))
                  if latest else "[STATUS] cached live instruments: waiting...")
    except KeyboardInterrupt:
        print("\nStopping test...")
        manager.stop()


if __name__ == "__main__":
    main()
