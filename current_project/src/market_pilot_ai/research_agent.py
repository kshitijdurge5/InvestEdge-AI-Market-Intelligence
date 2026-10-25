"""
MarketPilot AI - Research Agent

AI research agent that combines:

- Market data
- Historical OHLCV data
- Technical analysis
- Fundamental analysis
- Risk analysis
- News sentiment
- Deterministic scoring
- Unified market signal
- Score component breakdown
- Persistent RAG knowledge
- Metadata-aware company-document retrieval

The agent is evidence-aware and avoids inventing
company-specific facts when information is unavailable.
"""

import json
import logging
from typing import Any

from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

from market_pilot_ai.config import (
    DEEPSEEK_API_KEY,
    DEEPSEEK_BASE_URL,
    DEEPSEEK_MODEL,
    MAX_RETRIES,
    REQUEST_TIMEOUT_SECONDS,
)

from market_pilot_ai.research_tools import (
    get_market_data,
    get_technical_analysis,
    get_fundamental_analysis,
    get_risk_analysis,
    get_news_sentiment,
    get_deterministic_score,
    search_marketpilot_knowledge,
)


logger = logging.getLogger(__name__)


class MarketPilotResearchAgent:
    """
    AI-powered market research agent.

    The agent:

    1. Receives deterministic research data.
    2. Retrieves relevant RAG knowledge.
    3. Understands the unified market signal.
    4. Understands the deterministic score breakdown.
    5. Gives DeepSeek access to research tools.
    6. Allows additional tool calls when necessary.
    7. Produces an evidence-aware final report.
    """

    MAX_TOOL_ITERATIONS = 5

    def __init__(self):

        # =====================================================
        # RESEARCH TOOLS
        # =====================================================

        self.tools = [
            get_market_data,
            get_technical_analysis,
            get_fundamental_analysis,
            get_risk_analysis,
            get_news_sentiment,
            get_deterministic_score,
            search_marketpilot_knowledge,
        ]

        self.tools_by_name = {
            tool.name: tool
            for tool in self.tools
        }

        # =====================================================
        # DEEPSEEK
        # =====================================================

        self.llm = ChatOpenAI(
            api_key=DEEPSEEK_API_KEY,
            base_url=DEEPSEEK_BASE_URL,
            model=DEEPSEEK_MODEL,
            temperature=0,
            timeout=REQUEST_TIMEOUT_SECONDS,
            max_retries=MAX_RETRIES,
        )

        self.llm_with_tools = (
            self.llm.bind_tools(
                self.tools
            )
        )

        logger.info(
            "MarketPilot Research Agent initialized "
            "with %d tools.",
            len(self.tools),
        )

    # =========================================================
    # AUTOMATIC RAG RETRIEVAL
    # =========================================================

    def _automatic_rag_research(
        self,
        research: dict,
    ) -> str:
        """
        Retrieve company-specific knowledge before
        running the main AI research analysis.
        """

        symbol = str(
            research.get(
                "symbol",
                "",
            )
        ).strip().upper()

        if not symbol:

            logger.warning(
                "No stock symbol available for automatic RAG search."
            )

            return (
                "No company-specific RAG research was retrieved "
                "because the stock symbol was unavailable."
            )

        query = (
            f"{symbol} business quality, revenue growth, "
            f"profitability, financial strength, valuation, "
            f"future growth prospects, management, "
            f"competitive position, and major risks."
        )

        try:

            result = (
                search_marketpilot_knowledge.invoke(
                    {
                        "query": query,
                        "company": symbol,
                        "year": 0,
                        "document_type": "",
                        "category": "",
                    }
                )
            )

            if not result:

                logger.info(
                    "No company-specific RAG documents "
                    "found for %s.",
                    symbol,
                )

                return (
                    f"No company-specific documents were found "
                    f"in the RAG knowledge base for {symbol}."
                )

            logger.info(
                "Automatic RAG research completed for %s.",
                symbol,
            )

            return str(result)

        except Exception as exc:

            logger.exception(
                "Automatic RAG research failed for %s.",
                symbol,
            )

            return (
                f"Company-specific RAG retrieval failed for "
                f"{symbol}. The agent must continue using "
                f"the supplied research only. "
                f"Failure: {exc}"
            )

    # =========================================================
    # RESEARCH PAYLOAD
    # =========================================================

    def _build_research_payload(
        self,
        research: dict,
        rag_context: str,
    ) -> dict[str, Any]:
        """
        Build the structured evidence payload supplied
        to the AI agent.

        The deterministic architecture is intentionally
        exposed explicitly so the AI can explain:

        - what the market signal says
        - what the technical signal says
        - whether they agree
        - how the final score was calculated
        """

        market_analysis = research.get(
            "market_analysis",
            {},
        )

        signal_reconciliation = (
            market_analysis.get(
                "signal_reconciliation",
                {},
            )
        )

        unified_signal = market_analysis.get(
            "unified_signal"
        )

        # -----------------------------------------------------
        # Score breakdown
        # -----------------------------------------------------

        score_breakdown = research.get(
            "score_breakdown",
            {},
        )

        # The scoring engine currently returns the breakdown
        # inside the scoring result. Keep this defensive in
        # case the result is later nested differently.
        if not score_breakdown:

            scoring_result = research.get(
                "scoring_result",
                {},
            )

            if isinstance(
                scoring_result,
                dict,
            ):
                score_breakdown = scoring_result.get(
                    "score_breakdown",
                    {},
                )

        # -----------------------------------------------------
        # Explicit deterministic summary
        # -----------------------------------------------------

        deterministic_summary = {
            "overall_score": research.get(
                "score"
            ),
            "unified_signal": unified_signal,
            "signal_reconciliation": (
                signal_reconciliation
            ),
            "score_breakdown": score_breakdown,
        }

        return {
            "primary_research": research,

            # Explicitly expose the unified signal instead
            # of making the LLM derive it itself.
            "unified_market_signal": {
                "unified_signal": unified_signal,
                "market_signal": (
                    signal_reconciliation.get(
                        "market_signal"
                    )
                ),
                "technical_signal": (
                    signal_reconciliation.get(
                        "technical_signal"
                    )
                ),
                "signal_consistency": (
                    signal_reconciliation.get(
                        "signal_consistency"
                    )
                ),
            },

            # Explicitly expose how the score was created.
            "deterministic_score_analysis": (
                deterministic_summary
            ),

            "rag_knowledge": rag_context,

            "evidence_priority": [
                "supplied market research",
                "unified market signal",
                "deterministic score breakdown",
                "historical market data",
                "technical analysis",
                "fundamental analysis",
                "risk analysis",
                "news and sentiment",
                "company-specific RAG evidence",
                "general RAG knowledge",
            ],
        }

    # =========================================================
    # SYSTEM INSTRUCTIONS
    # =========================================================

    @staticmethod
    def _system_instruction() -> str:
        """
        Return the core instructions for the research agent.
        """

        return """
You are MarketPilot AI, an evidence-aware AI market
research analyst.

Your job is to analyze the supplied market research and
produce a professional research report.

===========================================================
AVAILABLE EVIDENCE
===========================================================

You may receive:

1. Current market data
2. Historical OHLCV data
3. Technical indicators
4. Fundamental analysis
5. Risk analysis
6. News and sentiment
7. Deterministic scoring
8. Unified market signal
9. Score component breakdown
10. Company-specific RAG documents
11. General MarketPilot knowledge

===========================================================
EVIDENCE HIERARCHY
===========================================================

Use evidence in this priority order:

1. Supplied research data
2. Unified market signal
3. Deterministic score breakdown
4. Historical market data
5. Calculated technical indicators
6. Fundamental data
7. Risk analysis
8. News and sentiment
9. Company-specific RAG evidence
10. General educational knowledge

Never allow general educational knowledge to override
actual supplied company data.

===========================================================
CRITICAL ANTI-HALLUCINATION RULES
===========================================================

- Never invent financial numbers.
- Never invent revenue.
- Never invent profit.
- Never invent debt.
- Never invent cash flow.
- Never invent valuation metrics.
- Never invent news.
- Never invent management information.
- Never invent company-specific RAG evidence.
- Never invent future prices.
- Never invent price targets.
- Never claim certainty about future performance.
- Never present mock data as live market data.
- If a required fact is unavailable, explicitly say:

  "Not available in the supplied research."

If RAG evidence is general rather than company-specific,
label it as general knowledge.

If company-specific evidence is retrieved, use it only
when it directly supports the statement being made.

===========================================================
UNIFIED MARKET SIGNAL
===========================================================

The system may provide:

- market_signal
- technical_signal
- unified_signal
- signal_consistency

The unified signal is produced by the deterministic
reconciliation layer.

Possible unified signals include:

- Positive
- Negative
- Mixed
- Neutral

Do NOT independently override the unified signal.

If:

Market = Positive
Technical = Negative
Unified = Mixed

then report the signal as MIXED.

Explain the disagreement rather than choosing whichever
signal sounds more favorable.

"Conflicting" signal consistency means the current market
snapshot and historical technical trend disagree.

"Partially Aligned" means one signal is directional while
the other is neutral.

"Aligned" means the two signals agree.

===========================================================
DETERMINISTIC SCORE
===========================================================

The deterministic score is a research signal.

It is NOT:

- a guaranteed return
- a prediction
- a buy/sell guarantee
- financial advice

The score may contain:

- market score
- technical score
- fundamental score
- risk score
- news score
- weight
- contribution
- overall score

When the score breakdown is available:

1. Report the overall score.
2. Explain the strongest positive contributors.
3. Explain the weakest contributors.
4. Explain the weighting when relevant.
5. Do not invent additional scoring factors.
6. Do not alter the deterministic score.

Remember:

score != investment recommendation

===========================================================
SCORING INTERPRETATION
===========================================================

A component's:

score

represents its normalized research assessment.

A component's:

weight

represents how strongly it affects the overall score.

A component's:

contribution

represents the actual weighted contribution to the
overall deterministic score.

Use these values to explain the score mathematically
and transparently.

===========================================================
HISTORICAL DATA RULES
===========================================================

Historical OHLCV data is useful for understanding:

- recent price behavior
- trend
- momentum
- volatility
- technical indicators
- historical context

Do not interpret historical technical indicators as
guaranteed future performance.

If the data source is a mock provider, explicitly
recognize that the values are development/sample data.

===========================================================
TECHNICAL ANALYSIS
===========================================================

Interpret:

- SMA 20
- EMA 20
- RSI 14
- volatility
- trend

Use multiple indicators together.

For RSI:

- around 50 = neutral momentum
- above 70 = potentially overbought
- below 30 = potentially oversold

Do not treat these thresholds as guaranteed trading signals.

If technical trend conflicts with the current market signal,
describe the conflict.

===========================================================
RISK ANALYSIS
===========================================================

Explain the major risks supported by the research.

Distinguish between:

- market risk
- technical risk
- business risk
- financial risk
- news/sentiment risk

Do not invent risks that require unavailable company data.

===========================================================
TOOL USAGE
===========================================================

You have access to research tools.

Use them when:

- supplied information is insufficient
- a specific component needs verification
- additional RAG evidence is useful
- you need a more detailed company-specific context

Do not call tools unnecessarily.

When searching company documents:

- use the stock symbol as the company filter
- prefer company-specific evidence
- do not treat general documents as company-specific

===========================================================
FINAL REPORT FORMAT
===========================================================

Produce the final response using this structure:

1. Executive Summary

2. Market Position
   - current price
   - market movement
   - current market signal
   - unified market signal
   - signal consistency
   - data-source caveat when applicable

3. Technical Analysis
   - SMA 20
   - EMA 20
   - RSI 14
   - volatility
   - technical trend
   - interpretation
   - explain any conflict with market signal

4. Fundamental Analysis
   - business quality
   - revenue/growth
   - profitability
   - financial strength
   - clearly identify unavailable information

5. News & Sentiment

6. Risk Analysis

7. Deterministic Score
   - overall score
   - market score
   - technical score
   - fundamental score
   - risk score
   - news score
   - weights
   - weighted contributions
   - explain the main contributors

8. RAG / Company Evidence
   - company-specific evidence
   - general knowledge
   - explicitly distinguish the two

9. Overall Interpretation
   - combine the unified signal and score
   - explain whether the evidence is aligned or mixed
   - discuss confidence based on evidence quality

10. Evidence Gaps
    - list important information that was unavailable

11. Conclusion

Keep the report concise but useful.

Do not manufacture missing information merely to make
the report appear complete.

The final conclusion must reflect the quality and
limitations of the evidence.

===========================================================
IMPORTANT
===========================================================

The deterministic architecture has already performed
signal reconciliation and scoring.

Your role is to:

- interpret
- explain
- summarize
- identify contradictions
- identify evidence gaps

Your role is NOT to silently change the deterministic
signal or score.
"""

    # =========================================================
    # RESPONSE NORMALIZATION
    # =========================================================

    @staticmethod
    def _normalize_response_content(
        content: Any,
    ) -> str:
        """
        Convert LangChain response content into plain text.
        """

        if isinstance(
            content,
            list,
        ):

            parts = []

            for item in content:

                if isinstance(
                    item,
                    dict,
                ):

                    text_value = item.get(
                        "text"
                    )

                    if text_value:
                        parts.append(
                            str(text_value)
                        )

                else:
                    parts.append(
                        str(item)
                    )

            return "\n".join(
                parts
            ).strip()

        return str(
            content
        ).strip()

    # =========================================================
    # TOOL EXECUTION
    # =========================================================

    def _execute_tool(
        self,
        tool_call: dict,
    ) -> str:
        """
        Execute one LangChain tool call safely.
        """

        tool_name = tool_call.get(
            "name",
            "",
        )

        tool_args = tool_call.get(
            "args",
            {},
        )

        tool = (
            self.tools_by_name.get(
                tool_name
            )
        )

        if tool is None:

            logger.error(
                "Unknown research tool requested: %s",
                tool_name,
            )

            return (
                f"Unknown tool: {tool_name}"
            )

        try:

            logger.info(
                "Calling research tool: %s",
                tool_name,
            )

            result = tool.invoke(
                tool_args
            )

            return str(result)

        except Exception as exc:

            logger.exception(
                "Research tool failed: %s",
                tool_name,
            )

            return (
                f"Tool '{tool_name}' failed: "
                f"{exc}"
            )

    # =========================================================
    # ANALYZE
    # =========================================================

    def analyze(
        self,
        research: dict,
    ) -> str:
        """
        Analyze supplied market research.

        Preserves the existing interface:

            agent.analyze(research)

        Returns:
            str: Final AI-generated research report.
        """

        if not isinstance(
            research,
            dict,
        ):
            raise TypeError(
                "research must be a dictionary."
            )

        logger.info(
            "Starting MarketPilot AI research-agent analysis."
        )

        # =====================================================
        # AUTOMATIC RAG RESEARCH
        # =====================================================

        rag_context = (
            self._automatic_rag_research(
                research
            )
        )

        # =====================================================
        # BUILD EVIDENCE PAYLOAD
        # =====================================================

        research_payload = (
            self._build_research_payload(
                research=research,
                rag_context=rag_context,
            )
        )

        research_json = json.dumps(
            research_payload,
            indent=2,
            default=str,
        )

        # =====================================================
        # INITIAL MESSAGE
        # =====================================================

        prompt = (
            self._system_instruction()
            + "\n\n"
            + "===================================================\n"
            + "MARKETPILOT RESEARCH EVIDENCE\n"
            + "===================================================\n\n"
            + research_json
            + "\n\n"
            + "Analyze this evidence now."
        )

        messages = [
            HumanMessage(
                content=prompt
            )
        ]

        # =====================================================
        # AGENT TOOL LOOP
        # =====================================================

        for iteration in range(
            self.MAX_TOOL_ITERATIONS
        ):

            logger.info(
                "Research-agent iteration %d/%d.",
                iteration + 1,
                self.MAX_TOOL_ITERATIONS,
            )

            response = (
                self.llm_with_tools.invoke(
                    messages
                )
            )

            messages.append(
                response
            )

            tool_calls = getattr(
                response,
                "tool_calls",
                None,
            )

            # =================================================
            # FINAL RESPONSE
            # =================================================

            if not tool_calls:

                final_content = (
                    self._normalize_response_content(
                        response.content
                    )
                )

                if not final_content:

                    raise RuntimeError(
                        "MarketPilot research agent "
                        "returned an empty response."
                    )

                logger.info(
                    "MarketPilot research-agent analysis "
                    "completed successfully."
                )

                return final_content

            # =================================================
            # TOOL CALLS
            # =================================================

            for tool_call in tool_calls:

                tool_call_id = tool_call.get(
                    "id"
                )

                tool_result = (
                    self._execute_tool(
                        tool_call
                    )
                )

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call_id,
                        "content": tool_result,
                    }
                )

        raise RuntimeError(
            "MarketPilot research agent exceeded "
            "the maximum tool-calling iterations."
        )