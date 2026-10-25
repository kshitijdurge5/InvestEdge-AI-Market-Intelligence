class RiskAnalyzer:
    """
    Analyzes market risk characteristics from technical indicators.
    """

    def analyze(self, technical_data):
        volatility = technical_data["volatility"]
        rsi = technical_data["rsi_14"]
        trend = technical_data["trend"]

        risk_factors = []
        risk_score = 0

        # Volatility risk
        if volatility >= 3:
            risk_factors.append("High volatility")
            risk_score += 3
        elif volatility >= 1.5:
            risk_factors.append("Moderate volatility")
            risk_score += 2
        else:
            risk_factors.append("Low volatility")
            risk_score += 1

        # RSI risk
        if rsi >= 70:
            risk_factors.append("RSI indicates potentially overbought conditions")
            risk_score += 2
        elif rsi <= 30:
            risk_factors.append("RSI indicates potentially oversold conditions")
            risk_score += 2
        else:
            risk_factors.append("RSI is in a neutral range")
            risk_score += 1

        # Trend condition
        if trend == "Negative":
            risk_factors.append("Negative technical trend")
            risk_score += 2
        elif trend == "Mixed":
            risk_factors.append("Mixed technical trend")
            risk_score += 1
        else:
            risk_factors.append("Positive technical trend")

        # Overall risk classification
        if risk_score >= 6:
            risk_level = "High"
        elif risk_score >= 4:
            risk_level = "Moderate"
        else:
            risk_level = "Lower"

        return {
            "risk_level": risk_level,
            "risk_score": risk_score,
            "risk_factors": risk_factors,
        }