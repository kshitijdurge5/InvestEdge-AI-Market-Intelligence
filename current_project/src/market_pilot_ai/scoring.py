class ScoringEngine:
    """
    Calculates a composite research score from:

    - Market
    - Technical
    - Fundamentals
    - Risk
    - News sentiment

    The engine also reconciles market and technical
    signals and exposes a transparent score breakdown.

    This score is for research summarization.
    It is not an investment recommendation.
    """

    # -----------------------------------------
    # Research score weights
    # -----------------------------------------

    MARKET_WEIGHT = 0.25
    TECHNICAL_WEIGHT = 0.25
    FUNDAMENTAL_WEIGHT = 0.25
    RISK_WEIGHT = 0.15
    NEWS_WEIGHT = 0.10

    def calculate_score(
        self,
        market_analysis,
        technical_analysis,
        fundamentals,
        risk_analysis,
        news_sentiment,
    ):
        """
        Calculate the complete deterministic research score.

        Returns both the component scores and the actual
        weighted contribution of each component.
        """

        # -----------------------------------------
        # 1. Calculate component scores
        # -----------------------------------------

        market_score = self.calculate_market_score(
            market_analysis
        )

        technical_score = self.calculate_technical_score(
            technical_analysis
        )

        fundamental_score = self.calculate_fundamental_score(
            fundamentals
        )

        risk_score = self.calculate_risk_score(
            risk_analysis
        )

        news_score = self.calculate_news_score(
            news_sentiment
        )

        # -----------------------------------------
        # 2. Reconcile market + technical signals
        # -----------------------------------------

        signal_reconciliation = self.reconcile_signals(
            market_analysis,
            technical_analysis,
        )

        # Add the reconciliation to market analysis so
        # ResearchEngine automatically exposes it in the
        # final research dictionary.
        market_analysis["signal_reconciliation"] = (
            signal_reconciliation
        )

        market_analysis["unified_signal"] = (
            signal_reconciliation["unified_signal"]
        )

        # -----------------------------------------
        # 3. Calculate weighted contributions
        # -----------------------------------------

        market_contribution = (
            market_score * self.MARKET_WEIGHT
        )

        technical_contribution = (
            technical_score * self.TECHNICAL_WEIGHT
        )

        fundamental_contribution = (
            fundamental_score * self.FUNDAMENTAL_WEIGHT
        )

        risk_contribution = (
            risk_score * self.RISK_WEIGHT
        )

        news_contribution = (
            news_score * self.NEWS_WEIGHT
        )

        # -----------------------------------------
        # 4. Final research score
        # -----------------------------------------

        overall_score = (
            market_contribution
            + technical_contribution
            + fundamental_contribution
            + risk_contribution
            + news_contribution
        )

        # -----------------------------------------
        # 5. Transparent score breakdown
        # -----------------------------------------

        score_breakdown = {
            "market": {
                "score": round(market_score, 2),
                "weight": self.MARKET_WEIGHT,
                "contribution": round(
                    market_contribution,
                    2,
                ),
            },
            "technical": {
                "score": round(technical_score, 2),
                "weight": self.TECHNICAL_WEIGHT,
                "contribution": round(
                    technical_contribution,
                    2,
                ),
            },
            "fundamental": {
                "score": round(fundamental_score, 2),
                "weight": self.FUNDAMENTAL_WEIGHT,
                "contribution": round(
                    fundamental_contribution,
                    2,
                ),
            },
            "risk": {
                "score": round(risk_score, 2),
                "weight": self.RISK_WEIGHT,
                "contribution": round(
                    risk_contribution,
                    2,
                ),
            },
            "news": {
                "score": round(news_score, 2),
                "weight": self.NEWS_WEIGHT,
                "contribution": round(
                    news_contribution,
                    2,
                ),
            },
        }

        return {
            "market_score": round(market_score, 2),
            "technical_score": round(
                technical_score,
                2,
            ),
            "fundamental_score": round(
                fundamental_score,
                2,
            ),
            "risk_score": round(
                risk_score,
                2,
            ),
            "news_score": round(
                news_score,
                2,
            ),
            "overall_score": round(
                overall_score,
                2,
            ),
            "unified_signal": signal_reconciliation[
                "unified_signal"
            ],
            "signal_reconciliation": (
                signal_reconciliation
            ),
            "score_breakdown": score_breakdown,
        }

    # -----------------------------------------
    # Market score
    # -----------------------------------------

    def calculate_market_score(self, analysis):
        """
        Converts market analysis into a 0-100 score.
        """

        momentum_score = analysis["momentum_score"]

        if analysis["trend"] == "Positive":
            trend_score = 80
        elif analysis["trend"] == "Negative":
            trend_score = 30
        else:
            trend_score = 50

        if analysis["volume_status"] == "High":
            volume_score = 80
        elif analysis["volume_status"] == "Moderate":
            volume_score = 60
        else:
            volume_score = 40

        return (
            momentum_score * 0.5
            + trend_score * 0.3
            + volume_score * 0.2
        )

    # -----------------------------------------
    # Technical score
    # -----------------------------------------

    def calculate_technical_score(self, technical):
        """
        Creates a descriptive technical score.
        """

        score = 50

        if technical["trend"] == "Positive":
            score += 20

        elif technical["trend"] == "Negative":
            score -= 20

        rsi = technical["rsi_14"]

        if 40 <= rsi <= 60:
            score += 10

        elif 30 <= rsi < 40 or 60 < rsi <= 70:
            score += 5

        elif rsi >= 70:
            score -= 10

        elif rsi <= 30:
            score -= 10

        volatility = technical["volatility"]

        if volatility < 1.5:
            score += 10

        elif volatility >= 3:
            score -= 10

        return max(
            0,
            min(100, score),
        )

    # -----------------------------------------
    # Fundamental score
    # -----------------------------------------

    def calculate_fundamental_score(self, fundamentals):
        """
        Creates a simple fundamental-data score.

        Missing values are ignored rather than invented.
        """

        scores = []

        pe = fundamentals.get("pe")

        if pe is not None:
            if pe < 15:
                scores.append(80)
            elif pe < 25:
                scores.append(65)
            elif pe < 40:
                scores.append(50)
            else:
                scores.append(35)

        pb = fundamentals.get("pb")

        if pb is not None:
            if pb < 3:
                scores.append(75)
            elif pb < 6:
                scores.append(60)
            else:
                scores.append(45)

        roe = fundamentals.get("roe")

        if roe is not None:
            if roe >= 20:
                scores.append(80)
            elif roe >= 10:
                scores.append(65)
            else:
                scores.append(45)

        roce = fundamentals.get("roce")

        if roce is not None:
            if roce >= 20:
                scores.append(80)
            elif roce >= 10:
                scores.append(65)
            else:
                scores.append(45)

        if not scores:
            return 50

        return sum(scores) / len(scores)

    # -----------------------------------------
    # Risk score
    # -----------------------------------------

    def calculate_risk_score(self, risk_analysis):
        """
        Converts the identified risk level into
        a descriptive research score.
        """

        risk_level = risk_analysis["risk_level"]

        if risk_level == "Lower":
            return 80

        elif risk_level == "Moderate":
            return 55

        elif risk_level == "High":
            return 30

        return 50

    # -----------------------------------------
    # News score
    # -----------------------------------------

    def calculate_news_score(self, news_sentiment):
        """
        Uses the sentiment analyzer's score.
        """

        return news_sentiment["sentiment_score"]

    # -----------------------------------------
    # Signal reconciliation
    # -----------------------------------------

    def reconcile_signals(
        self,
        market_analysis,
        technical_analysis,
    ):
        """
        Reconciles the current market trend with
        the historical technical trend.

        This creates one unified signal that can be
        consumed by the AI research agent.
        """

        market_signal = market_analysis.get(
            "trend",
            "Neutral",
        )

        technical_signal = technical_analysis.get(
            "trend",
            "Neutral",
        )

        # -----------------------------------------
        # Fully aligned
        # -----------------------------------------

        if (
            market_signal == "Positive"
            and technical_signal == "Positive"
        ):
            unified_signal = "Positive"

        elif (
            market_signal == "Negative"
            and technical_signal == "Negative"
        ):
            unified_signal = "Negative"

        # -----------------------------------------
        # Both neutral
        # -----------------------------------------

        elif (
            market_signal == "Neutral"
            and technical_signal == "Neutral"
        ):
            unified_signal = "Neutral"

        # -----------------------------------------
        # Direct contradiction
        # -----------------------------------------

        elif (
            market_signal in {"Positive", "Negative"}
            and technical_signal in {"Positive", "Negative"}
            and market_signal != technical_signal
        ):
            unified_signal = "Mixed"

        # -----------------------------------------
        # One directional + one neutral
        # -----------------------------------------

        elif market_signal == "Neutral":
            unified_signal = technical_signal

        elif technical_signal == "Neutral":
            unified_signal = market_signal

        else:
            unified_signal = "Neutral"

        # -----------------------------------------
        # Consistency classification
        # -----------------------------------------

        if market_signal == technical_signal:
            consistency = "Aligned"

        elif (
            market_signal == "Neutral"
            or technical_signal == "Neutral"
        ):
            consistency = "Partially Aligned"

        else:
            consistency = "Conflicting"

        return {
            "market_signal": market_signal,
            "technical_signal": technical_signal,
            "unified_signal": unified_signal,
            "signal_consistency": consistency,
        }