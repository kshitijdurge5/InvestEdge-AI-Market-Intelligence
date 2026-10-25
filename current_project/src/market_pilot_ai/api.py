"""
MarketPilot AI / InvestEdge API
================================

FastAPI backend for:

    - Health checks
    - Market research
    - Deterministic scoring
    - AI scoring
    - Research Agent
    - InvestEdge dashboard UI
"""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from .research import ResearchEngine
from .scoring_chain import MarketPilotScoringChain
from .ui import dashboard


# ============================================================
# APPLICATION
# ============================================================

app = FastAPI(
    title="InvestEdge API",
    description="AI-powered market intelligence and investment research API.",
    version="1.2.0",
)


# ============================================================
# COMPONENTS
# ============================================================

research_engine = ResearchEngine()
scoring_chain = MarketPilotScoringChain()



# ============================================================
# REQUEST MODELS
# ============================================================

class ResearchRequest(BaseModel):
    """
    Request body for stock research.
    """

    symbol: str = Field(
        ...,
        min_length=1,
        max_length=20,
        description="Stock trading symbol, e.g. RELIANCE, TCS, INFY.",
    )


# ============================================================
# RESPONSE MODELS
# ============================================================

class ResearchResponse(BaseModel):
    """
    Complete response returned by /research.
    """

    symbol: str

    deterministic_score: float | None = None

    score_breakdown: dict[str, Any] = {}

    unified_signal: str | None = None

    signal_reconciliation: dict[str, Any] = {}

    ai_score: float | None = None

    ai_reasoning: str | None = None

    score_difference: float | None = None

    score_agreement: str = "Unavailable"

    research: dict[str, Any] = {}

    ai_report: Any = None


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def compare_scores(
    deterministic_score: float | None,
    ai_score: float | None,
) -> tuple[float | None, str]:
    """
    Compare deterministic and AI scores.

    Difference:
        AI score - deterministic score

    Agreement:
        <= 5   -> High
        <= 10  -> Moderate
        > 10   -> Low
    """

    if deterministic_score is None or ai_score is None:
        return None, "Unavailable"

    difference = round(
        float(ai_score) - float(deterministic_score),
        2,
    )

    absolute_difference = abs(difference)

    if absolute_difference <= 5:
        agreement = "High"

    elif absolute_difference <= 10:
        agreement = "Moderate"

    else:
        agreement = "Low"

    return difference, agreement


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root() -> dict[str, str]:
    """
    API root endpoint.
    """

    return {
        "name": "InvestEdge API",
        "version": "1.2.0",
        "status": "running",
        "dashboard": "/dashboard",
        "docs": "/docs",
    }


# ============================================================
# HEALTH
# ============================================================

@app.get("/health")
def health() -> dict[str, str]:
    """
    Health check endpoint.
    """

    return {
        "status": "healthy",
    }


# ============================================================
# DASHBOARD
# ============================================================

@app.get(
    "/dashboard",
    response_class=HTMLResponse,
)
def dashboard_page():
    """
    Serve the InvestEdge web dashboard.
    """

    return dashboard()


# ============================================================
# RESEARCH
# ============================================================

@app.post(
    "/research",
    response_model=ResearchResponse,
)
def research_stock(
    request: ResearchRequest,
) -> ResearchResponse:
    """
    Run the complete MarketPilot research pipeline.

    Pipeline:

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
        News
             ↓
        Sentiment
             ↓
        Deterministic Score
             ↓
        AI Score
             ↓
        Research Agent
             ↓
        Final Response
    """

    symbol = request.symbol.strip().upper()

    # --------------------------------------------------------
    # 1. Core research
    # --------------------------------------------------------

    research_result = research_engine.analyze(symbol)

    # --------------------------------------------------------
    # 2. Deterministic score
    # --------------------------------------------------------

    deterministic_score = research_result.get(
        "score"
    )

    score_breakdown = research_result.get(
        "score_breakdown",
        {},
    )

    unified_signal = research_result.get(
        "unified_signal"
    )

    signal_reconciliation = research_result.get(
        "signal_reconciliation",
        {},
    )

    # --------------------------------------------------------
    # 3. AI scoring
    # --------------------------------------------------------

    ai_score = None
    ai_reasoning = None

    try:

        ai_result = scoring_chain.score_result(
            research_result
        )

        ai_score = ai_result.score
        ai_reasoning = ai_result.reasoning

    except Exception as exc:

        ai_reasoning = (
            f"AI scoring unavailable: {exc}"
        )

    # --------------------------------------------------------
    # 4. Compare AI and deterministic scores
    # --------------------------------------------------------

    score_difference, score_agreement = compare_scores(
        deterministic_score,
        ai_score,
    )

    # --------------------------------------------------------
    # 5. Research Agent
    # --------------------------------------------------------

    ai_report = None

    try:
        from .research_agent import ResearchAgent
        research_agent = ResearchAgent()
        
        ai_report = research_agent.run(
        symbol=symbol,
        research_data=research_result,
    )
    except Exception as exc:
        
        ai_report = {
        "error": str(exc),
    } 

    # --------------------------------------------------------
    # 6. Final API response
    # --------------------------------------------------------

    return ResearchResponse(
        symbol=symbol,
        deterministic_score=deterministic_score,
        score_breakdown=score_breakdown,
        unified_signal=unified_signal,
        signal_reconciliation=signal_reconciliation,
        ai_score=ai_score,
        ai_reasoning=ai_reasoning,
        score_difference=score_difference,
        score_agreement=score_agreement,
        research=research_result,
        ai_report=ai_report,
    )


# ============================================================
# MODULE EXPORTS
# ============================================================

__all__ = [
    "app",
    "ResearchRequest",
    "ResearchResponse",
    "compare_scores",
]