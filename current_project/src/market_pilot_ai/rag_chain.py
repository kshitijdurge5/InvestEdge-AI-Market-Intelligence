"""
MarketPilot AI - RAG Chain

Connects retrieved knowledge from the MarketPilot
knowledge base to the LangChain LLM.
"""

import logging

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from market_pilot_ai.config import (
    DEEPSEEK_API_KEY,
    DEEPSEEK_BASE_URL,
    DEEPSEEK_MODEL,
    MAX_RETRIES,
    REQUEST_TIMEOUT_SECONDS,
)

from market_pilot_ai.knowledge_base import (
    MarketPilotKnowledgeBase,
)


logger = logging.getLogger(__name__)


class MarketPilotRAGChain:
    """
    RAG-powered MarketPilot analysis chain.

    Flow:

        User Query
             ↓
        Knowledge Base
             ↓
        Retrieval
             ↓
        Context
             ↓
        LangChain
             ↓
        AI Analysis
    """

    def __init__(self):

        self.knowledge_base = (
            MarketPilotKnowledgeBase()
        )

        self.llm = ChatOpenAI(
            api_key=DEEPSEEK_API_KEY,
            base_url=DEEPSEEK_BASE_URL,
            model=DEEPSEEK_MODEL,
            temperature=0,
            timeout=REQUEST_TIMEOUT_SECONDS,
            max_retries=MAX_RETRIES,
        )

        self.prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
You are the MarketPilot AI research assistant.

Use the supplied retrieved knowledge to improve
your analysis.

IMPORTANT RULES:

1. Use the retrieved context when relevant.
2. Do not invent facts.
3. If the retrieved context does not contain
   enough information, clearly state that.
4. Treat the retrieved documents as research
   guidance, not as guaranteed predictions.
5. Keep the analysis professional and concise.

Retrieved knowledge:

{context}
""",
                ),
                (
                    "human",
                    """
Research question:

{question}

Provide a useful research-oriented answer
grounded in the retrieved knowledge.
""",
                ),
            ]
        )

        self.chain = (
            self.prompt
            | self.llm
            | StrOutputParser()
        )

    def retrieve(
        self,
        question: str,
        top_k: int = 3,
    ) -> str:
        """
        Retrieve relevant knowledge for a question.
        """

        return self.knowledge_base.build_context(
            query=question,
            top_k=top_k,
        )

    def analyze(
        self,
        question: str,
        top_k: int = 3,
    ) -> str:
        """
        Retrieve relevant knowledge and send it
        to the LangChain model.
        """

        logger.info(
            "Running RAG analysis for question."
        )

        context = self.retrieve(
            question=question,
            top_k=top_k,
        )

        result = self.chain.invoke(
            {
                "context": context,
                "question": question,
            }
        )

        logger.info(
            "RAG analysis completed."
        )

        return result