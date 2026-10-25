"""
MarketPilot AI - Technical Analysis

Calculates technical indicators from historical market data.

The original price-based analysis interface is preserved so existing
MarketPilot code continues to work.

Historical-data integration is provided through:
    TechnicalAnalyzer.analyze_symbol()
"""

from __future__ import annotations

import math
from typing import Any

from .historical_data import HistoricalDataClient


class TechnicalAnalyzer:
    """
    Calculates technical indicators from historical closing prices.

    Existing interface:
        analyze(prices)

    Historical-data interface:
        analyze_symbol(symbol)
    """

    def calculate_sma(
        self,
        prices: list[float],
        period: int,
    ) -> float:
        """Calculate Simple Moving Average."""

        if len(prices) < period:
            raise ValueError(
                f"Need at least {period} prices "
                "to calculate SMA."
            )

        recent_prices = prices[-period:]

        return sum(recent_prices) / period

    def calculate_ema(
        self,
        prices: list[float],
        period: int,
    ) -> float:
        """Calculate Exponential Moving Average."""

        if len(prices) < period:
            raise ValueError(
                f"Need at least {period} prices "
                "to calculate EMA."
            )

        multiplier = 2 / (period + 1)

        ema = sum(prices[:period]) / period

        for price in prices[period:]:
            ema = (
                (price - ema) * multiplier
                + ema
            )

        return ema

    def calculate_rsi(
        self,
        prices: list[float],
        period: int = 14,
    ) -> float:
        """Calculate Relative Strength Index."""

        if len(prices) <= period:
            raise ValueError(
                f"Need more than {period} prices "
                "to calculate RSI."
            )

        gains = []
        losses = []

        for i in range(1, len(prices)):
            change = prices[i] - prices[i - 1]

            if change > 0:
                gains.append(change)
                losses.append(0.0)
            else:
                gains.append(0.0)
                losses.append(abs(change))

        recent_gains = gains[-period:]
        recent_losses = losses[-period:]

        average_gain = (
            sum(recent_gains) / period
        )

        average_loss = (
            sum(recent_losses) / period
        )

        if average_loss == 0:
            return 100.0

        relative_strength = (
            average_gain / average_loss
        )

        return (
            100
            - (
                100
                / (1 + relative_strength)
            )
        )

    def calculate_volatility(
        self,
        prices: list[float],
    ) -> float:
        """Calculate standard deviation of daily percentage returns."""

        if len(prices) < 2:
            raise ValueError(
                "Need at least 2 prices "
                "to calculate volatility."
            )

        returns = []

        for i in range(1, len(prices)):
            previous_price = prices[i - 1]
            current_price = prices[i]

            if previous_price == 0:
                continue

            percentage_change = (
                (
                    current_price
                    - previous_price
                )
                / previous_price
            ) * 100

            returns.append(percentage_change)

        if not returns:
            return 0.0

        average_return = (
            sum(returns) / len(returns)
        )

        squared_differences = []

        for value in returns:
            difference = (
                value - average_return
            )

            squared_differences.append(
                difference ** 2
            )

        variance = (
            sum(squared_differences)
            / len(squared_differences)
        )

        return math.sqrt(variance)

    def analyze(
        self,
        prices: list[float],
    ) -> dict[str, Any]:
        """
        Calculate all technical indicators
        from a list of closing prices.
        """

        if not prices:
            raise ValueError(
                "Price list cannot be empty."
            )

        prices = [
            float(price)
            for price in prices
        ]

        sma_20 = self.calculate_sma(
            prices,
            20,
        )

        ema_20 = self.calculate_ema(
            prices,
            20,
        )

        rsi = self.calculate_rsi(
            prices,
            14,
        )

        volatility = (
            self.calculate_volatility(
                prices
            )
        )

        current_price = prices[-1]

        if (
            current_price > sma_20
            and current_price > ema_20
        ):
            trend = "Positive"

        elif (
            current_price < sma_20
            and current_price < ema_20
        ):
            trend = "Negative"

        else:
            trend = "Mixed"

        return {
            "current_price": round(
                current_price,
                2,
            ),
            "sma_20": round(
                sma_20,
                2,
            ),
            "ema_20": round(
                ema_20,
                2,
            ),
            "rsi_14": round(
                rsi,
                2,
            ),
            "volatility": round(
                volatility,
                2,
            ),
            "trend": trend,
        }

    def analyze_symbol(
        self,
        symbol: str,
        days: int = 30,
        historical_data_client: (
            HistoricalDataClient | None
        ) = None,
    ) -> dict[str, Any]:
        """
        Fetch historical market data and calculate
        technical indicators for a stock symbol.
        """

        symbol = symbol.strip().upper()

        if not symbol:
            raise ValueError(
                "Symbol cannot be empty."
            )

        if days < 20:
            raise ValueError(
                "At least 20 days of historical "
                "data are required."
            )

        client = (
            historical_data_client
            or HistoricalDataClient()
        )

        history = client.get_recent_history(
            symbol=symbol,
            days=days,
        )

        if not history:
            raise ValueError(
                f"No historical data found "
                f"for {symbol}."
            )

        closing_prices = []

        for candle in history:
            close = candle.get("close")

            if close is None:
                continue

            closing_prices.append(
                float(close)
            )

        if len(closing_prices) < 20:
            raise ValueError(
                f"Only {len(closing_prices)} "
                f"closing prices were returned "
                f"for {symbol}. At least 20 "
                "are required."
            )

        analysis = self.analyze(
            closing_prices
        )

        analysis["symbol"] = symbol

        analysis["data_points"] = len(
            closing_prices
        )

        analysis["data_source"] = (
            client.provider.__class__.__name__
        )

        return analysis