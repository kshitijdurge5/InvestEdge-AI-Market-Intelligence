"""
Upstox OAuth helper for MarketPilot.

Use this for a real multi-user application instead of embedding a single shared
access token. The access token should be stored server-side per connected user.

For local development, a manually generated token can be supplied through:
UPSTOX_ACCESS_TOKEN=...
"""

import os
from urllib.parse import urlencode

import httpx

UPSTOX_AUTHORIZE_URL = "https://api.upstox.com/v2/login/authorization/dialog"
UPSTOX_TOKEN_URL = "https://api.upstox.com/v2/login/authorization/token"


def get_authorization_url(state: str) -> str:
    client_id = os.environ["UPSTOX_CLIENT_ID"]
    redirect_uri = os.environ["UPSTOX_REDIRECT_URI"]

    params = {
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "state": state,
    }
    return f"{UPSTOX_AUTHORIZE_URL}?{urlencode(params)}"


async def exchange_code_for_token(code: str) -> dict:
    data = {
        "code": code,
        "client_id": os.environ["UPSTOX_CLIENT_ID"],
        "client_secret": os.environ["UPSTOX_CLIENT_SECRET"],
        "redirect_uri": os.environ["UPSTOX_REDIRECT_URI"],
        "grant_type": "authorization_code",
    }

    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.post(
            UPSTOX_TOKEN_URL,
            data=data,
            headers={
                "accept": "application/json",
                "Content-Type": "application/x-www-form-urlencoded",
            },
        )

    response.raise_for_status()
    return response.json()


def get_local_access_token() -> str | None:
    return os.getenv("UPSTOX_ACCESS_TOKEN") or None
