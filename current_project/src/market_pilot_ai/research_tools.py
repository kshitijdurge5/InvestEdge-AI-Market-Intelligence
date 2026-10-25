"""
MarketPilot AI - Research Tools

Tool definitions used by the AI research workflow.
"""

import json

from langchain_core.tools import tool

from market_pilot_ai.knowledge_base import (
    MarketPilotKnowledgeBase,
)


@tool
def get_market_data(research: str) -> str:
    """
    Return market data from the supplied research.

    Use this tool when you need price, volume,
    percentage change, or market-data information.
    """

    data = _load_research(research)

    return json.dumps(
        data.get("market_data", {}),
        indent=2,
        default=str,
    )


@tool
def get_technical_analysis(research: str) -> str:
    """
    Return technical-analysis information.

    Use this tool when analyzing trend, RSI,
    volatility, momentum, or indicators.
    """

    data = _load_research(research)

    return json.dumps(
        data.get("technical_analysis", {}),
        indent=2,
        default=str,
    )


@tool
def get_fundamental_analysis(research: str) -> str:
    """
    Return fundamental-analysis information.

    Use this tool when analyzing business quality,
    valuation, profitability, financial strength,
    revenue, or growth.
    """

    data = _load_research(research)

    return json.dumps(
        data.get("fundamentals", {}),
        indent=2,
        default=str,
    )


@tool
def get_risk_analysis(research: str) -> str:
    """
    Return risk-analysis information.

    Use this tool when evaluating investment risks,
    volatility, downside factors, or risk level.
    """

    data = _load_research(research)

    return json.dumps(
        data.get("risk_analysis", {}),
        indent=2,
        default=str,
    )


@tool
def get_news_sentiment(research: str) -> str:
    """
    Return news and sentiment information.

    Use this tool when analyzing recent events,
    headlines, sentiment, or news-related risks.
    """

    data = _load_research(research)

    result = {
        "news": data.get("news", []),
        "news_sentiment": data.get(
            "news_sentiment",
            {},
        ),
    }

    return json.dumps(
        result,
        indent=2,
        default=str,
    )


@tool
def get_deterministic_score(research: str) -> str:
    """
    Return the deterministic MarketPilot research score.
    """

    data = _load_research(research)

    return json.dumps(
        {
            "score": data.get("score")
        },
        indent=2,
        default=str,
    )


@tool
def search_marketpilot_knowledge(
    query: str,
    company: str = "",
    year: int = 0,
    document_type: str = "",
    category: str = "",
) -> str:
    """
    Search MarketPilot's internal knowledge base.

    Use this tool when additional research knowledge is
    needed about fundamentals, technical analysis, risk,
    news, or MarketPilot research methodology.

    Optional filters:

    company:
        Example: RELIANCE

    year:
        Example: 2025

    document_type:
        Examples:
        annual_report
        investor_presentation
        financial_results
        research_report

    category:
        Examples:
        fundamentals
        technical
        risk
        news
        methodology
    """

    knowledge_base = (
        MarketPilotKnowledgeBase()
    )

    metadata_filter = {}

    if company:
        metadata_filter["company"] = (
            company.strip().upper()
        )

    if year:
        metadata_filter["year"] = int(year)

    if document_type:
        metadata_filter["document_type"] = (
            document_type.strip().lower()
        )

    if category:
        metadata_filter["category"] = (
            category.strip().lower()
        )

    context = (
        knowledge_base.build_context(
            query=query,
            top_k=3,
            metadata_filter=(
                metadata_filter
                if metadata_filter
                else None
            ),
        )
    )

    return context


def _load_research(
    research: str,
) -> dict:
    """
    Convert serialized research data into a dictionary.
    """

    if isinstance(research, dict):
        return research

    try:
        return json.loads(research)

    except (
        TypeError,
        json.JSONDecodeError,
    ):
        return {}