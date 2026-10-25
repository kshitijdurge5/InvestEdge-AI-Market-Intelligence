"""
MarketPilot AI - Knowledge Base

Combines built-in research knowledge with documents loaded
from data/documents and indexes everything in persistent FAISS.
"""

from pathlib import Path

from .document_loader import MarketPilotDocumentLoader
from .rag import MarketPilotRAG
from .vector_store import MarketPilotVectorStore


class MarketPilotKnowledgeBase:
    """
    MarketPilot knowledge base.

    Sources:

        Built-in knowledge
              +
        Local TXT / MD / PDF / DOCX documents
              ↓
           Chunking
              ↓
          Embeddings
              ↓
            FAISS
              ↓
      Persistent semantic retrieval
    """

    def __init__(
        self,
        document_directory: str | Path = "data/documents",
    ):
        self.rag = MarketPilotRAG()

        self.document_loader = (
            MarketPilotDocumentLoader()
        )

        self.vector_store = (
            MarketPilotVectorStore()
        )

        self.document_directory = Path(
            document_directory
        )

        self._load_builtin_documents()
        self._load_external_documents()

        self._build_vector_store()

    # =========================================================
    # BUILT-IN KNOWLEDGE
    # =========================================================

    def _load_builtin_documents(self) -> None:
        """Load the built-in MarketPilot knowledge."""

        self.rag.add_document(
            content="""
            Fundamental analysis evaluates the financial
            health and business quality of a company.

            Important fundamental factors include revenue
            growth, earnings growth, profitability, operating
            margins, return on equity, return on capital,
            debt levels, cash flow, valuation, competitive
            position, and long-term business prospects.

            Strong revenue growth is useful, but analysts
            should also evaluate whether growth is profitable
            and sustainable.

            A company with strong profitability, healthy cash
            flow, manageable debt, and durable competitive
            advantages may have stronger fundamental quality.

            Valuation should always be considered alongside
            business quality and expected future growth.
            """,
            metadata={
                "source": "fundamental_analysis_guide",
                "category": "fundamentals",
            },
        )

        self.rag.add_document(
            content="""
            Technical analysis studies historical price and
            volume information to identify market trends and
            potential trading conditions.

            Common technical indicators include moving
            averages, RSI, MACD, support, resistance,
            momentum, and volatility.

            RSI can help identify momentum conditions.
            However, RSI should not be interpreted in
            isolation.

            Moving averages can help identify trends and
            changes in market momentum.

            Technical indicators are probabilistic tools and
            do not guarantee future price movements.
            """,
            metadata={
                "source": "technical_analysis_guide",
                "category": "technical",
            },
        )

        self.rag.add_document(
            content="""
            Investment risk analysis evaluates factors that
            could negatively affect an investment.

            Important risks include business risk, financial
            risk, valuation risk, market risk, liquidity risk,
            regulatory risk, industry risk, execution risk,
            and concentration risk.

            Higher potential returns generally involve some
            degree of uncertainty.

            Risk should be evaluated together with expected
            return, business quality, financial strength,
            valuation, and market conditions.

            Historical performance does not guarantee future
            results.
            """,
            metadata={
                "source": "risk_analysis_guide",
                "category": "risk",
            },
        )

        self.rag.add_document(
            content="""
            News and sentiment analysis can provide additional
            context for market research.

            Important news categories include earnings,
            management changes, acquisitions, regulatory
            decisions, major contracts, product launches,
            litigation, industry developments, and
            macroeconomic events.

            Positive sentiment does not automatically mean
            that a stock is attractive.

            News should be evaluated for materiality,
            credibility, timing, and potential impact on the
            company's fundamentals.
            """,
            metadata={
                "source": "news_analysis_guide",
                "category": "news",
            },
        )

        self.rag.add_document(
            content="""
            MarketPilot AI should combine multiple research
            dimensions rather than relying on a single signal.

            A comprehensive research process can consider
            market data, technical analysis, fundamentals,
            risk, news sentiment, and quantitative scoring.

            AI-generated conclusions should be grounded in
            the available research data.

            Missing information should be explicitly identified
            rather than invented.

            Scores are research signals and should not be
            treated as guaranteed investment outcomes.
            """,
            metadata={
                "source": "marketpilot_research_methodology",
                "category": "methodology",
            },
        )

    # =========================================================
    # EXTERNAL DOCUMENTS
    # =========================================================

    def _load_external_documents(self) -> None:
        """
        Load TXT, Markdown, PDF, and DOCX files from
        data/documents.
        """

        documents = (
            self.document_loader.load_directory(
                self.document_directory
            )
        )

        for document in documents:
            self.rag.add_document(
                content=document.content,
                metadata=document.metadata,
            )

    # =========================================================
    # VECTOR STORE
    # =========================================================

    def _build_vector_store(self) -> None:
        """Index all generated chunks in persistent FAISS."""

        self.vector_store.add_documents(
            self.rag.chunks
        )

    # =========================================================
    # RETRIEVAL
    # =========================================================

    def retrieve(
        self,
        query: str,
        top_k: int = 3,
        metadata_filter: dict | None = None,
    ):
        """
        Retrieve semantically relevant chunks with optional
        metadata filtering.
        """

        return self.vector_store.search(
            query=query,
            top_k=top_k,
            metadata_filter=metadata_filter,
        )

    def build_context(
        self,
        query: str,
        top_k: int = 3,
        metadata_filter: dict | None = None,
    ) -> str:
        """
        Build LLM-ready context from filtered retrieval.
        """

        retrieved = self.retrieve(
            query=query,
            top_k=top_k,
            metadata_filter=metadata_filter,
        )

        if not retrieved:
            return (
                "No relevant documents were found."
            )

        context_parts = []

        for index, document in enumerate(
            retrieved,
            start=1,
        ):
            source = document.metadata.get(
                "source",
                "unknown",
            )

            metadata = document.metadata

            context_parts.append(
                f"[Document {index}]\n"
                f"Source: {source}\n"
                f"Company: "
                f"{metadata.get('company', 'N/A')}\n"
                f"Year: "
                f"{metadata.get('year', 'N/A')}\n"
                f"Document Type: "
                f"{metadata.get('document_type', 'N/A')}\n"
                f"Category: "
                f"{metadata.get('category', 'N/A')}\n\n"
                f"{document.content}"
            )

        return "\n\n".join(
            context_parts
        )

    # =========================================================
    # PROPERTIES
    # =========================================================

    @property
    def document_count(self) -> int:
        """Number of source documents."""

        return self.rag.document_count

    @property
    def chunk_count(self) -> int:
        """Number of generated chunks."""

        return self.rag.chunk_count

    @property
    def vector_count(self) -> int:
        """Number of vectors stored in FAISS."""

        return self.vector_store.vector_count