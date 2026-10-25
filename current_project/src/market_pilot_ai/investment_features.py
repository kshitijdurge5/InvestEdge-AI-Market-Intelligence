"""Investment feature helpers for MarketPilot.

UI-safe utilities for SIP calculations and asset-category metadata.
These helpers do not place trades and do not provide personalized financial advice.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AssetCategory:
    key: str
    label: str
    description: str


ASSET_CATEGORIES = (
    AssetCategory("stocks", "Stocks", "Equities with technical, fundamental, risk and news analysis."),
    AssetCategory("mutual_funds", "Mutual Funds", "Equity, debt and hybrid fund research."),
    AssetCategory("sip", "SIP", "Goal-based recurring investment calculations."),
    AssetCategory("bonds", "Bonds", "Government and corporate fixed-income research."),
    AssetCategory("etfs", "ETFs", "Index, gold and sector ETF research."),
    AssetCategory("crypto", "Crypto", "Digital-asset price and momentum monitoring."),
    AssetCategory("ipos", "IPOs", "New-issue research and risk review."),
    AssetCategory("portfolio", "Portfolio", "Allocation and risk workspace."),
)


def sip_projection(monthly_amount: float, annual_return_pct: float, years: int) -> dict[str, float]:
    """Return an illustrative SIP projection using monthly compounding."""
    if monthly_amount <= 0 or annual_return_pct < 0 or years <= 0:
        raise ValueError("monthly_amount > 0, annual_return_pct >= 0 and years > 0 are required")

    months = years * 12
    monthly_rate = annual_return_pct / 100 / 12

    if monthly_rate == 0:
        corpus = monthly_amount * months
    else:
        corpus = monthly_amount * (((1 + monthly_rate) ** months - 1) / monthly_rate) * (1 + monthly_rate)

    invested = monthly_amount * months
    return {
        "monthly_amount": float(monthly_amount),
        "invested": float(invested),
        "estimated_corpus": float(corpus),
        "estimated_gain": float(corpus - invested),
    }


__all__ = ["AssetCategory", "ASSET_CATEGORIES", "sip_projection"]
