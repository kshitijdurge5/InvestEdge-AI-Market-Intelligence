"""
MarketPilot AI - Independent Scoring Chain

Uses DeepSeek through LangChain and validates the AI-generated
score with Pydantic.

The AI score is intentionally kept independent from the
deterministic scoring engine.

This module also contains a safe recovery mechanism for cases
where the LLM returns malformed JSON.
"""

from __future__ import annotations

import json
import logging
import re
from typing import Any

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from .config import (
    DEEPSEEK_API_KEY,
    DEEPSEEK_BASE_URL,
    DEEPSEEK_MODEL,
)


logger = logging.getLogger(__name__)


# ============================================================
# PYDANTIC OUTPUT MODEL
# ============================================================


class ScoringResult(BaseModel):
    """
    Structured independent AI scoring result.
    """

    score: float = Field(
        ge=0,
        le=100,
        description="Independent AI research score from 0 to 100.",
    )

    reasoning: str = Field(
        min_length=1,
        description=(
            "Concise explanation of why the AI assigned "
            "this score."
        ),
    )


# ============================================================
# MARKETPILOT SCORING CHAIN
# ============================================================


class MarketPilotScoringChain:
    """
    Generates an independent AI score for MarketPilot.

    The deterministic score is supplied to the model as evidence,
    but the AI is instructed to independently evaluate the data.

    Important:

    deterministic score
        =
        rule-based scoring engine

    AI score
        =
        independent DeepSeek research interpretation
    """

    def __init__(self) -> None:
        # --------------------------------------------------------
        # Output parser
        # --------------------------------------------------------

        self.parser = PydanticOutputParser(
            pydantic_object=ScoringResult
        )

        # --------------------------------------------------------
        # DeepSeek model
        # --------------------------------------------------------

        self.llm = ChatOpenAI(
            model=DEEPSEEK_MODEL,
            api_key=DEEPSEEK_API_KEY,
            base_url=DEEPSEEK_BASE_URL,
            temperature=0.1,
        )

        # --------------------------------------------------------
        # Prompt
        # --------------------------------------------------------

        self.prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
You are the independent AI scoring engine for MarketPilot AI.

Your job is to evaluate the supplied market research and produce
ONE independent research score from 0 to 100.

IMPORTANT RULES:

1. Do NOT simply copy the deterministic score.

2. Evaluate the evidence independently.

3. Pay particular attention to:
   - current market momentum
   - technical indicators
   - unified market signal
   - signal consistency
   - deterministic score breakdown
   - fundamentals
   - profitability
   - valuation
   - risk
   - news quality
   - evidence quality
   - whether data is mock/synthetic
   - missing information

4. Synthetic or mock news must NOT be treated as genuine
   real-world evidence.

5. If market and technical signals conflict, explicitly consider
   that conflict when assigning the score.

6. Do not invent:
   - revenue
   - earnings
   - debt
   - cash flow
   - management information
   - news
   - price targets
   - future returns
   - facts that are not supplied

7. The deterministic score is an input for comparison, not an
   answer that you must reproduce.

8. The reasoning should be concise but useful.

9. Return ONLY the structured output requested below.

{format_instructions}
""",
                ),
                (
                    "human",
                    """
Analyze the following MarketPilot research.

Research:

{research}

Return one independent AI score between 0 and 100.

The reasoning must explain:
- the strongest positive evidence
- the strongest negative evidence
- signal alignment/conflict
- data quality limitations
- why the AI score differs from or agrees with the deterministic score

Do not provide investment advice or guaranteed predictions.

