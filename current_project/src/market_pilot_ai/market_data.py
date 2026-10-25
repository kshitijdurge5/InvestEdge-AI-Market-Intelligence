from abc import ABC, abstractmethod
import logging

import requests

from market_pilot_ai.models import MarketData
from market_pilot_ai.config import (
    UPSTOX_ACCESS_TOKEN,
    REQUEST_TIMEOUT_SECONDS,
    MARKET_DATA_PROVIDER,
)
from market_pilot_ai.instrument_resolver import (
    InstrumentResolver,
    InstrumentResolverError,
    InstrumentNotFoundError,
)


logger = logging.getLogger(__name__)


# ============================================================
# Exceptions
# ============================================================


class MarketDataError(Exception):
    """Base exception for market-data errors."""


class SymbolNotFoundError(MarketDataError):
    """Raised when a requested symbol is not available."""


class MarketDataProviderError(MarketDataError):
    """Raised when a market-data provider fails."""


# ============================================================
# Provider interface
# ============================================================


class MarketDataProvider(ABC):
    """Abstract interface for market data providers."""

    @abstractmethod
    def get_market_data(
        self,
        symbol: str,
    ) -> MarketData:
        raise NotImplementedError


# ============================================================
# Mock provider
# ============================================================


class MockMarketDataProvider(MarketDataProvider):
    """Mock provider used for development and testing."""

    def __init__(self) -> None:
        self.market_data = {
            "RELIANCE": {
                "price": 1450.00,
                "change_percent": 1.25,
                "volume": 1250000,
            },
            "TCS": {
                "price": 3200.00,
                "change_percent": -0.45,
                "volume": 850000,
            },
            "INFY": {
                "price": 1550.00,
                "change_percent": 0.80,
                "volume": 1100000,
            },
        }

    def get_market_data(
        self,
        symbol: str,
    ) -> MarketData:
        """Return mock market data for a symbol."""

        symbol = symbol.strip().upper()

        if not symbol:
            raise SymbolNotFoundError(
                "Symbol cannot be empty."
            )

        if symbol not in self.market_data:
            available_symbols = ", ".join(
                sorted(self.market_data.keys())
            )

            raise SymbolNotFoundError(
                f"Symbol '{symbol}' not found. "
                f"Available symbols: "
                f"{available_symbols}"
            )

        data = self.market_data[symbol]

        return MarketData(
            symbol=symbol,
            price=data["price"],
            change_percent=data["change_percent"],
            volume=data["volume"],
        )


# ============================================================
# Upstox provider
# ============================================================


