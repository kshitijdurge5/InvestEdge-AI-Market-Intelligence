from .models import MarketData


class MarketAnalyzer:
    """
    Analyzes current market data.

    This module focuses on the current market snapshot:
    price change, volume, and momentum.

    Historical/technical signals are reconciled separately
    by the scoring layer.
    """

    def analyze(self, market_data: MarketData):
        change = market_data.change_percent
        volume = market_data.volume

        # -----------------------------
        # Market trend
        # -----------------------------
        if change > 1:
            trend = "Positive"
        elif change < -1:
            trend = "Negative"
        else:
            trend = "Neutral"

        # -----------------------------
        # Volume status
        # -----------------------------
        if volume >= 1_000_000:
            volume_status = "High"
        elif volume >= 500_000:
            volume_status = "Moderate"
        else:
            volume_status = "Low"

        # -----------------------------
        # Momentum score
        # -----------------------------
        if change > 2:
            momentum_score = 90
        elif change > 1:
            momentum_score = 75
        elif change >= 0:
            momentum_score = 60
        elif change > -1:
            momentum_score = 45
        else:
            momentum_score = 30

        return {
            "symbol": market_data.symbol,
            "price": market_data.price,
            "change_percent": change,
            "volume": volume,
            "trend": trend,
            "volume_status": volume_status,
            "momentum_score": momentum_score,
        }

    def reconcile_signals(
        self,
        market_analysis: dict,
        technical_analysis: dict,
    ) -> dict:
        """
        Reconciles the current market signal with the
        historical technical signal.

        This prevents the AI layer from having to arbitrarily
        choose between conflicting signals.

        Possible unified signals:
            Positive
            Negative
            Mixed
            Neutral
        """

        market_trend = market_analysis.get(
            "trend",
            "Neutral",
        )

        technical_trend = technical_analysis.get(
            "trend",
            "Neutral",
        )

        # Both agree positively.
        if (
            market_trend == "Positive"
            and technical_trend == "Positive"
        ):
            unified_signal = "Positive"

        # Both agree negatively.
        elif (
            market_trend == "Negative"
            and technical_trend == "Negative"
        ):
            unified_signal = "Negative"

        # Both are neutral.
        elif (
            market_trend == "Neutral"
            and technical_trend == "Neutral"
        ):
            unified_signal = "Neutral"

        # One positive/negative signal conflicts with
        # the other signal.
        elif (
            market_trend != technical_trend
            and market_trend != "Neutral"
            and technical_trend != "Neutral"
        ):
            unified_signal = "Mixed"

        # If one signal is neutral, use the directional
        # signal but mark the confidence as mixed.
        elif market_trend == "Neutral":
            unified_signal = technical_trend

        elif technical_trend == "Neutral":
            unified_signal = market_trend

        else:
            unified_signal = "Neutral"

        return {
            "market_signal": market_trend,
            "technical_signal": technical_trend,
            "unified_signal": unified_signal,
            "signal_consistency": (
                "Aligned"
                if market_trend == technical_trend
                else "Partially Aligned"
                if "Neutral" in {
                    market_trend,
                    technical_trend,
                }
                else "Conflicting"
            ),
        }