import logging

from .fundamentals import FundamentalsClient
from .historical_data import HistoricalDataClient
from .market_data import MarketDataClient
from .news import NewsClient
from .news_sentiments import NewsSentimentAnalyzer
from .risk import RiskAnalyzer
from .scoring import ScoringEngine
from .technical_analysis import TechnicalAnalyzer
from .analysis import MarketAnalyzer


logger = logging.getLogger(__name__)


class ResearchEngine:
    """
    Coordinates all MarketPilot market-research components.

    Flow:

    Market Data
        ↓
    Market Analysis
        ↓
    Historical Data
        ↓
    Technical Analysis
        ↓
    Fundamentals
        ↓
    Risk
        ↓
    News + Sentiment
        ↓
    Deterministic Scoring
        ↓
    Unified Market Signal
        ↓
    Score Breakdown

    Important data rule:

    The live market snapshot is authoritative for the
    current price.

    Historical data is used for indicators such as:
        - SMA
        - EMA
        - RSI
        - volatility
        - historical trend

    This prevents the live market price and technical
    current_price from becoming inconsistent.
    """

    def __init__(
        self,
        market_data_client=None,
        historical_data_client=None,
        fundamentals_client=None,
        news_client=None,
        sentiment_analyzer=None,
        scoring_engine=None,
    ):
        self.market_data_client = (
            market_data_client
            or MarketDataClient()
        )

        self.historical_data_client = (
            historical_data_client
            or HistoricalDataClient()
        )

        self.fundamentals_client = (
            fundamentals_client
            or FundamentalsClient()
        )

        self.news_client = (
            news_client
            or NewsClient()
        )

        self.sentiment_analyzer = (
            sentiment_analyzer
            or NewsSentimentAnalyzer()
        )

        self.scoring_engine = (
            scoring_engine
            or ScoringEngine()
        )

        self.technical_analyzer = (
            TechnicalAnalyzer()
        )

        self.risk_analyzer = (
            RiskAnalyzer()
        )

        self.market_analyzer = (
            MarketAnalyzer()
        )

    # =========================================================
    # HELPERS
    # =========================================================

    @staticmethod
    def _model_to_dict(value):
        """
        Convert Pydantic/model-like objects to dictionaries
        while leaving dictionaries untouched.
        """
        if hasattr(value, "model_dump"):
            return value.model_dump()

        if hasattr(value, "dict"):
            return value.dict()

        return value

    @staticmethod
    def _extract_live_price(market_data):
        """
        Extract the authoritative live price from market data.

        Supports the common field names used by the project.
        """
        data = (
            market_data.model_dump()
            if hasattr(market_data, "model_dump")
            else (
                market_data.dict()
                if hasattr(market_data, "dict")
                else market_data
            )
        )

        if not isinstance(data, dict):
            return None

        possible_fields = (
            "price",
            "current_price",
            "last_price",
            "ltp",
            "close",
        )

        for field in possible_fields:
            value = data.get(field)

            if value is None:
                continue

            try:
                price = float(value)

                if price > 0:
                    return price

            except (TypeError, ValueError):
                continue

        return None

    @staticmethod
    def _synchronize_technical_price(
        technical_analysis,
        live_price,
    ):
        """
        Synchronize technical current_price with the live
        market snapshot.

        Historical indicators are NOT recalculated here.

        Only the current-price field is synchronized because
        indicators such as SMA/EMA/RSI should remain based on
        the historical series.
        """

        if live_price is None:
            return technical_analysis

        # -----------------------------------------------------
        # Dictionary result
        # -----------------------------------------------------

        if isinstance(
            technical_analysis,
            dict,
        ):
            technical_analysis = dict(
                technical_analysis
            )

            technical_analysis[
                "current_price"
            ] = live_price

            # Keep an explicit reference to the authoritative
            # source for downstream UI/analysis.
            technical_analysis[
                "current_price_source"
            ] = "live_market_data"

            return technical_analysis

        # -----------------------------------------------------
        # Pydantic model result
        # -----------------------------------------------------

        if hasattr(
            technical_analysis,
            "model_copy",
        ):
            try:
                return technical_analysis.model_copy(
                    update={
                        "current_price": live_price,
                    }
                )
            except Exception:
                pass

        # -----------------------------------------------------
        # Generic object fallback
        # -----------------------------------------------------

        try:
            setattr(
                technical_analysis,
                "current_price",
                live_price,
            )

            return technical_analysis

        except Exception:
            logger.warning(
                "Unable to synchronize technical "
                "current_price with live market price."
            )

            return technical_analysis

    # =========================================================
    # MAIN RESEARCH PIPELINE
    # =========================================================

    def analyze(
        self,
        symbol: str,
    ) -> dict:
        """
        Run the complete MarketPilot research pipeline.

        Returns:

        - market data
        - market analysis
        - historical data
        - technical analysis
        - fundamentals
        - risk
        - news
        - sentiment
        - deterministic score
        - score breakdown
        - unified market signal
        - signal reconciliation
        """

        # -----------------------------------------------------
        # Normalize symbol
        # -----------------------------------------------------

        symbol = symbol.strip().upper()

        if not symbol:
            raise ValueError(
                "Stock symbol cannot be empty."
            )

        logger.info(
            "Starting research for %s",
            symbol,
        )

        # =====================================================
        # 1. CURRENT MARKET DATA
        # =====================================================

        market_data = (
            self.market_data_client.get_market_data(
                symbol
            )
        )

        market_data_dict = (
            self._model_to_dict(
                market_data
            )
        )

        # Extract the authoritative live price.
        live_price = self._extract_live_price(
            market_data
        )

        logger.info(
            "Live market price for %s: %s",
            symbol,
            live_price,
        )

        # =====================================================
        # 2. MARKET ANALYSIS
        # =====================================================

        market_analysis = (
            self.market_analyzer.analyze(
                market_data
            )
        )

        # =====================================================
        # 3. HISTORICAL DATA
        # =====================================================

        historical_data = (
            self.historical_data_client.get_recent_history(
                symbol=symbol,
                days=60,
            )
        )

        if not historical_data:
            raise ValueError(
                f"No historical data available for {symbol}"
            )

        logger.info(
            "Retrieved %s historical candles for %s",
            len(historical_data),
            symbol,
        )

        # =====================================================
        # 4. TECHNICAL ANALYSIS
        # =====================================================

        technical_analysis = (
            self.technical_analyzer.analyze_symbol(
                symbol=symbol,
                days=60,
                historical_data_client=(
                    self.historical_data_client
                ),
            )
        )

        # -----------------------------------------------------
        # CRITICAL FIX
        #
        # TechnicalAnalyzer may use the latest historical
        # candle as current_price.
        #
        # For the live research dashboard, the live market
        # snapshot must be authoritative.
        # -----------------------------------------------------

        technical_analysis = (
            self._synchronize_technical_price(
                technical_analysis,
                live_price,
            )
        )

        technical_analysis_dict = (
            self._model_to_dict(
                technical_analysis
            )
        )

        logger.info(
            "Synchronized technical current_price "
            "for %s to live price %s",
            symbol,
            live_price,
        )

        # =====================================================
        # 5. RISK ANALYSIS
        # =====================================================

        risk_analysis = (
            self.risk_analyzer.analyze(
                technical_analysis
            )
        )

        # =====================================================
        # 6. FUNDAMENTALS
        # =====================================================

        fundamentals = (
            self.fundamentals_client.get_fundamentals(
                symbol
            )
        )

        # =====================================================
        # 7. NEWS
        # =====================================================

        news = (
            self.news_client.get_news(
                symbol
            )
        )

        # =====================================================
        # 8. NEWS SENTIMENT
        # =====================================================

        news_sentiment = (
            self.sentiment_analyzer.analyze(
                news
            )
        )

        # =====================================================
        # 9. DETERMINISTIC SCORING
        # =====================================================

        score_result = (
            self.scoring_engine.calculate_score(
                market_analysis=market_analysis,
                technical_analysis=technical_analysis,
                fundamentals=fundamentals,
                risk_analysis=risk_analysis,
                news_sentiment=news_sentiment,
            )
        )

        # =====================================================
        # 10. EXTRACT SCORE INFORMATION
        # =====================================================

        if isinstance(
            score_result,
            dict,
        ):

            score = score_result.get(
                "overall_score",
                score_result.get(
                    "score",
                    score_result,
                ),
            )

            score_breakdown = score_result.get(
                "score_breakdown",
                {},
            )

            unified_signal = score_result.get(
                "unified_signal"
            )

            signal_reconciliation = (
                score_result.get(
                    "signal_reconciliation",
                    {},
                )
            )

        else:

            # Backward-compatible fallback.
            score = score_result
            score_breakdown = {}
            unified_signal = None
            signal_reconciliation = {}

        # =====================================================
        # 11. FINAL RESEARCH RESULT
        # =====================================================

        research_result = {
            "symbol": symbol,

            # -------------------------------------------------
            # Authoritative live market snapshot.
            # -------------------------------------------------
            "market_data": market_data_dict,

            # -------------------------------------------------
            # Market analysis.
            # -------------------------------------------------
            "market_analysis": market_analysis,

            # -------------------------------------------------
            # Historical OHLCV.
            # -------------------------------------------------
            "historical_data": historical_data,

            # -------------------------------------------------
            # Technical indicators.
            #
            # Use the synchronized dictionary so the API
            # explicitly returns the same current price as
            # market_data.
            # -------------------------------------------------
            "technical_analysis": (
                technical_analysis_dict
            ),

            # -------------------------------------------------
            # Risk.
            # -------------------------------------------------
            "risk_analysis": risk_analysis,

            # -------------------------------------------------
            # Fundamentals.
            # -------------------------------------------------
            "fundamentals": fundamentals,

            # -------------------------------------------------
            # News.
            # -------------------------------------------------
            "news": news,

            # -------------------------------------------------
            # News sentiment.
            # -------------------------------------------------
            "news_sentiment": news_sentiment,

            # -------------------------------------------------
            # Overall deterministic score.
            # -------------------------------------------------
            "score": score,

            # -------------------------------------------------
            # Transparent scoring architecture.
            # -------------------------------------------------
            "score_breakdown": score_breakdown,

            # -------------------------------------------------
            # Unified signal.
            # -------------------------------------------------
            "unified_signal": unified_signal,

            # -------------------------------------------------
            # Signal reconciliation.
            # -------------------------------------------------
            "signal_reconciliation": (
                signal_reconciliation
            ),
        }

        logger.info(
            "Research completed for %s "
            "with score %s and unified signal %s",
            symbol,
            score,
            unified_signal,
        )

        return research_result