Return ONLY the requested structured output.
""",
                ),
            ]
        )

        # --------------------------------------------------------
        # Chain
        # --------------------------------------------------------

        self.chain = (
            self.prompt
            | self.llm
            | self.parser
        )

    # ========================================================
    # RESEARCH PREPARATION
    # ========================================================

    def _prepare_research(
        self,
        research: dict[str, Any],
    ) -> str:
        """
        Prepare research data for the AI scoring model.

        Important scoring evidence is explicitly exposed so that
        the model does not overlook the unified signal or the
        deterministic score breakdown.
        """

        payload = {
            "symbol": research.get("symbol"),

            "deterministic_score": research.get(
                "score"
            ),

            "unified_market_signal": research.get(
                "unified_signal"
            ),

            "signal_reconciliation": research.get(
                "signal_reconciliation"
            ),

            "deterministic_score_breakdown": research.get(
                "score_breakdown"
            ),

            "market_data": research.get(
                "market_data"
            ),

            "market_analysis": research.get(
                "market_analysis"
            ),

            "historical_data": research.get(
                "historical_data"
            ),

            "technical_analysis": research.get(
                "technical_analysis"
            ),

            "fundamentals": research.get(
                "fundamentals"
            ),

            "risk_analysis": research.get(
                "risk_analysis"
            ),

            "news": research.get(
                "news"
            ),

            "news_sentiment": research.get(
                "news_sentiment"
            ),

            "research": research,
        }

        return json.dumps(
            payload,
            indent=2,
            default=str,
        )

    # ========================================================
    # MALFORMED OUTPUT RECOVERY
    # ========================================================

    @staticmethod
    def _recover_from_raw_output(
        raw_output: str,
        research: dict[str, Any],
    ) -> ScoringResult | None:
        """
        Recover a usable ScoringResult from malformed LLM output.

        This protects the complete MarketPilot research pipeline
        when DeepSeek produces partially valid JSON.
        """

        if not raw_output:
            return None

        raw_text = str(raw_output).strip()

        # ----------------------------------------------------
        # Recover score
        # ----------------------------------------------------

        score_match = re.search(
            r'"score"\s*:\s*(-?\d+(?:\.\d+)?)',
            raw_text,
            re.IGNORECASE,
        )

        if not score_match:
            return None

        try:
            recovered_score = float(
                score_match.group(1)
            )
        except ValueError:
            return None

        recovered_score = max(
            0.0,
            min(
                100.0,
                recovered_score,
            ),
        )

        # ----------------------------------------------------
        # Recover reasoning
        # ----------------------------------------------------

        reasoning = ""

        reasoning_match = re.search(
            r'"reasoning"\s*:\s*"',
            raw_text,
            re.IGNORECASE,
        )

        if reasoning_match:
            reasoning_start = reasoning_match.end()

            reasoning = raw_text[
                reasoning_start:
            ]

            # The model sometimes produces repeated fragments.
            # Remove the most obvious malformed JSON ending.
            reasoning = re.sub(
                r'"\s*,?\s*}\s*$',
                "",
                reasoning,
                flags=re.DOTALL,
            )

            # Remove accidental closing braces.
            reasoning = reasoning.replace(
                '\\"',
                '"',
            )

            reasoning = reasoning.replace(
                "\\n",
                " ",
            )

            # Collapse excessive whitespace.
            reasoning = re.sub(
                r"\s+",
                " ",
                reasoning,
            ).strip()

            # Protect the dashboard from an enormous malformed
            # response.
            if len(reasoning) > 4000:
                reasoning = (
                    reasoning[:4000]
                    + "..."
                )

        if not reasoning:
            reasoning = (
                "DeepSeek returned malformed structured output, "
                "but the AI score was successfully recovered from "
                "the model response."
            )

        # ----------------------------------------------------
        # Add recovery note
        # ----------------------------------------------------

        reasoning = (
            reasoning
            + " "
            "Note: the structured AI response required automatic "
            "recovery because the model returned malformed JSON."
        )

        logger.warning(
            "Recovered independent AI score %.2f from "
            "malformed DeepSeek output.",
            recovered_score,
        )

        return ScoringResult(
            score=recovered_score,
            reasoning=reasoning,
        )

    # ========================================================
    # STRUCTURED SCORING
    # ========================================================

    def score_result(
        self,
        research: dict[str, Any],
    ) -> ScoringResult:
        """
        Generate and validate the complete independent AI score.

        Normal path:
            DeepSeek
                ↓
            Pydantic parser
                ↓
            ScoringResult

        Recovery path:
            DeepSeek malformed JSON
                ↓
            extract score/reasoning
                ↓
            ScoringResult

        Final fallback:
            deterministic score
        """

        research_text = self._prepare_research(
            research
        )

        format_instructions = (
            self.parser.get_format_instructions()
        )

        try:
            # ------------------------------------------------
            # Normal structured-output path
            # ------------------------------------------------

            result = self.chain.invoke(
                {
                    "research": research_text,
                    "format_instructions": (
                        format_instructions
                    ),
                }
            )

            if not isinstance(
                result,
                ScoringResult,
            ):
                result = ScoringResult.model_validate(
                    result
                )

            logger.info(
                "Independent AI scoring completed: %.2f/100",
                result.score,
            )

            return result

        except Exception as exc:
            # ------------------------------------------------
            # The structured parser failed.
            # ------------------------------------------------

            logger.exception(
                "Independent AI scoring failed."
            )

            # ------------------------------------------------
            # Try to obtain the raw LLM response.
            #
            # LangChain's OutputParserException normally exposes
            # the original model output through llm_output.
            # ------------------------------------------------

            raw_output = getattr(
                exc,
                "llm_output",
                None,
            )

            recovered = None

            if raw_output:
                recovered = (
                    self._recover_from_raw_output(
                        raw_output,
                        research,
                    )
                )

            if recovered is not None:
                return recovered

            # ------------------------------------------------
            # Some LangChain exceptions store the original
            # response elsewhere. Try string conversion as a
            # second recovery path.
            # ------------------------------------------------

            exception_text = str(exc)

            if exception_text:
                recovered = (
                    self._recover_from_raw_output(
                        exception_text,
                        research,
                    )
                )

            if recovered is not None:
                return recovered

            # ------------------------------------------------
            # FINAL SAFE FALLBACK
            # ------------------------------------------------

            deterministic_score = research.get(
                "score"
            )

            if deterministic_score is not None:
                try:
                    fallback_score = float(
                        deterministic_score
                    )
                except (
                    TypeError,
                    ValueError,
                ):
                    fallback_score = 50.0
            else:
                fallback_score = 50.0

            fallback_score = max(
                0.0,
                min(
                    100.0,
                    fallback_score,
                ),
            )

            logger.warning(
                "Unable to recover the independent AI score. "
                "Using deterministic score %.2f as a safe "
                "workflow fallback.",
                fallback_score,
            )

            return ScoringResult(
                score=fallback_score,
                reasoning=(
                    "Independent AI scoring could not be "
                    "parsed correctly. MarketPilot used the "
                    "deterministic research score as a safe "
                    "workflow fallback so the complete research "
                    "report could continue. This fallback is "
                    "not an independent AI assessment."
                ),
            )

    # ========================================================
    # BACKWARD-COMPATIBLE SCORE API
    # ========================================================

    def score(
        self,
        research: dict[str, Any],
    ) -> float:
        """
        Generate and validate the independent AI research score.

        This method is kept for compatibility with existing
        MarketPilot code.
        """

        result = self.score_result(
            research
        )

        return float(
            result.score
        )