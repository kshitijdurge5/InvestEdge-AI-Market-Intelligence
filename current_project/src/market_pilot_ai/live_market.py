"""
MarketPilot AI - Live Market Stream

This module provides a one-second market-price stream.

CURRENT MODE:
    Mock / simulated live data.

The interface is intentionally designed so that a real
market-data WebSocket/provider can replace this later
without changing the dashboard architecture.
"""

import asyncio
import random
from datetime import datetime, timezone


class MockLiveMarketStream:
    """
    Simulates a live stock-price feed.

    This is NOT real market data.

    It exists so the MarketPilot real-time architecture
    can be developed and tested before a real live-data
    provider is connected.
    """

    BASE_PRICES = {
        "RELIANCE": 1450.00,
        "TCS": 3200.00,
        "INFY": 1550.00,
        "HDFCBANK": 1840.00,
        "ITC": 420.00,
        "SBIN": 610.00,
        "BHARTIARTL": 1700.00,
        "LT": 3900.00,
        "TATAMOTORS": 700.00,
        "ASIANPAINT": 2900.00,
    }

    BASE_CHANGES = {
        "RELIANCE": 1.25,
        "TCS": -0.45,
        "INFY": 0.80,
        "HDFCBANK": -1.10,
        "ITC": 0.35,
        "SBIN": -0.75,
        "BHARTIARTL": 0.60,
        "LT": 0.40,
        "TATAMOTORS": -0.30,
        "ASIANPAINT": 0.25,
    }

    def __init__(self, symbol: str):
        self.symbol = symbol.strip().upper()

        self.price = self.BASE_PRICES.get(
            self.symbol,
            1000.00,
        )

        self.start_price = self.price

        self.change_percent = self.BASE_CHANGES.get(
            self.symbol,
            0.00,
        )

        self.tick_number = 0

    async def stream(self):
        """
        Yield one simulated market tick every second.
        """

        while True:

            previous_price = self.price

            # Small random price movement.
            movement = random.uniform(
                -1.25,
                1.25,
            )

            self.price = max(
                1.00,
                self.price + movement,
            )

            self.tick_number += 1

            # Calculate movement from the initial
            # simulated market price.
            self.change_percent = (
                (
                    self.price - self.start_price
                )
                / self.start_price
            ) * 100

            tick_change = (
                self.price - previous_price
            )

            if tick_change > 0:
                direction = "UP"
                signal = "BULLISH"

            elif tick_change < 0:
                direction = "DOWN"
                signal = "BEARISH"

            else:
                direction = "FLAT"
                signal = "NEUTRAL"

            # Simulated volume.
            volume = random.randint(
                500_000,
                2_000_000,
            )

            yield {
                "symbol": self.symbol,
                "price": round(
                    self.price,
                    2,
                ),
                "previous_price": round(
                    previous_price,
                    2,
                ),
                "tick_change": round(
                    tick_change,
                    2,
                ),
                "change_percent": round(
                    self.change_percent,
                    2,
                ),
                "direction": direction,
                "signal": signal,
                "volume": volume,
                "tick_number": self.tick_number,
                "timestamp": datetime.now(
                    timezone.utc
                ).isoformat(),
                "data_source": (
                    "MockLiveMarketStream"
                ),
                "is_live": True,
                "is_simulated": True,
            }

            await asyncio.sleep(1)