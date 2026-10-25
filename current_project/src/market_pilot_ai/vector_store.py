"""
MarketPilot AI - Persistent Metadata-Aware Vector Store

Semantic document retrieval using:
- Sentence Transformers
- FAISS
- Persistent local storage
- Metadata filtering
"""

import json
import logging
from pathlib import Path

import faiss
from sentence_transformers import SentenceTransformer

from .rag import Document


logger = logging.getLogger(__name__)


class MarketPilotVectorStore:
    """
    Persistent FAISS vector store with metadata filtering.
    """

    def __init__(
        self,
        model_name: str = (
            "sentence-transformers/"
            "all-MiniLM-L6-v2"
        ),
        storage_path: str = "data/vector_store",
    ):
        self.model_name = model_name

        self.storage_path = Path(
            storage_path
        )

        self.storage_path.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.index_path = (
            self.storage_path / "index.faiss"
        )

        self.documents_path = (
            self.storage_path / "documents.json"
        )

        logger.info(
            "Loading embedding model: %s",
            model_name,
        )

        self.embedding_model = (
            SentenceTransformer(model_name)
        )

        dimension = (
            self.embedding_model
            .get_embedding_dimension()
        )

        if dimension is None:
            raise RuntimeError(
                "Could not determine embedding dimension."
            )

        self.dimension = dimension

        self.documents: list[Document] = []

        self.index = faiss.IndexFlatL2(
            self.dimension
        )

        self._load()

        logger.info(
            "Vector store initialized. "
            "Vectors: %d",
            self.vector_count,
        )

    # =========================================================
    # ADD DOCUMENTS
    # =========================================================

    def add_documents(
        self,
        documents: list[Document],
    ) -> None:
        """Add new documents to the vector store."""

        if not documents:
            return

        existing_keys = {
            self._document_key(document)
            for document in self.documents
        }

        new_documents = [
            document
            for document in documents
            if self._document_key(document)
            not in existing_keys
        ]

        if not new_documents:
            logger.info(
                "No new documents to add."
            )
            return

        texts = [
            document.content
            for document in new_documents
        ]

        embeddings = (
            self.embedding_model.encode(
                texts,
                convert_to_numpy=True,
                normalize_embeddings=True,
            )
        )

        self.index.add(
            embeddings.astype("float32")
        )

        self.documents.extend(
            new_documents
        )

        self.save()

        logger.info(
            "Added %d documents. "
            "Total vectors: %d",
            len(new_documents),
            self.vector_count,
        )

    # =========================================================
    # SEMANTIC SEARCH
    # =========================================================

    def search(
        self,
        query: str,
        top_k: int = 3,
        metadata_filter: dict | None = None,
    ) -> list[Document]:
        """
        Perform semantic search with optional metadata filtering.

        Example:

            metadata_filter={
                "company": "RELIANCE",
                "year": 2025,
                "document_type": "annual_report",
            }
        """

        if not query or not query.strip():
            return []

        if not self.documents:
            return []

        query_embedding = (
            self.embedding_model.encode(
                [query],
                convert_to_numpy=True,
                normalize_embeddings=True,
            )
        )

        # Search all indexed vectors first.
        # Metadata filtering is applied afterward.
        search_k = len(self.documents)

        distances, indices = self.index.search(
            query_embedding.astype("float32"),
            search_k,
        )

        candidates = []

        for distance, index in zip(
            distances[0],
            indices[0],
        ):
            if index < 0:
                continue

            document = self.documents[index]

            if not self._matches_metadata(
                document,
                metadata_filter,
            ):
                continue

            candidates.append(
                (
                    float(distance),
                    document,
                )
            )

        candidates.sort(
            key=lambda item: item[0]
        )

        results = [
            document
            for _, document in candidates[:top_k]
        ]

        logger.info(
            "Semantic search returned %d results.",
            len(results),
        )

        return results

    # =========================================================
    # METADATA FILTERING
    # =========================================================

    @staticmethod
    def _matches_metadata(
        document: Document,
        metadata_filter: dict | None,
    ) -> bool:
        """
        Check whether a document satisfies all metadata
        filter conditions.
        """

        if not metadata_filter:
            return True

        metadata = document.metadata or {}

        for key, expected_value in (
            metadata_filter.items()
        ):
            actual_value = metadata.get(key)

            if actual_value is None:
                return False

            if isinstance(
                expected_value,
                str,
            ):
                if (
                    str(actual_value).lower()
                    != expected_value.lower()
                ):
                    return False

            else:
                if actual_value != expected_value:
                    return False

        return True

    # =========================================================
    # PERSISTENCE
    # =========================================================

    def save(self) -> None:
        """Save FAISS index and document metadata."""

        faiss.write_index(
            self.index,
            str(self.index_path),
        )

        serialized_documents = [
            {
                "content": document.content,
                "metadata": document.metadata,
            }
            for document in self.documents
        ]

        with self.documents_path.open(
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                serialized_documents,
                file,
                indent=2,
                ensure_ascii=False,
            )

        logger.info(
            "Vector store saved to %s",
            self.storage_path,
        )

    def _load(self) -> None:
        """Load the persistent vector store."""

        if not self.index_path.exists():
            return

        if not self.documents_path.exists():
            logger.warning(
                "FAISS index exists but documents.json "
                "is missing."
            )
            return

        try:
            loaded_index = faiss.read_index(
                str(self.index_path)
            )

            with self.documents_path.open(
                "r",
                encoding="utf-8",
            ) as file:
                raw_documents = json.load(file)

            loaded_documents = [
                Document(
                    content=item["content"],
                    metadata=item.get(
                        "metadata",
                        {},
                    ),
                )
                for item in raw_documents
            ]

            if loaded_index.d != self.dimension:
                raise RuntimeError(
                    "Persisted FAISS index dimension "
                    "does not match the embedding model."
                )

            if loaded_index.ntotal != len(
                loaded_documents
            ):
                raise RuntimeError(
                    "FAISS index and documents.json "
                    "are inconsistent."
                )

            self.index = loaded_index
            self.documents = loaded_documents

            logger.info(
                "Loaded persistent vector store: "
                "%d documents, %d vectors.",
                len(self.documents),
                self.vector_count,
            )

        except Exception:
            logger.exception(
                "Could not load persistent vector store. "
                "Starting empty."
            )

            self.index = faiss.IndexFlatL2(
                self.dimension
            )

            self.documents = []

    # =========================================================
    # CLEAR
    # =========================================================

    def clear(self) -> None:
        """Clear the vector store and persisted files."""

        self.index = faiss.IndexFlatL2(
            self.dimension
        )

        self.documents.clear()

        if self.index_path.exists():
            self.index_path.unlink()

        if self.documents_path.exists():
            self.documents_path.unlink()

        logger.info(
            "Persistent vector store cleared."
        )

    # =========================================================
    # UTILITIES
    # =========================================================

    @staticmethod
    def _document_key(
        document: Document,
    ) -> str:
        """Generate a stable document key."""

        metadata = json.dumps(
            document.metadata,
            sort_keys=True,
            default=str,
        )

        return (
            f"{document.content}|{metadata}"
        )

    @property
    def document_count(self) -> int:
        """Number of indexed documents."""

        return len(self.documents)

    @property
    def vector_count(self) -> int:
        """Number of stored vectors."""

        return self.index.ntotal