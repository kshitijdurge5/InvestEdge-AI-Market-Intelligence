"""
MarketPilot AI - LangChain Client

Main AI-powered market research analysis.
"""

import logging

from langchain_core.output_parsers import (
    PydanticOutputParser,
    StrOutputParser,
)
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from market_pilot_ai.config import (
    DEEPSEEK_API_KEY,
    DEEPSEEK_BASE_URL,
    DEEPSEEK_MODEL,
    MAX_RETRIES,
    REQUEST_TIMEOUT_SECONDS,
)


logger = logging.getLogger(__name__)


# ============================================================
# Structured market research report
# ============================================================


class MarketResearchReport(BaseModel):
    """Structured AI-generated market research report."""

    business_quality: str = Field(
        description=(
            "Assessment of the company's business quality."
        )
    )

    revenue_and_growth: str = Field(
        description=(
            "Assessment of revenue performance and growth."
        )
    )

    profitability: str = Field(
        description=(
            "Assessment of profitability and earnings quality."
        )
    )

    financial_strength: str = Field(
        description=(
            "Assessment of financial strength and stability."
        )
    )

    recent_performance: str = Field(
        description=(
            "Assessment of recent business or market performance."
        )
    )

    future_growth_prospects: str = Field(
        description=(
            "Assessment of future growth opportunities."
        )
    )

    major_risks: list[str] = Field(
        description=(
            "Important risks identified from the supplied research."
        )
    )

    important_observations: list[str] = Field(
        description=(
            "Important observations supported by the research."
        )
    )


# ============================================================
# LangChain client
# ============================================================


class MarketPilotLangChain:
    """Main LangChain-powered market research client."""

    def __init__(self) -> None:

        self.llm = ChatOpenAI(
            api_key=DEEPSEEK_API_KEY,
            base_url=DEEPSEEK_BASE_URL,
            model=DEEPSEEK_MODEL,
            temperature=0,
            timeout=REQUEST_TIMEOUT_SECONDS,
            max_retries=MAX_RETRIES,
        )

        # ----------------------------------------------------
        # Plain-text analysis prompt
        #
        # Kept for backward compatibility with the existing
        # application.
        # ----------------------------------------------------

        self.prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
You are MarketPilot AI, an AI market research analyst.

Analyze the stock research supplied by the user.

Provide a clear market research report covering:

1. Business quality
2. Revenue and growth
3. Profitability
4. Financial strength
5. Recent performance
6. Future growth prospects
7. Major risks
8. Important observations

Rules:

- Do not invent facts.
- Use only information available in the supplied research.
- If information is missing, clearly state that it is
  not available in the supplied research.
- Do not provide personalized financial advice.
- Do not claim certainty about future returns.
- Return a clear text report.
- Do not return JSON.
- Do not use code fences.
""",
                ),
                (
                    "human",
                    """
Market research:

{research}

Analyze this research and provide the market research report.
""",
                ),
            ]
        )

        self.chain = (
            self.prompt
            | self.llm
            | StrOutputParser()
        )

        # ----------------------------------------------------
        # Structured-output parser
        # ----------------------------------------------------

        self.structured_parser = (
            PydanticOutputParser(
                pydantic_object=MarketResearchReport
            )
        )

        self.structured_prompt = (
            ChatPromptTemplate.from_messages(
                [
                    (
                        "system",
                        """
You are MarketPilot AI's structured market
research analyst.

Analyze the supplied market research and produce
a structured market research report.

Rules:

- Do not invent facts.
- Use only information supplied in the research.
- If information is missing, explicitly say that
  the information is not available in the supplied
  research.
- Do not make up financial figures.
- Do not predict guaranteed returns.
- Keep the analysis factual and evidence-based.

{format_instructions}
""",
                    ),
                    (
                        "human",
                        """
Market research:

{research}

Return the structured market research report.
""",
                    ),
                ]
            )
        )

        self.structured_chain = (
            self.structured_prompt
            | self.llm
            | self.structured_parser
        )

        logger.info(
            "MarketPilotLangChain initialized "
            "with model: %s",
            DEEPSEEK_MODEL,
        )

    # ========================================================
    # Existing plain-text analysis
    # ========================================================

    def analyze(
        self,
        research,
    ) -> str:
        """
        Analyze supplied market research.

        Returns:
            str: Plain-text AI research report.

        This method is intentionally kept compatible with
        the existing application.
        """

        try:

            result = self.chain.invoke(
                {
                    "research": str(research),
                }
            )

            logger.info(
                "Market research analysis completed."
            )

            return result

        except Exception:
            logger.exception(
                "Market research analysis failed."
            )
            raise

    # ========================================================
    # New structured analysis
    # ========================================================

    def analyze_structured(
        self,
        research,
    ) -> MarketResearchReport:
        """
        Analyze supplied research and return a validated
        Pydantic market research report.
        """

        try:

            research_text = (
                research
                if isinstance(research, str)
                else str(research)
            )

            format_instructions = (
                self.structured_parser
                .get_format_instructions()
            )

            result = self.structured_chain.invoke(
                {
                    "research": research_text,
                    "format_instructions": (
                        format_instructions
                    ),
                }
            )

            if not isinstance(
                result,
                MarketResearchReport,
            ):
                result = MarketResearchReport.model_validate(
                    result
                )

            logger.info(
                "Structured market research analysis "
                "completed."
            )

            return result

        except Exception:
            logger.exception(
                "Structured market research analysis failed."
            )
            raise