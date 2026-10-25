"""
MarketPilot AI - RAG Foundation

Local document ingestion, chunking, and retrieval foundation.

This first version intentionally uses a lightweight in-memory
retriever so we can build and verify the RAG architecture
before introducing a vector database.
"""

from dataclasses import dataclass


@dataclass
class Document:
    """A small document representation."""

    content: str
    metadata: dict


class MarketPilotRAG:
    """
    Lightweight RAG foundation.

    Pipeline:

        Documents
            ↓
        Chunking
            ↓
        Keyword retrieval
            ↓
        Retrieved context
    """

    def __init__(
        self,
        chunk_size: int = 800,
        chunk_overlap: int = 100,
    ):
        if chunk_size <= 0:
            raise ValueError(
                "chunk_size must be greater than zero."
            )

        if chunk_overlap < 0:
            raise ValueError(
                "chunk_overlap cannot be negative."
            )

        if chunk_overlap >= chunk_size:
            raise ValueError(
                "chunk_overlap must be smaller "
                "than chunk_size."
            )

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        self.documents: list[Document] = []
        self.chunks: list[Document] = []

    # =========================================================
    # DOCUMENT INGESTION
    # =========================================================

    def add_document(
        self,
        content: str,
        metadata: dict | None = None,
    ) -> None:
        """
        Add a document to the RAG collection.
        """

        if not content or not content.strip():
            raise ValueError(
                "Document content cannot be empty."
            )

        document = Document(
            content=content.strip(),
            metadata=metadata or {},
        )

        self.documents.append(document)

        self.chunks.extend(
            self._chunk_document(document)
        )

    # =========================================================
    # CHUNKING
    # =========================================================

    def _chunk_document(
        self,
        document: Document,
    ) -> list[Document]:
        """
        Split a document into overlapping chunks.
        """

        text = document.content

        chunks = []

        start = 0
        chunk_number = 1

        while start < len(text):

            end = min(
                start + self.chunk_size,
                len(text),
            )

            chunk_text = text[start:end]

            metadata = dict(
                document.metadata
            )

            metadata["chunk"] = chunk_number

            chunks.append(
                Document(
                    content=chunk_text,
                    metadata=metadata,
                )
            )

            if end >= len(text):
                break

            start = (
                end - self.chunk_overlap
            )

            chunk_number += 1

        return chunks

    # =========================================================
    # RETRIEVAL
    # =========================================================

    def retrieve(
        self,
        query: str,
        top_k: int = 3,
    ) -> list[Document]:
        """
        Retrieve the most relevant chunks.

        This initial implementation uses simple keyword
        matching. A vector database will replace this
        retrieval mechanism in the next step.
        """

        if not query or not query.strip():
            return []

        if top_k <= 0:
            return []

        query_words = self._tokenize(query)

        scored_chunks = []

        for chunk in self.chunks:

            chunk_words = self._tokenize(
                chunk.content
            )

            score = sum(
                1
                for word in query_words
                if word in chunk_words
            )

            if score > 0:
                scored_chunks.append(
                    (
                        score,
                        chunk,
                    )
                )

        scored_chunks.sort(
            key=lambda item: item[0],
            reverse=True,
        )

        return [
            chunk
            for _, chunk in scored_chunks[:top_k]
        ]

    # =========================================================
    # CONTEXT BUILDING
    # =========================================================

    def build_context(
        self,
        query: str,
        top_k: int = 3,
    ) -> str:
        """
        Retrieve relevant chunks and combine them
        into LLM-ready context.
        """

        retrieved = self.retrieve(
            query=query,
            top_k=top_k,
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

            context_parts.append(
                f"[Document {index} | "
                f"Source: {source}]\n"
                f"{document.content}"
            )

        return "\n\n".join(
            context_parts
        )

    # =========================================================
    # UTILITIES
    # =========================================================

    @staticmethod
    def _tokenize(text: str) -> set[str]:
        """
        Convert text into normalized keywords.
        """

        cleaned = (
            text.lower()
            .replace(",", " ")
            .replace(".", " ")
            .replace(":", " ")
            .replace(";", " ")
            .replace("(", " ")
            .replace(")", " ")
        )

        return {
            word
            for word in cleaned.split()
            if len(word) > 2
        }

    def clear(self) -> None:
        """Remove all loaded documents and chunks."""

        self.documents.clear()
        self.chunks.clear()

    @property
    def document_count(self) -> int:
        """Return the number of source documents."""

        return len(self.documents)

    @property
    def chunk_count(self) -> int:
        """Return the number of generated chunks."""

        return len(self.chunks)