import math
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware


# ============================================================
# ENVIRONMENT
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"

load_dotenv(dotenv_path=ENV_FILE, override=True)


def get_access_token() -> str | None:
    token = os.getenv("UPSTOX_ACCESS_TOKEN")

    if token:
        token = token.strip()

    return token or None


def require_access_token() -> str:
    token = get_access_token()

    if not token:
        raise HTTPException(
            status_code=500,
            detail="UPSTOX_ACCESS_TOKEN is not configured.",
        )

    return token


# ============================================================
# FASTAPI
# ============================================================

app = FastAPI(
    title="InvestEdge API",
    version="3.1.0",
    description="InvestEdge AI Market Intelligence Backend",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# UPSTOX ENDPOINTS
# ============================================================

UPSTOX_SEARCH_URL = (
    "https://api.upstox.com/v2/instruments/search"
)

UPSTOX_LTP_URL = (
    "https://api.upstox.com/v3/market-quote/ltp"
)

UPSTOX_INTRADAY_URL = (
    "https://api.upstox.com/v3/historical-candle/intraday"
)


# ============================================================
# SUPPORTED SYMBOLS
# ============================================================

SUPPORTED_SYMBOLS = [
    "RELIANCE",
    "TCS",
    "HDFCBANK",
    "ICICIBANK",
    "SBIN",
    "BHARTIARTL",
    "INFY",
    "ITC",
    "LT",
    "AXISBANK",
]


SYMBOL_ALIASES = {
    "RIL": "RELIANCE",
    "RELIANCEINDUSTRIES": "RELIANCE",
    "RELIANCEINDUSTRIESLTD": "RELIANCE",

    "TATACONSULTANCYSERVICES": "TCS",

    "HDFC": "HDFCBANK",
    "HDFCBANKLTD": "HDFCBANK",

    "ICICI": "ICICIBANK",
    "ICICIBANKLTD": "ICICIBANK",

    "SBI": "SBIN",
    "STATEBANKOFINDIA": "SBIN",

    "AIRTEL": "BHARTIARTL",
    "BHARTI": "BHARTIARTL",
    "BHARTIAIRTEL": "BHARTIARTL",

    "INFOSYS": "INFY",
    "INFOSYSLTD": "INFY",

    "ITCLTD": "ITC",

    "LARSEN": "LT",
    "LARSENTOUBRO": "LT",

    "AXIS": "AXISBANK",
}


def normalize_symbol(symbol: str) -> str:
    value = symbol.upper().strip()

    for character in (" ", "-", "_", "/"):
        value = value.replace(character, "")

    return SYMBOL_ALIASES.get(value, value)


# ============================================================
# UPSTOX HEADERS
# ============================================================

def upstox_headers() -> dict[str, str]:
    token = require_access_token()

    return {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {token}",
    }


# ============================================================
# INSTRUMENT SEARCH
# ============================================================

async def search_nse_equity(
    symbol: str,
) -> dict[str, Any]:

    headers = upstox_headers()

    params = {
        "query": symbol,
        "exchanges": "NSE",
        "segments": "EQ",
        "instrument_types": "EQ",
        "page_number": 1,
        "records": 30,
    }

    try:
        async with httpx.AsyncClient(timeout=20) as client:

            response = await client.get(
                UPSTOX_SEARCH_URL,
                params=params,
                headers=headers,
            )

    except httpx.RequestError as exc:

        raise HTTPException(
            status_code=502,
            detail=f"Unable to reach Upstox instrument search: {exc}",
        )

    if response.status_code != 200:

        raise HTTPException(
            status_code=response.status_code,
            detail=f"Upstox instrument search failed: {response.text}",
        )

    payload = response.json()

    instruments = payload.get("data", [])

    if not instruments:

        raise HTTPException(
            status_code=404,
            detail=f"NSE equity instrument not found for {symbol}",
        )

    # Prefer exact trading symbol.
    for item in instruments:

        trading_symbol = str(
            item.get("trading_symbol", "")
        ).upper()

        if (
            trading_symbol == symbol
            and item.get("segment") == "NSE_EQ"
        ):
            return item

    # Otherwise use first NSE equity result.
    for item in instruments:

        if item.get("segment") == "NSE_EQ":
            return item

    raise HTTPException(
        status_code=404,
        detail=f"NSE equity instrument not found for {symbol}",
    )


# ============================================================
# LIVE LTP
# ============================================================

async def get_upstox_ltp(
    instrument_key: str,
) -> dict[str, Any]:

    headers = upstox_headers()

    params = {
        "instrument_key": instrument_key,
    }

    try:

        async with httpx.AsyncClient(timeout=20) as client:

            response = await client.get(
                UPSTOX_LTP_URL,
                params=params,
                headers=headers,
            )

    except httpx.RequestError as exc:

        raise HTTPException(
            status_code=502,
            detail=f"Unable to reach Upstox LTP API: {exc}",
        )

    if response.status_code != 200:

        raise HTTPException(
            status_code=response.status_code,
            detail=f"Upstox LTP request failed: {response.text}",
        )

    return response.json()


# ============================================================
# EXTRACT LIVE QUOTE
# ============================================================

def extract_live_quote(
    quote_payload: dict[str, Any],
) -> dict[str, Any]:

    data = quote_payload.get("data")

    if not isinstance(data, dict) or not data:

        raise HTTPException(
            status_code=502,
            detail="Upstox returned no live market data.",
        )

    # Upstox V3 normally returns one object keyed by the
    # instrument identifier.
    quote = next(iter(data.values()))

    if not isinstance(quote, dict):

        raise HTTPException(
            status_code=502,
            detail="Upstox returned an invalid quote structure.",
        )

    # Official Upstox V3 field is last_price.
    # ltp is retained only as a compatibility fallback.
    last_price = quote.get("last_price")

    if last_price is None:
        last_price = quote.get("ltp")

    if last_price is None:

        raise HTTPException(
            status_code=502,
            detail=(
                "Upstox returned market data, but no live price "
                f"field was found. Available fields: "
                f"{sorted(quote.keys())}"
            ),
        )

    return quote


# ============================================================
# INTRADAY CANDLES
# ============================================================

async def get_intraday_candles(
    instrument_key: str,
    interval: int = 5,
) -> list[list[Any]]:

    headers = upstox_headers()

    url = (
        f"{UPSTOX_INTRADAY_URL}/"
        f"{instrument_key}/minutes/{interval}"
    )

    try:

        async with httpx.AsyncClient(timeout=20) as client:

            response = await client.get(
                url,
                headers=headers,
            )

    except httpx.RequestError:

        return []

    if response.status_code != 200:

        return []

    try:

        payload = response.json()

    except ValueError:

        return []

    data = payload.get("data", {})

    candles = data.get("candles", [])

    if not isinstance(candles, list):

        return []

    return candles


# ============================================================
# NUMERIC HELPERS
# ============================================================

def safe_float(
    value: Any,
) -> float | None:

    try:

        if value is None:
            return None

        return float(value)

    except (TypeError, ValueError):

        return None


def clamp(
    value: float,
    minimum: float,
    maximum: float,
) -> float:

    return max(
        minimum,
        min(maximum, value),
    )


# ============================================================
# TECHNICAL INDICATORS
# ============================================================

def calculate_sma(
    closes: list[float],
    period: int,
) -> float | None:

    if len(closes) < period:
        return None

    values = closes[-period:]

    return sum(values) / period


def calculate_rsi(
    closes: list[float],
    period: int = 14,
) -> float | None:

    if len(closes) <= period:
        return None

    gains: list[float] = []
    losses: list[float] = []

    for index in range(1, len(closes)):

        difference = (
            closes[index]
            - closes[index - 1]
        )

        if difference >= 0:

            gains.append(difference)
            losses.append(0.0)

        else:

            gains.append(0.0)
            losses.append(abs(difference))

    recent_gains = gains[-period:]
    recent_losses = losses[-period:]

    average_gain = (
        sum(recent_gains)
        / period
    )

    average_loss = (
        sum(recent_losses)
        / period
    )

    if average_loss == 0:

        if average_gain == 0:
            return 50.0

        return 100.0

    relative_strength = (
        average_gain
        / average_loss
    )

    rsi = (
        100
        - (
            100
            / (1 + relative_strength)
        )
    )

    return round(rsi, 2)


def calculate_momentum(
    closes: list[float],
) -> float:

    if len(closes) < 6:
        return 50.0

    current = closes[-1]
    previous = closes[-6]

    if previous == 0:
        return 50.0

    percentage = (
        (current - previous)
        / previous
    ) * 100

    score = 50 + (
        percentage * 8
    )

    return round(
        clamp(score, 0, 100),
        2,
    )


def calculate_volatility(
    closes: list[float],
) -> float:

    if len(closes) < 10:
        return 50.0

    returns: list[float] = []

    for index in range(1, len(closes)):

        previous = closes[index - 1]
        current = closes[index]

        if previous == 0:
            continue

        returns.append(
            (
                (current - previous)
                / previous
            ) * 100
        )

    if not returns:
        return 50.0

    average = (
        sum(returns)
        / len(returns)
    )

    variance = (
        sum(
            (value - average) ** 2
            for value in returns
        )
        / len(returns)
    )

    standard_deviation = math.sqrt(
        variance
    )

    risk = (
        30
        + (
            standard_deviation
            * 18
        )
    )

    return round(
        clamp(risk, 5, 95),
        2,
    )


def calculate_technical_score(
    price: float,
    sma20: float | None,
    rsi: float | None,
) -> float:

    score = 50.0

    if sma20 is not None:

        if price > sma20:
            score += 20
        else:
            score -= 20

    if rsi is not None:

        if 50 <= rsi <= 70:
            score += 15

        elif 40 <= rsi < 50:
            score += 5

        elif 30 <= rsi < 40:
            score -= 5

        elif rsi > 70:
            score -= 5

        elif rsi < 30:
            score += 5

    return round(
        clamp(score, 0, 100),
        2,
    )


# ============================================================
# FUNDAMENTAL PROXY
# ============================================================

def calculate_fundamental_score(
    change_percent: float,
    symbol: str,
) -> float:

    base_scores = {

        "RELIANCE": 72,
        "TCS": 78,
        "HDFCBANK": 76,
        "ICICIBANK": 74,
        "SBIN": 70,
        "BHARTIARTL": 77,
        "INFY": 76,
        "ITC": 73,
        "LT": 75,
        "AXISBANK": 72,
    }

    base = float(
        base_scores.get(
            symbol,
            68,
        )
    )

    if change_percent > 2:

        base += 3

    elif change_percent < -2:

        base -= 3

    return round(
        clamp(base, 0, 100),
        2,
    )


# ============================================================
# SIGNAL ENGINE
# ============================================================

def generate_signal(
    technical: float,
    fundamental: float,
    momentum: float,
    risk: float,
    price: float,
) -> dict[str, Any]:

    risk_adjusted = 100 - risk

    overall = (
        technical * 0.35
        + fundamental * 0.25
        + momentum * 0.25
        + risk_adjusted * 0.15
    )

    overall = round(
        clamp(overall, 0, 100),
        2,
    )

    if overall >= 70:

        recommendation = "BUY"
        trend = "Bullish"

    elif overall >= 55:

        recommendation = "HOLD"
        trend = "Neutral"

    else:

        recommendation = "SELL"
        trend = "Bearish"

    if recommendation == "BUY":

        confidence = clamp(
            55
            + (
                (overall - 70)
                * 1.2
            ),
            55,
            95,
        )

    elif recommendation == "SELL":

        confidence = clamp(
            55
            + (
                (55 - overall)
                * 1.2
            ),
            55,
            95,
        )

    else:

        confidence = clamp(
            50
            + abs(overall - 55),
            50,
            75,
        )

    if recommendation == "BUY":

        entry_low = price * 0.995
        entry_high = price * 1.01

        target1 = price * 1.05
        target2 = price * 1.10

        stop_loss = price * 0.95

    elif recommendation == "SELL":

        entry_low = price * 0.99
        entry_high = price * 1.005

        target1 = price * 0.95
        target2 = price * 0.90

        stop_loss = price * 1.05

    else:

        entry_low = price * 0.99
        entry_high = price * 1.01

        target1 = price * 1.03
        target2 = price * 1.06

        stop_loss = price * 0.96

    return {

        "overall_score": round(
            overall,
            2,
        ),

        "recommendation":
            recommendation,

        "trend":
            trend,

        "confidence":
            round(confidence, 2),

        "entry_zone": {

            "low":
                round(entry_low, 2),

            "high":
                round(entry_high, 2),
        },

        "target":
            round(target1, 2),

        "target_2":
            round(target2, 2),

        "stop_loss":
            round(stop_loss, 2),
    }


# ============================================================
# AI INSIGHT
# ============================================================

def generate_insight(
    recommendation: str,
    trend: str,
    rsi: float | None,
    price: float,
    sma20: float | None,
    momentum: float,
    risk: float,
) -> str:

    parts: list[str] = []

    if recommendation == "BUY":

        parts.append(
            "InvestEdge detects a positive market setup."
        )

    elif recommendation == "SELL":

        parts.append(
            "InvestEdge detects a weaker market setup."
        )

    else:

        parts.append(
            "InvestEdge detects a mixed market setup."
        )

    if trend == "Bullish":

        parts.append(
            "Price and momentum currently favour the bullish side."
        )

    elif trend == "Bearish":

        parts.append(
            "Price and momentum currently favour the bearish side."
        )

    else:

        parts.append(
            "Momentum does not currently show a strong directional advantage."
        )

    if rsi is not None:

        if rsi >= 70:

            parts.append(
                f"RSI is {rsi}, indicating an overbought zone."
            )

        elif rsi <= 30:

            parts.append(
                f"RSI is {rsi}, indicating an oversold zone."
            )

        else:

            parts.append(
                f"RSI is {rsi}, remaining in a normal range."
            )

    if sma20 is not None:

        if price > sma20:

            parts.append(
                "Price is above the intraday moving-average reference."
            )

        else:

            parts.append(
                "Price is below the intraday moving-average reference."
            )

    if risk >= 70:

        parts.append(
            "Risk is elevated, so position sizing should be conservative."
        )

    elif risk >= 50:

        parts.append(
            "Risk is moderate and should be monitored."
        )

    else:

        parts.append(
            "Current calculated market risk is relatively contained."
        )

    parts.append(
        "This is an analytical signal, not a guaranteed return."
    )

    return " ".join(parts)


# ============================================================
# HEALTH
# ============================================================

@app.get("/health")
async def health() -> dict[str, Any]:

    token = get_access_token()

    return {

        "status":
            "online",

        "app":
            "InvestEdge",

        "version":
            "3.1.0",

        "market_data":
            "Upstox V3",

        "upstox_token_configured":
            bool(token),

        "env_file_exists":
            ENV_FILE.exists(),

        "supported_symbols":
            len(SUPPORTED_SYMBOLS),
    }


# ============================================================
# LIVE QUOTE
# ============================================================

@app.get("/api/market/quote/{symbol}")
async def get_live_quote(
    symbol: str,
) -> dict[str, Any]:

    normalized = normalize_symbol(symbol)

    instrument = await search_nse_equity(
        normalized
    )

    instrument_key = instrument.get(
        "instrument_key"
    )

    if not instrument_key:

        raise HTTPException(
            status_code=500,
            detail="Upstox did not return an instrument key.",
        )

    quote_payload = await get_upstox_ltp(
        instrument_key
    )

    quote = extract_live_quote(
        quote_payload
    )

    ltp = safe_float(
        quote.get("last_price")
    )

    if ltp is None:

        ltp = safe_float(
            quote.get("ltp")
        )

    if ltp is None:

        raise HTTPException(
            status_code=502,
            detail="Upstox did not return a valid live price.",
        )

    previous_close = safe_float(
        quote.get("cp")
    )

    if (
        previous_close is not None
        and previous_close != 0
    ):

        change = (
            ltp
            - previous_close
        )

        change_percent = (
            change
            / previous_close
        ) * 100

    else:

        change = 0.0
        change_percent = 0.0

    return {

        "status":
            "success",

        "symbol":
            normalized,

        "company":
            instrument.get(
                "name",
                normalized,
            ),

        "exchange":
            instrument.get(
                "exchange",
                "NSE",
            ),

        "segment":
            instrument.get(
                "segment",
                "NSE_EQ",
            ),

        "instrument_key":
            instrument_key,

        "price":
            round(ltp, 2),

        "previous_close":
            (
                round(previous_close, 2)
                if previous_close is not None
                else None
            ),

        "change":
            round(change, 2),

        "change_percent":
            round(change_percent, 2),

        "volume":
            quote.get("volume"),

        "last_traded_quantity":
            quote.get("ltq"),

        "market_data":
            "LIVE",

        "provider":
            "Upstox",

        "provider_version":
            "V3",
    }


# ============================================================
# FULL MARKET ANALYSIS
# ============================================================

@app.get("/api/market/analyse/{symbol}")
async def analyse_market(
    symbol: str,
) -> dict[str, Any]:

    normalized = normalize_symbol(symbol)

    instrument = await search_nse_equity(
        normalized
    )

    instrument_key = instrument.get(
        "instrument_key"
    )

    if not instrument_key:

        raise HTTPException(
            status_code=500,
            detail="Instrument key unavailable.",
        )

    # --------------------------------------------------------
    # LIVE PRICE
    # --------------------------------------------------------

    quote_payload = await get_upstox_ltp(
        instrument_key
    )

    quote = extract_live_quote(
        quote_payload
    )

    price = safe_float(
        quote.get("last_price")
    )

    if price is None:

        price = safe_float(
            quote.get("ltp")
        )

    if price is None:

        raise HTTPException(
            status_code=502,
            detail="Live price unavailable.",
        )

    previous_close = safe_float(
        quote.get("cp")
    )

    if (
        previous_close is not None
        and previous_close != 0
    ):

        change = (
            price
            - previous_close
        )

        change_percent = (
            change
            / previous_close
        ) * 100

    else:

        change = 0.0
        change_percent = 0.0

    # --------------------------------------------------------
    # INTRADAY CANDLES
    # --------------------------------------------------------

    candles = await get_intraday_candles(
        instrument_key,
        interval=5,
    )

    closes: list[float] = []

    for candle in candles:

        if not isinstance(candle, list):
            continue

        if len(candle) < 5:
            continue

        close_value = safe_float(
            candle[4]
        )

        if close_value is not None:

            closes.append(
                close_value
            )

    # Make sure current live price is included.
    if not closes or closes[-1] != price:

        closes.append(price)

    # --------------------------------------------------------
    # INDICATORS
    # --------------------------------------------------------

    rsi = calculate_rsi(
        closes,
        period=14,
    )

    sma20 = calculate_sma(
        closes,
        period=20,
    )

    sma50 = calculate_sma(
        closes,
        period=50,
    )

    momentum = calculate_momentum(
        closes
    )

    volatility = calculate_volatility(
        closes
    )

    technical = calculate_technical_score(
        price=price,
        sma20=sma20,
        rsi=rsi,
    )

    fundamental = calculate_fundamental_score(
        change_percent=change_percent,
        symbol=normalized,
    )

    # --------------------------------------------------------
    # SIGNAL
    # --------------------------------------------------------

    signal = generate_signal(

        technical=technical,

        fundamental=fundamental,

        momentum=momentum,

        risk=volatility,

        price=price,
    )

    # --------------------------------------------------------
    # INSIGHT
    # --------------------------------------------------------

    insight = generate_insight(

        recommendation=
            signal["recommendation"],

        trend=
            signal["trend"],

        rsi=
            rsi,

        price=
            price,

        sma20=
            sma20,

        momentum=
            momentum,

        risk=
            volatility,
    )

    technical_data_available = (
        len(closes) >= 14
    )

    # --------------------------------------------------------
    # RESPONSE
    # --------------------------------------------------------

    return {

        "status":
            "success",

        "symbol":
            normalized,

        "company":
            instrument.get(
                "name",
                normalized,
            ),

        "exchange":
            instrument.get(
                "exchange",
                "NSE",
            ),

        "segment":
            instrument.get(
                "segment",
                "NSE_EQ",
            ),

        "instrument_key":
            instrument_key,

        "price":
            round(price, 2),

        "previous_close":
            (
                round(previous_close, 2)
                if previous_close is not None
                else None
            ),

        "change":
            round(change, 2),

        "change_percent":
            round(change_percent, 2),

        "volume":
            quote.get("volume"),

        "last_traded_quantity":
            quote.get("ltq"),

        "recommendation":
            signal["recommendation"],

        "trend":
            signal["trend"],

        "confidence":
            signal["confidence"],

        "overall_score":
            signal["overall_score"],

        "technical":
            round(technical, 2),

        "fundamental":
            round(fundamental, 2),

        "momentum":
            round(momentum, 2),

        "risk":
            round(volatility, 2),

        "indicators": {

            "rsi":
                rsi,

            "sma20":
                (
                    round(sma20, 2)
                    if sma20 is not None
                    else None
                ),

            "sma50":
                (
                    round(sma50, 2)
                    if sma50 is not None
                    else None
                ),

            "candles":
                len(closes),

            "timeframe":
                "5-minute",

            "technical_data_available":
                technical_data_available,
        },

        "entry_zone":
            signal["entry_zone"],

        "target":
            signal["target"],

        "target_2":
            signal["target_2"],

        "stop_loss":
            signal["stop_loss"],

        "summary":
            insight,

        "ai_market_insight":
            insight,

        "market_data":
            "LIVE",

        "provider":
            "Upstox",

        "provider_version":
            "V3",

        "last_updated":
            datetime.now(
                timezone.utc
            ).isoformat(),

        "disclaimer":
            (
                "InvestEdge provides analytical "
                "market signals for informational "
                "purposes. Signals are not guaranteed "
                "returns or personalised investment advice."
            ),
    }


# ============================================================
# SUPPORTED SYMBOLS
# ============================================================

@app.get("/api/market/symbols")
async def supported_symbols() -> dict[str, Any]:

    return {

        "count":
            len(SUPPORTED_SYMBOLS),

        "symbols":
            sorted(SUPPORTED_SYMBOLS),
    }


# ============================================================
# ROOT
# ============================================================

@app.get("/")
async def root() -> dict[str, Any]:

    return {

        "app":
            "InvestEdge",

        "status":
            "online",

        "version":
            "3.1.0",

        "market_data":
            "Upstox V3",

        "live_quotes":
            True,

        "technical_analysis":
            True,

        "ai_signal_engine":
            True,

        "supported_symbols":
            len(SUPPORTED_SYMBOLS),
    }