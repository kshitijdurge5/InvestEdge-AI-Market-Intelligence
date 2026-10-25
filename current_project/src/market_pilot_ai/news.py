import requests

from market_pilot_ai.config import UPSTOX_ACCESS_TOKEN


class NewsProvider:
    """
    Base class for market-news providers.
    """

    def get_news(self, symbol):
        raise NotImplementedError


class MockNewsProvider(NewsProvider):
    """
    Provides fake news for development and testing.
    """

    def __init__(self):
        self.news = {
            "RELIANCE": [
                {
                    "headline": "Reliance Industries reports strong business activity",
                    "summary": "Synthetic development news for testing MarketPilot.",
                    "published_time": "2026-10-01",
                    "article_link": "https://example.com/reliance",
                },
                {
                    "headline": "Reliance continues expansion across key businesses",
                    "summary": "Synthetic development news for testing MarketPilot.",
                    "published_time": "2026-09-30",
                    "article_link": "https://example.com/reliance-2",
                },
            ],
            "TCS": [
                {
                    "headline": "TCS sees continued technology-services demand",
                    "summary": "Synthetic development news for testing MarketPilot.",
                    "published_time": "2026-10-01",
                    "article_link": "https://example.com/tcs",
                },
            ],
            "INFY": [
                {
                    "headline": "Infosys focuses on continued digital-services growth",
                    "summary": "Synthetic development news for testing MarketPilot.",
                    "published_time": "2026-10-01",
                    "article_link": "https://example.com/infy",
                },
            ],
        }

    def get_news(self, symbol):
        symbol = symbol.upper()

        if symbol not in self.news:
            raise ValueError(
                f"No news available for {symbol}."
            )

        return self.news[symbol]


class UpstoxNewsProvider(NewsProvider):
    """
    Gets real market news from Upstox.
    """

    def __init__(self, access_token):
        self.access_token = access_token

        self.base_url = "https://api.upstox.com/v2/news"

    def get_news(self, symbol):
        symbol = symbol.upper()

        instrument_key = self.get_instrument_key(symbol)

        params = {
            "category": "instrument_keys",
            "instrument_keys": instrument_key,
            "page_number": 1,
            "page_size": 10,
        }

        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.access_token}",
        }

        response = requests.get(
            self.base_url,
            params=params,
            headers=headers,
            timeout=10,
        )

        response.raise_for_status()

        response_data = response.json()

        news_items = response_data["data"].get(
            instrument_key,
            []
        )

        news = []

        for item in news_items:
            news.append(
                {
                    "headline": item["heading"],
                    "summary": item["summary"],
                    "published_time": item["published_time"],
                    "article_link": item["article_link"],
                    "thumbnail": item.get("thumbnail"),
                }
            )

        return news

    def get_instrument_key(self, symbol):
        instrument_keys = {
            "RELIANCE": "NSE_EQ|INE002A01018",
            "TCS": "NSE_EQ|INE467B01029",
            "INFY": "NSE_EQ|INE009A01021",
        }

        if symbol not in instrument_keys:
            raise ValueError(
                f"Instrument key not configured for {symbol}."
            )

        return instrument_keys[symbol]


class NewsClient:
    """
    Main interface used by MarketPilot for market news.
    """

    def __init__(self, provider=None):

        if provider is not None:
            self.provider = provider

        elif UPSTOX_ACCESS_TOKEN:
            self.provider = UpstoxNewsProvider(
                UPSTOX_ACCESS_TOKEN
            )

        else:
            self.provider = MockNewsProvider()

    def get_news(self, symbol):
        return self.provider.get_news(symbol)