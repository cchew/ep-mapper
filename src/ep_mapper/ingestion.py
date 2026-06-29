from __future__ import annotations
from pathlib import Path
import pdfplumber


def pdf_to_pages(pdf_path: Path) -> list[str]:
    """Extract text from PDF, one string per page.

    Raises FileNotFoundError if path does not exist.
    No OCR fallback in v1 — deferred to v2.
    """
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    pages: list[str] = []
    with pdfplumber.open(str(pdf_path)) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            pages.append(text)
    return pages


def pages_to_document_text(pages: list[str]) -> str:
    """Join page texts with page markers for LLM context."""
    parts = []
    for i, text in enumerate(pages, start=1):
        parts.append(f"--- Page {i} ---\n{text}")
    return "\n\n".join(parts)
