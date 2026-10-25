import requests

from market_pilot_ai.config import UPSTOX_ACCESS_TOKEN


class FundamentalsProvider:
    """
    Base class for company fundamental-data providers.
    """

    def get_fundamentals(self, symbol):
        raise NotImplementedError


class MockFundamentalsProvider(FundamentalsProvider):
    """
    Provides fake fundamental data for development and testing.
    """

    def __init__(self):
        self.fundamentals = {
            "RELIANCE": {
                "company_name": "Reliance Industries Limited",
                "sector": "Refineries",
                "pe": 20.15,
                "pb": 2.13,
                "roa": 4.39,
                "roe": 8.94,
                "roce": 10.39,
                "ev_ebitda": 10.25,
            },
            "TCS": {
                "company_name": "Tata Consultancy Services Limited",
                "sector": "IT Services",
                "pe": 25.10,
                "pb": 12.40,
                "roa": 18.20,
                "roe": 46.30,
                "roce": 52.10,
                "ev_ebitda": 17.80,
            },
            "INFY": {
                "company_name": "Infosys Limited",
                "sector": "IT Services",
                "pe": 24.50,
                "pb": 8.90,
                "roa": 20.10,
                "roe": 31.50,
                "roce": 37.20,
                "ev_ebitda": 16.40,
            },
        }

    def get_fundamentals(self, symbol):
        symbol = symbol.upper()

        if symbol not in self.fundamentals:
            raise ValueError(
                f"No fundamental data available for {symbol}."
            )

        return self.fundamentals[symbol]


class UpstoxFundamentalsProvider(FundamentalsProvider):
    """
    Gets real company fundamental data from Upstox.
    """

    def __init__(self, access_token):
        self.access_token = access_token

        self.base_url = (
            "https://api.upstox.com/v2/fundamentals"
        )

    def get_fundamentals(self, symbol):
        symbol = symbol.upper()

        isin = self.get_isin(symbol)

        profile = self.get_company_profile(isin)
        ratios = self.get_key_ratios(isin)

        return {
            "company_name": profile["company_profile"],
            "sector": profile["sector"],
            **ratios,
        }

    def get_company_profile(self, isin):
        url = f"{self.base_url}/{isin}/profile"

        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.access_token}",
        }

        response = requests.get(
            url,
            headers=headers,
            timeout=10,
        )

        response.raise_for_status()

        return response.json()["data"]

    def get_key_ratios(self, isin):
        url = f"{self.base_url}/{isin}/key-ratios"

        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.access_token}",
        }

        response = requests.get(
            url,
            headers=headers,
            timeout=10,
        )

        response.raise_for_status()

        ratios = response.json()["data"]

        result = {}

        for ratio in ratios:
            name = ratio["name"]
            company_value = ratio["company_value"]

            if name == "P/E":
                result["pe"] = self.clean_number(company_value)

            elif name == "P/B":
                result["pb"] = self.clean_number(company_value)

            elif name == "ROA":
                result["roa"] = self.clean_number(company_value)

            elif name == "ROE":
                result["roe"] = self.clean_number(company_value)

            elif name == "ROCE":
                result["roce"] = self.clean_number(company_value)

            elif name == "EV/EBITDA":
                result["ev_ebitda"] = self.clean_number(
                    company_value
                )

        return result

    def clean_number(self, value):
        value = str(value).replace("%", "")
        return float(value)

    def get_isin(self, symbol):
        instrument_keys = {
            "RELIANCE": "INE002A01018",
            "TCS": "INE467B01029",
            "INFY": "INE009A01021",
        }

        if symbol not in instrument_keys:
            raise ValueError(
                f"ISIN not configured for {symbol}."
            )

        return instrument_keys[symbol]


class FundamentalsClient:
    """
    Main interface used by MarketPilot for fundamental data.
    """

    def __init__(self, provider=None):

        if provider is not None:
            self.provider = provider

        elif UPSTOX_ACCESS_TOKEN:
            self.provider = UpstoxFundamentalsProvider(
                UPSTOX_ACCESS_TOKEN
            )

        else:
            self.provider = MockFundamentalsProvider()

    def get_fundamentals(self, symbol):
        return self.provider.get_fundamentals(symbol)