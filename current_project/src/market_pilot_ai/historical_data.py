"""
MarketPilot AI - Historical Market Data

Provides historical OHLCV data through a provider architecture.

Providers:
    mock   -> deterministic local development data
    upstox -> Upstox Historical Candle V3 API
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from datetime import date, timedelta
from typing import Any

import requests

from .config import (
    MARKET_DATA_PROVIDER,
    REQUEST_TIMEOUT_SECONDS,
    UPSTOX_ACCESS_TOKEN,
)
from .instrument_resolver import InstrumentResolver


logger = logging.getLogger(__name__)


# ============================================================
# EXCEPTIONS
# ============================================================


class HistoricalDataError(Exception):
    """Base historical-data exception."""


class HistoricalDataProviderError(
    HistoricalDataError
):
    """Historical-data provider failure."""


class HistoricalDataNotFoundError(
    HistoricalDataError
):
    """Historical data was not found."""


# ============================================================
# PROVIDER INTERFACE
# ============================================================


class HistoricalDataProvider(ABC):
    """Abstract historical-data provider."""

    @abstractmethod
    def get_history(
        self,
        symbol: str,
        from_date: str,
        to_date: str,
        unit: str = "days",
        interval: int = 1,
    ) -> list[dict[str, Any]]:
        """Return normalized historical candles."""
        raise NotImplementedError


# ============================================================
# MOCK PROVIDER
# ============================================================


class MockHistoricalDataProvider(
    HistoricalDataProvider
):
    """
    Deterministic historical data for development.

    Latest close is aligned with the corresponding
    mock market-data price.
    """

    BASE_PRICES = {
        "RELIANCE": 1450.00,
        "TCS": 3200.00,
        "INFY": 1550.00,
    }

    def get_history(
        self,
        symbol: str,
        from_date: str,
        to_date: str,
        unit: str = "days",
        interval: int = 1,
    ) -> list[dict[str, Any]]:

        symbol = symbol.strip().upper()

        if not symbol:
            raise HistoricalDataNotFoundError(
                "Symbol cannot be empty."
            )

        try:
            start = date.fromisoformat(from_date)
            end = date.fromisoformat(to_date)
        except ValueError as exc:
            raise HistoricalDataError(
                "Dates must use YYYY-MM-DD format."
            ) from exc

        if start > end:
            raise HistoricalDataError(
                "from_date cannot be later than to_date."
            )

        if unit != "days":
            raise HistoricalDataError(
                "Mock provider currently supports "
                "unit='days' only."
            )

        if interval != 1:
            raise HistoricalDataError(
                "Mock daily data requires interval=1."
            )

        base_price = self.BASE_PRICES.get(
            symbol,
            1000.00,
        )

        candles = []

        current = start
        index = 0

        while current <= end:

            movement = (
                ((index % 7) - 3) * 2.5
            )

            open_price = (
                base_price + movement
            )

            high_price = (
                open_price + 12.0
            )

            low_price = (
                open_price - 8.0
            )

            close_price = (
                open_price + 2.5
            )

            # Keep latest historical close equal
            # to the mock market-data price.
            if current == end:
                close_price = base_price

            volume = (
                900_000
                + (index * 25_000)
            )

            candles.append(
                {
                    "timestamp": (
                        f"{current.isoformat()}"
                        "T15:30:00+05:30"
                    ),
                    "open": round(
                        open_price,
                        2,
                    ),
                    "high": round(
                        high_price,
                        2,
                    ),
                    "low": round(
                        low_price,
                        2,
                    ),
                    "close": round(
                        close_price,
                        2,
                    ),
                    "volume": int(volume),
                    "open_interest": 0,
                }
            )

            current += timedelta(days=1)
            index += 1

        logger.info(
            "Generated %s mock historical candles for %s",
            len(candles),
            symbol,
        )

        return candles


# ============================================================
# UPSTOX PROVIDER
# ============================================================


class UpstoxHistoricalDataProvider(
    HistoricalDataProvider
):
    """Upstox Historical Candle V3 provider."""

    BASE_URL = (
        "https://api.upstox.com/v3/"
        "historical-candle"
    )

    def __init__(
        self,
        access_token: str | None = None,
        timeout: float | None = None,
        instrument_resolver: (
            InstrumentResolver | None
        ) = None,
    ) -> None:

        self.access_token = (
            access_token
            or UPSTOX_ACCESS_TOKEN
        ).strip()

        self.timeout = (
            timeout
            if timeout is not None
            else REQUEST_TIMEOUT_SECONDS
        )

        if not self.access_token:
            raise HistoricalDataProviderError(
                "UPSTOX_ACCESS_TOKEN is not configured."
            )

        self.instrument_resolver = (
            instrument_resolver
            or InstrumentResolver(
                access_token=self.access_token,
                timeout=self.timeout,
            )
        )

    def get_history(
        self,
        symbol: str,
        from_date: str,
        to_date: str,
        unit: str = "days",
        interval: int = 1,
    ) -> list[dict[str, Any]]:

        symbol = symbol.strip().upper()

        if not symbol:
            raise HistoricalDataError(
                "Symbol cannot be empty."
            )

        self._validate_dates(
            from_date,
            to_date,
        )

        self._validate_interval(
            unit,
            interval,
        )

        instrument_key = (
            self.instrument_resolver.resolve(
                symbol
            )
        )

        url = (
            f"{self.BASE_URL}/"
            f"{instrument_key}/"
            f"{unit}/"
            f"{interval}/"
            f"{to_date}/"
            f"{from_date}"
        )

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": (
                f"Bearer {self.access_token}"
            ),
        }

        try:

            response = requests.get(
                url,
                headers=headers,
                timeout=self.timeout,
            )

            response.raise_for_status()

            payload = response.json()

        except requests.RequestException as exc:

            raise HistoricalDataProviderError(
                f"Historical data request failed "
                f"for '{symbol}'."
            ) from exc

        except ValueError as exc:

            raise HistoricalDataProviderError(
                "Upstox returned invalid JSON."
            ) from exc

        if payload.get("status") != "success":
            raise HistoricalDataProviderError(
                f"Upstox historical-data request "
                f"failed for '{symbol}'."
            )

        data = payload.get(
            "data",
            {},
        )

        candles = data.get(
            "candles",
            [],
        )

        if not isinstance(
            candles,
            list,
        ):
            raise HistoricalDataProviderError(
                "Unexpected Upstox candle format."
            )

        normalized = (
            self._normalize_candles(
                candles
            )
        )

        if not normalized:
            raise HistoricalDataNotFoundError(
                f"No historical data found "
                f"for '{symbol}'."
            )

        return normalized

    @staticmethod
    def _validate_dates(
        from_date: str,
        to_date: str,
    ) -> None:

        try:
            start = date.fromisoformat(
                from_date
            )

            end = date.fromisoformat(
                to_date
            )

        except ValueError as exc:

            raise HistoricalDataError(
                "Dates must use YYYY-MM-DD format."
            ) from exc

        if start > end:
            raise HistoricalDataError(
                "from_date cannot be later than "
                "to_date."
            )

    @staticmethod
    def _validate_interval(
        unit: str,
        interval: int,
    ) -> None:

        allowed_units = {
            "minutes",
            "hours",
            "days",
            "weeks",
            "months",
        }

        if unit not in allowed_units:
            raise HistoricalDataError(
                "Invalid historical-data unit."
            )

        if interval < 1:
            raise HistoricalDataError(
                "Interval must be >= 1."
            )

        if unit == "minutes" and interval > 300:
            raise HistoricalDataError(
                "Minute interval must be between "
                "1 and 300."
            )

        if unit == "hours" and interval > 5:
            raise HistoricalDataError(
                "Hour interval must be between "
                "1 and 5."
            )

        if unit in {
            "days",
            "weeks",
            "months",
        } and interval != 1:
            raise HistoricalDataError(
                "Days, weeks, and months support "
                "interval 1."
            )

    @staticmethod
    def _normalize_candles(
        candles: list[Any],
    ) -> list[dict[str, Any]]:

        normalized = []

        for candle in candles:

            if not isinstance(
                candle,
                list,
            ):
                continue

            if len(candle) < 6:
                continue

            try:

                normalized.append(
                    {
                        "timestamp": str(
                            candle[0]
                        ),
                        "open": float(
                            candle[1]
                        ),
                        "high": float(
                            candle[2]
                        ),
                        "low": float(
                            candle[3]
                        ),
                        "close": float(
                            candle[4]
                        ),
                        "volume": int(
                            candle[5]
                        ),
                        "open_interest": (
                            int(candle[6])
                            if len(candle) > 6
                            else 0
                        ),
                    }
                )

            except (
                TypeError,
                ValueError,
            ):

                logger.warning(
                    "Skipping malformed candle: %s",
                    candle,
                )

        return normalized


# ============================================================
# APPLICATION CLIENT
# ============================================================


class HistoricalDataClient:
    """
    Application-facing historical-data client.

    Provider is selected using:

        MARKETPILOT_DATA_PROVIDER=mock

    or:

        MARKETPILOT_DATA_PROVIDER=upstox
    """

    def __init__(
        self,
        provider: (
            HistoricalDataProvider | None
        ) = None,
    ) -> None:

        if provider is not None:

            self.provider = provider

        elif MARKET_DATA_PROVIDER == "mock":

            self.provider = (
                MockHistoricalDataProvider()
            )

        elif MARKET_DATA_PROVIDER == "upstox":

            self.provider = (
                UpstoxHistoricalDataProvider()
            )

        else:

            raise HistoricalDataProviderError(
                "Unsupported historical-data "
                f"provider: {MARKET_DATA_PROVIDER}"
            )

        logger.info(
            "HistoricalDataClient initialized "
            "with %s",
            self.provider.__class__.__name__,
        )

    def get_history(
        self,
        symbol: str,
        from_date: str,
        to_date: str,
        unit: str = "days",
        interval: int = 1,
    ) -> list[dict[str, Any]]:

        return self.provider.get_history(
            symbol=symbol,
            from_date=from_date,
            to_date=to_date,
            unit=unit,
            interval=interval,
        )

    def get_recent_history(
        self,
        symbol: str,
        days: int = 30,
    ) -> list[dict[str, Any]]:

        if days < 1:
            raise HistoricalDataError(
                "days must be >= 1."
            )

        end = date.today()

        start = (
            end
            - timedelta(days=days)
        )

        return self.get_history(
            symbol=symbol,
            from_date=start.isoformat(),
            to_date=end.isoformat(),
            unit="days",
            interval=1,
        )