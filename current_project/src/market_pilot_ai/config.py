import os

from dotenv import load_dotenv


load_dotenv()


# ============================================================
# DeepSeek configuration
# ============================================================

DEEPSEEK_API_KEY = os.getenv(
    "DEEPSEEK_API_KEY",
    "",
).strip()

if not DEEPSEEK_API_KEY:
    raise ValueError(
        "DEEPSEEK_API_KEY is missing from the .env file."
    )


DEEPSEEK_BASE_URL = os.getenv(
    "DEEPSEEK_BASE_URL",
    "https://api.deepseek.com",
).strip()


DEEPSEEK_MODEL = os.getenv(
    "DEEPSEEK_MODEL",
    "deepseek-flash",
).strip()


# ============================================================
# Upstox configuration
# ============================================================

UPSTOX_ACCESS_TOKEN = os.getenv(
    "UPSTOX_ACCESS_TOKEN",
    "",
).strip()


# ============================================================
# Application configuration
# ============================================================

APP_NAME = os.getenv(
    "MARKETPILOT_APP_NAME",
    "MarketPilot AI",
).strip()


DEFAULT_SYMBOL = os.getenv(
    "MARKETPILOT_DEFAULT_SYMBOL",
    "RELIANCE",
).strip().upper()


LOG_LEVEL = os.getenv(
    "MARKETPILOT_LOG_LEVEL",
    "INFO",
).strip().upper()


# ============================================================
# Market-data provider configuration
# ============================================================

MARKET_DATA_PROVIDER = os.getenv(
    "MARKETPILOT_DATA_PROVIDER",
    "mock",
).strip().lower()


# ============================================================
# Runtime settings
# ============================================================

REQUEST_TIMEOUT_SECONDS = float(
    os.getenv(
        "MARKETPILOT_REQUEST_TIMEOUT",
        "30",
    )
)


MAX_RETRIES = int(
    os.getenv(
        "MARKETPILOT_MAX_RETRIES",
        "3",
    )
)