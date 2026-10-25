from market_pilot_ai.llm import DeepSeekClient
from market_pilot_ai.report_parser import ResearchReportParser


class MarketResearcher:
    """
    Uses DeepSeek to turn MarketPilot research data
    into a structured research report.
    """

    def __init__(self, ai_client=None, parser=None):
        if ai_client is None:
            ai_client = DeepSeekClient()

        if parser is None:
            parser = ResearchReportParser()

        self.ai = ai_client
        self.parser = parser

    def build_prompt(self, symbol, research):
        """
        Builds the prompt sent to DeepSeek.
        """

        return f"""
You are the research-reporting engine for MarketPilot AI.

Create a structured research report for {symbol}.

IMPORTANT RULES:

1. Use ONLY the supplied research data.
2. Do not invent market data.
3. Do not provide personalized financial advice.
4. Do not tell the user to buy, sell, or hold.
5. Return ONLY valid JSON.
6. Follow the exact JSON structure below.

JSON STRUCTURE:

{{
  "symbol": "string",

  "market_overview": {{
    "summary": "string"
  }},

  "technical_analysis": {{
    "summary": "string",
    "trend": "string",
    "rsi_comment": "string",
    "volatility_comment": "string"
  }},

  "fundamental_analysis": {{
    "summary": "string",
    "valuation_comment": "string",
    "profitability_comment": "string"
  }},

  "risk_analysis": {{
    "summary": "string",
    "risk_level": "string",
    "important_risks": ["string"]
  }},

  "news_analysis": {{
    "summary": "string",
    "sentiment": "string",
    "important_events": ["string"]
  }},

  "score_interpretation": {{
    "summary": "string",
    "overall_score": 0
  }},

  "research_takeaway": "string"
}}

RESEARCH DATA:

{research}
"""

    def generate_report(self, symbol, research):
        """
        Generates and validates a structured AI research report.
        """

        prompt = self.build_prompt(
            symbol,
            research,
        )

        ai_response = self.ai.chat(prompt)

        report = self.parser.parse(
            ai_response
        )

        return report