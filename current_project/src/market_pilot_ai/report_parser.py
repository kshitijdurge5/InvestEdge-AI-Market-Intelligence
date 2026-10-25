"""
MarketPilot AI - Research Report Parser

Converts raw ResearchEngine output together with
structured LangChain results into the final validated
ResearchReport Pydantic model.
"""

from market_pilot_ai.report_models import (
    FundamentalReport,
    MarketOverview,
    NewsReport,
    ResearchReport,
    RiskReport,
    ScoreComponent,
    ScoreBreakdown,
    ScoreReport,
    SignalReport,
    TechnicalReport,
)


class ResearchReportParser:
    """
    Builds the final validated ResearchReport.

    Bridge:

        ResearchEngine
              ↓
        Deterministic scoring
              ↓
        Signal reconciliation
              ↓
        LangChain structured analysis
              ↓
        AI scoring
              ↓
        ResearchReport
    """

    def parse(
        self,
        research: dict,
        ai_report,
        ai_score_result,
    ) -> ResearchReport:
        """
        Convert raw research + structured AI results
        into a validated ResearchReport.
        """

        symbol = str(
            research.get(
                "symbol",
                "",
            )
        ).upper()

        # =====================================================
        # 1. MARKET OVERVIEW
        # =====================================================

        market_data = research.get(
            "market_data",
            {},
        )

        market_analysis = research.get(
            "market_analysis",
            {},
        )

        market_overview_summary = (
            self._extract_summary(
                market_analysis,
                fallback=self._format_market_data(
                    market_data
                ),
            )
        )

        market_overview = MarketOverview(
            summary=market_overview_summary
        )

        # =====================================================
        # 2. SIGNAL ANALYSIS
        # =====================================================

        signal_reconciliation = research.get(
            "signal_reconciliation",
            {},
        )

        market_signal = (
            signal_reconciliation.get(
                "market_signal",
                market_analysis.get(
                    "trend",
                    "Not available.",
                ),
            )
        )

        technical_signal = (
            signal_reconciliation.get(
                "technical_signal",
                research.get(
                    "technical_analysis",
                    {},
                ).get(
                    "trend",
                    "Not available.",
                ),
            )
        )

        unified_signal = (
            signal_reconciliation.get(
                "unified_signal",
                research.get(
                    "unified_signal",
                    "Not available.",
                ),
            )
        )

        signal_consistency = (
            signal_reconciliation.get(
                "signal_consistency",
                "Not available.",
            )
        )

        signal_report = SignalReport(
            market_signal=str(
                market_signal
            ),
            technical_signal=str(
                technical_signal
            ),
            unified_signal=str(
                unified_signal
            ),
            signal_consistency=str(
                signal_consistency
            ),
        )

        # =====================================================
        # 3. TECHNICAL ANALYSIS
        # =====================================================

        technical_data = research.get(
            "technical_analysis",
            {},
        )

        technical_report = TechnicalReport(
            summary=(
                ai_report.recent_performance
            ),
            trend=self._extract_value(
                technical_data,
                "trend",
                default="Not available.",
            ),
            unified_signal=str(
                unified_signal
            ),
            signal_consistency=str(
                signal_consistency
            ),
            rsi_comment=self._extract_value(
                technical_data,
                "rsi_14",
                default=(
                    "RSI information "
                    "not available."
                ),
            ),
            volatility_comment=self._extract_value(
                technical_data,
                "volatility",
                default=(
                    "Volatility information "
                    "not available."
                ),
            ),
        )

        # =====================================================
        # 4. FUNDAMENTAL ANALYSIS
        # =====================================================

        fundamentals = research.get(
            "fundamentals",
            {},
        )

        fundamental_report = FundamentalReport(
            summary=(
                ai_report.business_quality
            ),
            valuation_comment=(
                self._format_valuation(
                    fundamentals
                )
            ),
            profitability_comment=(
                ai_report.profitability
            ),
        )

        # =====================================================
        # 5. RISK ANALYSIS
        # =====================================================

        risk_data = research.get(
            "risk_analysis",
            {},
        )

        risk_level = self._extract_value(
            risk_data,
            "risk_level",
            default="Not available.",
        )

        risk_report = RiskReport(
            summary=(
                ai_report.major_risks[0]
                if ai_report.major_risks
                else (
                    "No specific risk summary "
                    "available."
                )
            ),
            risk_level=risk_level,
            important_risks=(
                ai_report.major_risks
            ),
        )

        # =====================================================
        # 6. NEWS ANALYSIS
        # =====================================================

        news_sentiment = research.get(
            "news_sentiment",
            {},
        )

        sentiment = self._extract_value(
            news_sentiment,
            "sentiment",
            default="Not available.",
        )

        important_events = (
            self._extract_list(
                research.get("news"),
                keys=[
                    "events",
                    "important_events",
                    "headlines",
                ],
            )
        )

        news_report = NewsReport(
            summary=self._format_news_summary(
                news_sentiment
            ),
            sentiment=sentiment,
            important_events=important_events,
        )

        # =====================================================
        # 7. SCORE BREAKDOWN
        # =====================================================

        score_breakdown_data = research.get(
            "score_breakdown",
            {},
        )

        score_breakdown = (
            self._build_score_breakdown(
                score_breakdown_data
            )
        )

        # =====================================================
        # 8. SCORE COMPARISON
        # =====================================================

        deterministic_score = research.get(
            "score",
            0,
        )

        ai_score = float(
            ai_score_result.score
        )

        score_difference = (
            self._calculate_score_difference(
                deterministic_score,
                ai_score,
            )
        )

        score_agreement = (
            self._calculate_score_agreement(
                score_difference
            )
        )

        score_report = ScoreReport(
            summary=(
                ai_score_result.reasoning
            ),
            deterministic_score=float(
                deterministic_score
            ),
            ai_score=ai_score,
            score_difference=(
                score_difference
            ),
            score_agreement=(
                score_agreement
            ),
            score_breakdown=(
                score_breakdown
            ),
        )

        # =====================================================
        # 9. FINAL TAKEAWAY
        # =====================================================

        research_takeaway = (
            self._build_takeaway(
                ai_report=ai_report,
                deterministic_score=(
                    deterministic_score
                ),
                ai_score=ai_score,
                unified_signal=(
                    unified_signal
                ),
                score_difference=(
                    score_difference
                ),
                score_agreement=(
                    score_agreement
                ),
            )
        )

        # =====================================================
        # 10. FINAL VALIDATED REPORT
        # =====================================================

        return ResearchReport(
            symbol=symbol,
            market_overview=(
                market_overview
            ),
            technical_analysis=(
                technical_report
            ),
            fundamental_analysis=(
                fundamental_report
            ),
            risk_analysis=(
                risk_report
            ),
            news_analysis=(
                news_report
            ),
            signal_analysis=(
                signal_report
            ),
            score_interpretation=(
                score_report
            ),
            research_takeaway=(
                research_takeaway
            ),
        )

    # =========================================================
    # HELPERS
    # =========================================================

    @staticmethod
    def _extract_value(
        data,
        key: str,
        default: str,
    ) -> str:
        """
        Safely extract a value from a dictionary.
        """

        if not isinstance(
            data,
            dict,
        ):
            return default

        value = data.get(
            key
        )

        if value is None:
            return default

        if isinstance(
            value,
            (dict, list),
        ):
            return str(value)

        return str(value)

    @staticmethod
    def _extract_summary(
        data,
        fallback: str,
    ) -> str:
        """
        Extract a useful summary from market analysis.
        """

        if isinstance(
            data,
            dict,
        ):

            for key in (
                "summary",
                "analysis",
                "description",
                "comment",
            ):

                value = data.get(
                    key
                )

                if value:
                    return str(value)

        if data:
            return str(data)

        return fallback

    @staticmethod
    def _extract_list(
        data,
        keys: list[str],
    ) -> list[str]:
        """
        Extract a list of strings from a dictionary.
        """

        if isinstance(
            data,
            list,
        ):

            return [
                str(item)
                for item in data
            ]

        if not isinstance(
            data,
            dict,
        ):
            return []

        for key in keys:

            value = data.get(
                key
            )

            if isinstance(
                value,
                list,
            ):

                return [
                    str(item)
                    for item in value
                ]

            if value:
                return [str(value)]

        return []

    @staticmethod
    def _format_market_data(
        market_data,
    ) -> str:
        """
        Create a readable market-data fallback.
        """

        if not isinstance(
            market_data,
            dict,
        ):
            return str(
                market_data
            )

        parts = []

        for key in (
            "price",
            "change_percent",
            "volume",
        ):

            if key in market_data:

                parts.append(
                    f"{key}: "
                    f"{market_data[key]}"
                )

        if parts:
            return " | ".join(
                parts
            )

        return str(
            market_data
        )

    @staticmethod
    def _format_valuation(
        fundamentals,
    ) -> str:
        """
        Build a valuation summary from available
        fundamental metrics without inventing values.
        """

        if not isinstance(
            fundamentals,
            dict,
        ):
            return (
                "Valuation information "
                "not available."
            )

        parts = []

        if fundamentals.get("pe") is not None:
            parts.append(
                f"P/E: {fundamentals['pe']}"
            )

        if fundamentals.get("pb") is not None:
            parts.append(
                f"P/B: {fundamentals['pb']}"
            )

        if fundamentals.get(
            "ev_ebitda"
        ) is not None:

            parts.append(
                "EV/EBITDA: "
                f"{fundamentals['ev_ebitda']}"
            )

        if not parts:
            return (
                "Valuation information "
                "not available."
            )

        return " | ".join(parts)

    @staticmethod
    def _format_news_summary(
        news_sentiment,
    ) -> str:
        """
        Convert news sentiment data into a readable summary.
        """

        if not news_sentiment:
            return (
                "News sentiment information "
                "not available."
            )

        if isinstance(
            news_sentiment,
            dict,
        ):

            summary = news_sentiment.get(
                "summary"
            )

            if summary:
                return str(
                    summary
                )

            sentiment = news_sentiment.get(
                "sentiment"
            )

            if sentiment:
                return (
                    "Current news sentiment: "
                    f"{sentiment}"
                )

        return str(
            news_sentiment
        )

    @staticmethod
    def _build_score_breakdown(
        data,
    ) -> ScoreBreakdown:
        """
        Convert the deterministic score breakdown
        into validated Pydantic models.
        """

        def component(
            name: str,
        ) -> ScoreComponent:

            item = {}

            if isinstance(
                data,
                dict,
            ):
                item = data.get(
                    name,
                    {},
                )

            if not isinstance(
                item,
                dict,
            ):
                item = {}

            return ScoreComponent(
                score=float(
                    item.get(
                        "score",
                        0,
                    )
                ),
                weight=float(
                    item.get(
                        "weight",
                        0,
                    )
                ),
                contribution=float(
                    item.get(
                        "contribution",
                        0,
                    )
                ),
            )

        return ScoreBreakdown(
            market=component(
                "market"
            ),
            technical=component(
                "technical"
            ),
            fundamental=component(
                "fundamental"
            ),
            risk=component(
                "risk"
            ),
            news=component(
                "news"
            ),
        )

    @staticmethod
    def _calculate_score_difference(
        deterministic_score,
        ai_score,
    ) -> float | None:
        """
        Calculate:

            AI score - deterministic score
        """

        if deterministic_score is None:
            return None

        return round(
            float(ai_score)
            - float(deterministic_score),
            2,
        )

    @staticmethod
    def _calculate_score_agreement(
        difference,
    ) -> str:
        """
        Classify agreement between the two scores.
        """

        if difference is None:
            return "Unavailable"

        absolute_difference = abs(
            float(difference)
        )

        if absolute_difference <= 5:
            return "High"

        if absolute_difference <= 10:
            return "Moderate"

        return "Low"

    @staticmethod
    def _build_takeaway(
        ai_report,
        deterministic_score,
        ai_score,
        unified_signal,
        score_difference,
        score_agreement,
    ) -> str:
        """
        Build the final high-level research takeaway.
        """

        difference_text = (
            "unavailable"
            if score_difference is None
            else f"{score_difference:+.2f}"
        )

        return (
            f"MarketPilot AI's independent AI score is "
            f"{float(ai_score):.2f}/100, while the "
            f"deterministic research score is "
            f"{float(deterministic_score):.2f}. "
            f"The score difference is "
            f"{difference_text}, with "
            f"{score_agreement.lower()} agreement. "
            f"The unified market signal is "
            f"{unified_signal}. "
            f"{ai_report.future_growth_prospects}"
        )