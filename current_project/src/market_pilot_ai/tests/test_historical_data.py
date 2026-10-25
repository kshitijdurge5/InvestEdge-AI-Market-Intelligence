from datetime import date, timedelta

from market_pilot_ai.historical_data import (
    HistoricalDataClient,
    MockHistoricalDataProvider,
)

from market_pilot_ai.technical_analysis import (
    TechnicalAnalyzer,
)


def test_mock_historical_data_returns_candles():
    provider = MockHistoricalDataProvider()

    end = date.today()
    start = end - timedelta(days=30)

    candles = provider.get_history(
        symbol="RELIANCE",
        from_date=start.isoformat(),
        to_date=end.isoformat(),
    )

    assert len(candles) == 31

    assert candles[-1]["close"] == 1450.00


def test_historical_client_uses_mock_provider():
    client = HistoricalDataClient()

    assert (
        client.provider.__class__.__name__
        == "MockHistoricalDataProvider"
    )


def test_historical_data_contains_ohlcv_fields():
    provider = MockHistoricalDataProvider()

    end = date.today()
    start = end - timedelta(days=30)

    candles = provider.get_history(
        symbol="RELIANCE",
        from_date=start.isoformat(),
        to_date=end.isoformat(),
    )

    candle = candles[-1]

    assert "timestamp" in candle
    assert "open" in candle
    assert "high" in candle
    assert "low" in candle
    assert "close" in candle
    assert "volume" in candle
    assert "open_interest" in candle


def test_technical_analyzer_uses_historical_data():
    client = HistoricalDataClient()

    analyzer = TechnicalAnalyzer()

    result = analyzer.analyze_symbol(
        symbol="RELIANCE",
        days=30,
        historical_data_client=client,
    )

    assert result["symbol"] == "RELIANCE"

    assert (
        result["data_source"]
        == "MockHistoricalDataProvider"
    )

    assert result["data_points"] == 31

    assert result["current_price"] == 1450.00

    assert "sma_20" in result
    assert "ema_20" in result
    assert "rsi_14" in result
    assert "volatility" in result
    assert "trend" in result