"""
MarketPilot AI - Main Application

Supports:
1. FastAPI web dashboard
2. Stock research API
3. Existing CLI analysis workflow
"""

import logging
from typing import Any

from fastapi import FastAPI, Query
from .auth import router as auth_router
from .auth_v2 import router as auth_v2_router
from fastapi.responses import HTMLResponse
from fastapi.encoders import jsonable_encoder

from .research import ResearchEngine
from .scoring_chain import MarketPilotScoringChain
from .research_agent import MarketPilotResearchAgent
from .ui import dashboard
from .research_ui import research_page


# ============================================================
# LOGGING
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
)

logger = logging.getLogger(__name__)


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="InvestEdge API",
    version="1.2.0",
    description="AI-powered market and investment intelligence",
)
app.include_router(auth_router)
app.include_router(auth_v2_router)


# ============================================================
# HOME
# ============================================================

@app.get("/")
def home():
    return {
        "name": "InvestEdge API",
        "version": "1.2.0",
        "status": "running",
        "dashboard": "/dashboard",
        "docs": "/docs",
    }


# ============================================================
# DASHBOARD
# ============================================================

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard_page():
    return dashboard()



# ============================================================
# RESEARCH UI
# ============================================================

@app.get("/research-ui", response_class=HTMLResponse)
def research_ui_page():
    return research_page()

# ============================================================
# RESEARCH API
# ============================================================

@app.get("/research")
def research(
    symbol: str = Query(
        ...,
        min_length=1,
        description="Stock symbol such as RELIANCE, TCS or INFY",
    )
):
    symbol = symbol.strip().upper()

    if not symbol:
        return {
            "error": "Please provide a valid stock symbol."
        }

    try:
        logger.info("Research requested for %s", symbol)

        # ----------------------------------------------------
        # 1. MARKET RESEARCH
        # ----------------------------------------------------

        research_engine = ResearchEngine()

        result = research_engine.analyze(symbol)

        if result is None:
            return {
                "error": f"No research data returned for {symbol}"
            }

        # Make a normal dictionary copy
        if isinstance(result, dict):
            data = dict(result)
        else:
            data = {
                "research": result
            }

        # ----------------------------------------------------
        # 2. AI SCORING
        # ----------------------------------------------------

        try:
            scoring_chain = MarketPilotScoringChain()

            scoring_result = scoring_chain.score_result(
                data
            )

            if hasattr(scoring_result, "score"):
                data["ai_score"] = scoring_result.score

            if hasattr(scoring_result, "reasoning"):
                data["ai_reasoning"] = scoring_result.reasoning

        except Exception as exc:
            logger.warning(
                "AI scoring unavailable: %s",
                exc,
            )

        # ----------------------------------------------------
        # 3. COMMON UI FIELDS
        # ----------------------------------------------------

        data["symbol"] = symbol

        # Keep a consistent symbol for the frontend
        if "market_data" not in data:
            data["market_data"] = {}

        if "technical_analysis" not in data:
            data["technical_analysis"] = {}

        if "fundamentals" not in data:
            data["fundamentals"] = {}

        if "risk" not in data:
            data["risk"] = {}

        if "research" not in data:
            data["research"] = {}

        # ----------------------------------------------------
        # 4. JSON-SAFE RESPONSE
        # ----------------------------------------------------

        return jsonable_encoder(data)

    except Exception as exc:

        logger.exception(
            "Research failed for %s",
            symbol,
        )

        return {
            "error": str(exc),
            "symbol": symbol,
        }


# ============================================================
# EXISTING CLI WORKFLOW
# ============================================================

def main():

    print("=" * 70)
    print("                         MARKETPILOT AI")
    print("=" * 70)

    symbol = input(
        "\nEnter stock symbol: "
    ).strip().upper()

    if not symbol:
        print(
            "\nPlease enter a valid stock symbol."
        )
        return

    try:

        # ====================================================
        # 1. MARKET RESEARCH
        # ====================================================

        print(
            f"\n[1/4] Running market research "
            f"for {symbol}...\n"
        )

        research_engine = ResearchEngine()

        research = (
            research_engine.analyze(
                symbol
            )
        )

        print(
            "\nResearch completed successfully."
        )

        print(
            f"Stock: {symbol}"
        )

        print(
            f"Deterministic Score: "
            f"{research.get('score')}"
        )

        # ====================================================
        # 2. AI SCORING
        # ====================================================

        print(
            "\n[2/4] Running AI scoring chain...\n"
        )

        scoring_chain = (
            MarketPilotScoringChain()
        )

        scoring_result = (
            scoring_chain.score_result(
                research
            )
        )

        ai_score = (
            scoring_result.score
        )

        ai_reasoning = (
            scoring_result.reasoning
        )

        print(
            f"AI Score: {ai_score:.2f}/100"
        )

        print(
            "\nAI Scoring Reasoning:"
        )

        print(
            ai_reasoning
        )

        # ====================================================
        # 3. RAG + AI RESEARCH AGENT
        # ====================================================

        print(
            "\n[3/4] Running RAG-powered "
            "AI research agent...\n"
        )

        research_agent = (
            MarketPilotResearchAgent()
        )

        final_analysis = (
            research_agent.analyze(
                research
            )
        )

        # ====================================================
        # 4. FINAL RESULT
        # ====================================================

        print(
            "\n[4/4] Generating final MarketPilot report..."
        )

        print(
            "\n"
            + "=" * 70
        )

        print(
            "                    MARKETPILOT RESULT"
        )

        print(
            "=" * 70
        )

        print(
            f"\nStock: {symbol}"
        )

        print(
            f"Deterministic Score: "
            f"{research.get('score')}"
        )

        print(
            f"AI Score: "
            f"{ai_score:.2f}/100"
        )

        print(
            "\n"
            + "-" * 70
        )

        print(
            "                    AI RESEARCH REPORT"
        )

        print(
            "-" * 70
        )

        print(
            f"\n{final_analysis}"
        )

        print(
            "\n"
            + "-" * 70
        )

        print(
            "                    RESEARCH DATA"
        )

        print(
            "-" * 70
        )

        for key, value in research.items():

            if key in {
                "news",
                "news_sentiment",
            }:
                continue

            print(
                f"\n{key}:"
            )

            print(
                value
            )

        print(
            "\n"
            + "=" * 70
        )

        print(
            "Analysis completed."
        )

        print(
            "=" * 70
        )

    except KeyboardInterrupt:

        print(
            "\n\nAnalysis cancelled by user."
        )

    except Exception as exc:

        logger.exception(
            "MarketPilot failed."
        )

        print(
            "\nMarketPilot encountered an error:"
        )

        print(
            f"{exc}"
        )


# ============================================================
# CLI ENTRY
# ============================================================

if __name__ == "__main__":
    main()



