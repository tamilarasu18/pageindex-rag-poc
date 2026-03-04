"""
PDF Processing Service — Text extraction and page-level parsing.

Uses PyPDF2 for text extraction and pymupdf for fallback / metadata.
"""

import logging
from pathlib import Path
from typing import Optional

import PyPDF2
import pymupdf  # fitz

logger = logging.getLogger(__name__)


def extract_pages(pdf_path: str | Path) -> list[tuple[str, int]]:
    """
    Extract text from every page of a PDF.
    
    Returns:
        List of (page_text, page_number) tuples (1-indexed).
    """
    pdf_path = Path(pdf_path)
    pages: list[tuple[str, int]] = []

    try:
        reader = PyPDF2.PdfReader(str(pdf_path))
        for i, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            pages.append((text, i + 1))
    except Exception as exc:
        logger.warning("PyPDF2 failed, falling back to pymupdf: %s", exc)
        doc = pymupdf.open(str(pdf_path))
        for i, page in enumerate(doc):
            text = page.get_text() or ""
            pages.append((text, i + 1))
        doc.close()

    return pages


def get_page_text(
    pages: list[tuple[str, int]],
    start_page: int,
    end_page: int,
    tag: bool = True,
) -> str:
    """
    Get concatenated text for a range of pages (1-indexed, inclusive).
    Optionally wraps each page in <physical_index_N> tags.
    """
    parts: list[str] = []
    for text, page_num in pages:
        if start_page <= page_num <= end_page:
            if tag:
                parts.append(
                    f"<physical_index_{page_num}>\n{text}\n</physical_index_{page_num}>"
                )
            else:
                parts.append(text)
    return "\n".join(parts)


def get_pdf_metadata(pdf_path: str | Path) -> dict:
    """Extract PDF metadata (title, author, page count)."""
    pdf_path = Path(pdf_path)
    try:
        reader = PyPDF2.PdfReader(str(pdf_path))
        meta = reader.metadata
        return {
            "title": (meta.title if meta and meta.title else pdf_path.stem),
            "author": (meta.author if meta and meta.author else "Unknown"),
            "page_count": len(reader.pages),
        }
    except Exception:
        return {
            "title": pdf_path.stem,
            "author": "Unknown",
            "page_count": 0,
        }


def get_total_text(pages: list[tuple[str, int]]) -> str:
    """Get all page text concatenated."""
    return "\n".join(text for text, _ in pages)