class UpstoxMarketDataProvider(MarketDataProvider):
    """
    Real market-data provider using Upstox.

    Instrument keys are resolved dynamically through
    InstrumentResolver instead of being hardcoded.
    """

    BASE_URL = (
        "https://api.upstox.com/v3/market-quote/quotes"
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
            access_token or UPSTOX_ACCESS_TOKEN
        ).strip()

        self.timeout = (
            timeout
            if timeout is not None
            else REQUEST_TIMEOUT_SECONDS
        )

        if not self.access_token:
            raise MarketDataProviderError(
                "UPSTOX_ACCESS_TOKEN is not configured."
            )

        self.instrument_resolver = (
            instrument_resolver
            or InstrumentResolver(
                access_token=self.access_token,
                timeout=self.timeout,
            )
        )

        logger.info(
            "UpstoxMarketDataProvider initialized."
        )

    def get_market_data(
        self,
        symbol: str,
    ) -> MarketData:
        """Fetch real-time market data from Upstox."""

        symbol = symbol.strip().upper()

        if not symbol:
            raise SymbolNotFoundError(
                "Symbol cannot be empty."
            )

        # ----------------------------------------------------
        # Step 1: Resolve trading symbol
        # ----------------------------------------------------

        try:
            instrument_key = (
                self.instrument_resolver.resolve(
                    symbol
                )
            )

        except InstrumentNotFoundError as exc:
            raise SymbolNotFoundError(
                str(exc)
            ) from exc

        except InstrumentResolverError as exc:
            raise MarketDataProviderError(
                str(exc)
            ) from exc

        # ----------------------------------------------------
        # Step 2: Request market quote
        # ----------------------------------------------------

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": (
                f"Bearer {self.access_token}"
            ),
        }

        params = {
            "instrument_key": instrument_key,
        }

        logger.info(
            "Requesting Upstox market data: "
            "%s -> %s",
            symbol,
            instrument_key,
        )

        try:
            response = requests.get(
                self.BASE_URL,
                headers=headers,
                params=params,
                timeout=self.timeout,
            )

            response.raise_for_status()

            payload = response.json()

        except requests.RequestException as exc:
            logger.exception(
                "Upstox market-data request failed "
                "for %s",
                symbol,
            )

            raise MarketDataProviderError(
                f"Upstox market-data request failed "
                f"for '{symbol}'."
            ) from exc

        except ValueError as exc:
            logger.exception(
                "Invalid JSON received from Upstox "
                "for %s",
                symbol,
            )

            raise MarketDataProviderError(
                "Upstox returned invalid JSON."
            ) from exc

        # ----------------------------------------------------
        # Step 3: Validate response
        # ----------------------------------------------------

        if payload.get("status") != "success":
            logger.error(
                "Unsuccessful Upstox response: %s",
                payload,
            )

            raise MarketDataProviderError(
                f"Upstox API returned an unsuccessful "
                f"response for '{symbol}'."
            )

        data = payload.get("data", {})

        if not isinstance(data, dict):
            raise MarketDataProviderError(
                "Unexpected Upstox market-data "
                "response format."
            )

        # ----------------------------------------------------
        # Step 4: Extract quote
        # ----------------------------------------------------

        quote = data.get(instrument_key)

        if quote is None:
            # Fallback for API response-key differences.
            for item in data.values():
                if not isinstance(item, dict):
                    continue

                if (
                    item.get("symbol", "").upper()
                    == symbol
                ):
                    quote = item
                    break

        if quote is None:
            raise SymbolNotFoundError(
                f"No market quote returned by Upstox "
                f"for '{symbol}'."
            )

        # ----------------------------------------------------
        # Step 5: Extract market values
        # ----------------------------------------------------

        last_price = quote.get("last_price")

        prev_close_price = quote.get(
            "prev_close_price"
        )

        volume = quote.get(
            "volume",
            0,
        )

        if last_price is None:
            raise MarketDataProviderError(
                f"Upstox response did not contain "
                f"a last price for '{symbol}'."
            )

        # ----------------------------------------------------
        # Step 6: Calculate percentage change
        # ----------------------------------------------------

        if (
            prev_close_price is not None
            and prev_close_price != 0
        ):
            change_percent = (
                (
                    last_price
                    - prev_close_price
                )
                / prev_close_price
            ) * 100.0

        else:
            change_percent = 0.0

        logger.info(
            "Received Upstox data for %s: "
            "price=%s, change=%.2f%%, volume=%s",
            symbol,
            last_price,
            change_percent,
            volume,
        )

        # ----------------------------------------------------
        # Step 7: Convert to MarketData model
        # ----------------------------------------------------

        return MarketData(
            symbol=symbol,
            price=float(last_price),
            change_percent=float(
                change_percent
            ),
            volume=int(volume or 0),
        )


# ============================================================
# Market-data client
# ============================================================


class MarketDataClient:
    """
    Main interface used by the rest of MarketPilot AI.

    Provider selection comes from:

        MARKETPILOT_DATA_PROVIDER=mock

    or:

        MARKETPILOT_DATA_PROVIDER=upstox
    """

    def __init__(
        self,
        provider: MarketDataProvider | None = None,
    ) -> None:

        if provider is None:

            if MARKET_DATA_PROVIDER == "mock":
                provider = MockMarketDataProvider()

            elif MARKET_DATA_PROVIDER == "upstox":
                provider = UpstoxMarketDataProvider()

            else:
                raise MarketDataProviderError(
                    "Unsupported market-data provider: "
                    f"'{MARKET_DATA_PROVIDER}'. "
                    "Use 'mock' or 'upstox'."
                )

        self.provider = provider

        logger.info(
            "MarketDataClient initialized with "
            "provider: %s",
            type(provider).__name__,
        )

    def get_market_data(
        self,
        symbol: str,
    ) -> MarketData:
        """Get complete market data for a symbol."""

        logger.info(
            "MarketDataClient requesting data "
            "for %s",
            symbol,
        )

        try:
            return self.provider.get_market_data(
                symbol
            )

        except MarketDataError:
            logger.warning(
                "Market-data error for symbol: %s",
                symbol,
            )
            raise

        except Exception as exc:
            logger.exception(
                "Unexpected market-data provider "
                "error for %s",
                symbol,
            )

            raise MarketDataProviderError(
                "Unexpected market-data provider error "
                f"for '{symbol}'."
            ) from exc

    def get_price(
        self,
        symbol: str,
    ) -> float:
        """Get only the current price for a symbol."""

        market_data = self.get_market_data(
            symbol
        )

        return market_data.price