"""
MarketPilot AI - Document Loader

Loads local TXT, Markdown, PDF, and DOCX files and
automatically attaches useful metadata for RAG.
"""

import logging
import re
from pathlib import Path

from .rag import Document


logger = logging.getLogger(__name__)


class DocumentLoaderError(Exception):
    """Raised when a document cannot be loaded."""


class MarketPilotDocumentLoader:
    """
    Loads supported documents from a local directory.

    Supported formats:

    - TXT
    - Markdown
    - PDF
    - DOCX

    Metadata extracted from filenames can include:

    - company
    - year
    - document_type
    - source
    - file_type
    """

    SUPPORTED_EXTENSIONS = {
        ".txt",
        ".md",
        ".pdf",
        ".docx",
    }

    DOCUMENT_TYPE_KEYWORDS = {
        "annual_report": (
            "annual_report",
            "annual-report",
            "annualreport",
        ),
        "investor_presentation": (
            "investor_presentation",
            "investor-presentation",
            "investorpresentation",
        ),
        "financial_results": (
            "financial_results",
            "financial-results",
            "results",
        ),
        "earnings": (
            "earnings",
            "earnings_report",
        ),
        "quarterly_report": (
            "quarterly_report",
            "quarterly-report",
            "quarterly",
        ),
        "research_report": (
            "research_report",
            "research-report",
        ),
    }

    def load_directory(
        self,
        directory: str | Path,
    ) -> list[Document]:
        """Load all supported documents from a directory."""

        directory_path = Path(directory)

        if not directory_path.exists():
            directory_path.mkdir(
                parents=True,
                exist_ok=True,
            )

            logger.info(
                "Created document directory: %s",
                directory_path,
            )

            return []

        if not directory_path.is_dir():
            raise DocumentLoaderError(
                f"Document path is not a directory: "
                f"{directory_path}"
            )

        documents = []

        for file_path in sorted(
            directory_path.iterdir()
        ):
            if not file_path.is_file():
                continue

            if (
                file_path.suffix.lower()
                not in self.SUPPORTED_EXTENSIONS
            ):
                continue

            try:
                document = self.load_file(
                    file_path
                )

                documents.append(document)

                logger.info(
                    "Loaded document: %s",
                    file_path.name,
                )

            except Exception:
                logger.exception(
                    "Failed to load document: %s",
                    file_path,
                )

        return documents

    def load_file(
        self,
        file_path: str | Path,
    ) -> Document:
        """Load a single supported document."""

        path = Path(file_path)

        if not path.exists():
            raise DocumentLoaderError(
                f"Document does not exist: {path}"
            )

        extension = path.suffix.lower()

        if extension not in self.SUPPORTED_EXTENSIONS:
            raise DocumentLoaderError(
                f"Unsupported document type: "
                f"{extension}"
            )

        if extension in {".txt", ".md"}:
            content = self._load_text(path)

        elif extension == ".pdf":
            content = self._load_pdf(path)

        elif extension == ".docx":
            content = self._load_docx(path)

        else:
            raise DocumentLoaderError(
                f"Unsupported document type: "
                f"{extension}"
            )

        if not content.strip():
            raise DocumentLoaderError(
                f"Document is empty: {path}"
            )

        metadata = self._build_metadata(path)

        return Document(
            content=content.strip(),
            metadata=metadata,
        )

    # =========================================================
    # METADATA
    # =========================================================

    def _build_metadata(
        self,
        path: Path,
    ) -> dict:
        """Build metadata from the document filename."""

        filename = path.stem

        normalized = filename.lower().replace(
            " ",
            "_",
        )

        metadata = {
            "source": path.name,
            "file_path": str(path),
            "file_type": path.suffix.lower(),
        }

        company = self._extract_company(
            normalized
        )

        if company:
            metadata["company"] = company

        year = self._extract_year(
            normalized
        )

        if year:
            metadata["year"] = year

        document_type = (
            self._extract_document_type(
                normalized
            )
        )

        metadata["document_type"] = (
            document_type
        )

        return metadata

    @staticmethod
    def _extract_year(
        filename: str,
    ) -> int | None:
        """Extract a four-digit year."""

        match = re.search(
            r"\b(20\d{2})\b",
            filename,
        )

        if not match:
            return None

        return int(match.group(1))

    def _extract_document_type(
        self,
        filename: str,
    ) -> str:
        """Identify the document type."""

        for document_type, keywords in (
            self.DOCUMENT_TYPE_KEYWORDS.items()
        ):
            for keyword in keywords:
                if keyword in filename:
                    return document_type

        return "general_research"

    @staticmethod
    def _extract_company(
        filename: str,
    ) -> str | None:
        """
        Extract the likely company identifier.

        This intentionally uses the first filename token
        rather than pretending to identify a company with
        certainty.
        """

        parts = [
            part
            for part in filename.split("_")
            if part
        ]

        if not parts:
            return None

        ignored = {
            "annual",
            "report",
            "investor",
            "presentation",
            "financial",
            "results",
            "quarterly",
            "research",
            "earnings",
            "analysis",
            "reporting",
            "statement",
        }

        first = parts[0]

        if first in ignored:
            return None

        return first.upper()

    # =========================================================
    # FILE READERS
    # =========================================================

    @staticmethod
    def _load_text(
        path: Path,
    ) -> str:
        """Load TXT or Markdown content."""

        try:
            return path.read_text(
                encoding="utf-8"
            )

        except UnicodeDecodeError:
            return path.read_text(
                encoding="latin-1"
            )

    @staticmethod
    def _load_pdf(
        path: Path,
    ) -> str:
        """Extract text from a PDF."""

        try:
            from pypdf import PdfReader
        except ImportError as exc:
            raise DocumentLoaderError(
                "PDF support requires pypdf."
            ) from exc

        try:
            reader = PdfReader(
                str(path)
            )

            pages = []

            for page in reader.pages:
                text = page.extract_text()

                if text:
                    pages.append(text)

            return "\n\n".join(pages)

        except Exception as exc:
            raise DocumentLoaderError(
                f"Could not extract PDF text: {path}"
            ) from exc

    @staticmethod
    def _load_docx(
        path: Path,
    ) -> str:
        """Extract text from a DOCX document."""

        try:
            from docx import Document as DocxDocument
        except ImportError as exc:
            raise DocumentLoaderError(
                "DOCX support requires python-docx."
            ) from exc

        try:
            document = DocxDocument(
                str(path)
            )

            paragraphs = [
                paragraph.text
                for paragraph in document.paragraphs
                if paragraph.text.strip()
            ]

            return "\n\n".join(
                paragraphs
            )

        except Exception as exc:
            raise DocumentLoaderError(
                f"Could not extract DOCX text: {path}"
            ) from exc