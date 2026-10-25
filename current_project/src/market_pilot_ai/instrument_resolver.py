import logging

import requests

from market_pilot_ai.config import (
    UPSTOX_ACCESS_TOKEN,
    REQUEST_TIMEOUT_SECONDS,
)


logger = logging.getLogger(__name__)


class InstrumentResolverError(Exception):
    """Base exception for instrument-resolution errors."""


class InstrumentNotFoundError(InstrumentResolverError):
    """Raised when an instrument cannot be found."""


class InstrumentResolver:
    """
    Resolves a trading symbol into an Upstox instrument key.

    Example:

        RELIANCE
            ↓
        NSE_EQ|INE002A01018
    """

    BASE_URL = (
        "https://api.upstox.com/v2/instruments/search"
    )

    def __init__(
        self,
        access_token: str | None = None,
        timeout: float | None = None,
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
            raise InstrumentResolverError(
                "UPSTOX_ACCESS_TOKEN is not configured."
            )

        logger.info(
            "InstrumentResolver initialized."
        )

    def resolve(
        self,
        symbol: str,
    ) -> str:
        """
        Resolve a trading symbol to an Upstox
        instrument key.
        """

        symbol = symbol.strip().upper()

        if not symbol:
            raise InstrumentNotFoundError(
                "Symbol cannot be empty."
            )

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": (
                f"Bearer {self.access_token}"
            ),
        }

        params = {
            "query": symbol,
            "exchanges": "NSE",
            "segments": "EQ",
            "instrument_types": "EQ",
            "page_number": 1,
            "records": 30,
        }

        logger.info(
            "Resolving instrument for symbol: %s",
            symbol,
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
                "Instrument search request failed "
                "for %s",
                symbol,
            )

            raise InstrumentResolverError(
                f"Instrument search failed "
                f"for '{symbol}'."
            ) from exc

        except ValueError as exc:
            logger.exception(
                "Invalid JSON received while resolving "
                "%s",
                symbol,
            )

            raise InstrumentResolverError(
                "Upstox returned invalid JSON "
                "during instrument search."
            ) from exc

        if payload.get("status") != "success":
            logger.error(
                "Instrument search returned "
                "unsuccessful response: %s",
                payload,
            )

            raise InstrumentResolverError(
                f"Upstox instrument search failed "
                f"for '{symbol}'."
            )

        data = payload.get("data", [])

        if not isinstance(data, list):
            raise InstrumentResolverError(
                "Unexpected instrument-search "
                "response format."
            )

        # Prefer an exact trading-symbol match.
        exact_matches = [
            instrument
            for instrument in data
            if str(
                instrument.get(
                    "trading_symbol",
                    "",
                )
            ).upper()
            == symbol
        ]

        if not exact_matches:
            raise InstrumentNotFoundError(
                f"Instrument '{symbol}' was not found "
                f"on NSE."
            )

        instrument = exact_matches[0]

        instrument_key = instrument.get(
            "instrument_key"
        )

        if not instrument_key:
            raise InstrumentResolverError(
                f"Instrument '{symbol}' was returned "
                f"without an instrument_key."
            )

        logger.info(
            "Resolved %s -> %s",
            symbol,
            instrument_key,
        )

        return str(instrument_key)