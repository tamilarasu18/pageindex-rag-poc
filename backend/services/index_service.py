"""
Index Builder Service — Core PageIndex logic adapted for Groq.

Transforms a PDF into a hierarchical tree structure by:
1. Detecting the Table of Contents (if present)
2. Extracting and structuring the TOC via LLM
3. Building a page-level tree with node summaries
4. Falling back to LLM-generated structure if no TOC exists

This is a simplified adaptation of the original PageIndex repo
(https://github.com/VectifyAI/PageIndex) focused on the POC use case.
"""

import asyncio
import json
import logging
import math
from typing import Optional

from services import llm_service, pdf_service
from config import (
    TOC_CHECK_PAGES,
    MAX_PAGES_PER_NODE,
    MAX_TOKENS_PER_NODE,
    GROQ_MODEL,
)

logger = logging.getLogger(__name__)


# ─── TOC Detection ────────────────────────────────────────────────────────────

def _detect_toc_in_page(page_text: str) -> bool:
    """Ask LLM if a single page contains a table of contents."""
    prompt = f"""
    Your job is to detect if there is a table of content provided in the given text.

    Given text: {page_text}

    return the following JSON format:
    {{
        "thinking": <why do you think there is a table of content in the given text>
        "toc_detected": "<yes or no>",
    }}

    Directly return the final JSON structure. Do not output anything else.
    Please note: abstract, summary, notation list, figure list, table list, etc. are not table of contents."""

    response = llm_service.chat(prompt)
    result = llm_service.extract_json(response)
    return result.get("toc_detected", "no") == "yes"


def _find_toc_pages(pages: list[tuple[str, int]]) -> list[int]:
    """Scan the first N pages to find which ones contain a TOC."""
    toc_pages: list[int] = []
    check_limit = min(TOC_CHECK_PAGES, len(pages))

    for i in range(check_limit):
        text, page_num = pages[i]
        if text.strip() and _detect_toc_in_page(text):
            toc_pages.append(i)

    logger.info("TOC pages found: %s", toc_pages)
    return toc_pages


# ─── TOC Extraction & Structuring ────────────────────────────────────────────

def _extract_toc_content(pages: list[tuple[str, int]], toc_page_indices: list[int]) -> str:
    """Concatenate text from TOC pages."""
    return "\n".join(pages[i][0] for i in toc_page_indices if i < len(pages))


def _transform_toc_to_structure(toc_content: str) -> list[dict]:
    """Use LLM to convert raw TOC text into a structured JSON list."""
    prompt = f"""
    You are given a table of contents. Transform the whole table of content into a JSON format.

    structure is the numeric system which represents the index of the hierarchy section.
    For example, the first section has structure index 1, the first subsection has structure index 1.1, etc.

    The response should be in the following JSON format:
    {{
    "table_of_contents": [
        {{
            "structure": <structure index, "x.x.x" or null> (string),
            "title": <title of the section>,
            "page": <page number or null>
        }},
        ...
        ]
    }}
    You should transform the full table of contents in one go.
    Directly return the final JSON structure, do not output anything else.

    Given table of contents:
    {toc_content}"""

    response, _ = llm_service.chat_with_finish_reason(prompt)
    result = llm_service.extract_json(response)

    if "table_of_contents" in result:
        return result["table_of_contents"]
    elif isinstance(result, list):
        return result
    return []


# ─── Structure Generation (No TOC) ───────────────────────────────────────────

def _generate_structure_from_content(
    pages: list[tuple[str, int]],
) -> list[dict]:
    """
    When no TOC is found, ask the LLM to generate a hierarchical structure
    from the document content itself.
    """
    total_pages = len(pages)

    # Sample pages to avoid context overflow
    sample_size = min(15, total_pages)
    step = max(1, total_pages // sample_size)
    sampled = [pages[i] for i in range(0, total_pages, step)][:sample_size]

    sampled_text = "\n".join(
        f"--- Page {p[1]} ---\n{p[0][:1500]}" for p in sampled
    )

    prompt = f"""
    You are given sample pages from a {total_pages}-page PDF document.
    There is NO table of contents. Your job is to analyze the content and create
    a hierarchical structure (like a table of contents) for this document.

    Group related content into logical sections and subsections.

    Return a JSON array:
    [
        {{
            "title": "<section title>",
            "start_page": <starting page number>,
            "end_page": <ending page number>,
            "summary": "<brief summary of the section>",
            "nodes": [
                {{
                    "title": "<subsection title>",
                    "start_page": <starting page>,
                    "end_page": <ending page>,
                    "summary": "<brief summary>"
                }}
            ]
        }}
    ]

    Make sure all {total_pages} pages are covered. Directly return the JSON.

    Sample pages:
    {sampled_text}"""

    response = llm_service.chat(prompt)
    result = llm_service.extract_json(response)

    if isinstance(result, list):
        return result
    elif isinstance(result, dict) and "sections" in result:
        return result["sections"]
    return []


# ─── Tree Builder ─────────────────────────────────────────────────────────────

def _build_tree_from_toc(
    toc_items: list[dict],
    pages: list[tuple[str, int]],
    total_pages: int,
) -> list[dict]:
    """
    Convert flat TOC list into a nested tree structure with page ranges
    and LLM-generated summaries.
    """
    tree: list[dict] = []
    node_counter = 0

    for i, item in enumerate(toc_items):
        start_page = item.get("page") or 1
        if isinstance(start_page, str):
            try:
                start_page = int(start_page)
            except ValueError:
                start_page = 1

        # End page is the start of the next section - 1, or total pages
        if i + 1 < len(toc_items):
            next_page = toc_items[i + 1].get("page")
            if next_page is not None:
                try:
                    end_page = int(next_page) - 1
                except (ValueError, TypeError):
                    end_page = min(start_page + MAX_PAGES_PER_NODE, total_pages)
            else:
                end_page = min(start_page + MAX_PAGES_PER_NODE, total_pages)
        else:
            end_page = total_pages

        end_page = max(start_page, min(end_page, total_pages))

        # Get summary for this section
        section_text = pdf_service.get_page_text(pages, start_page, end_page, tag=False)
        summary = _summarize_section(item.get("title", ""), section_text[:3000])

        node = {
            "title": item.get("title", f"Section {i + 1}"),
            "node_id": str(node_counter).zfill(4),
            "start_index": start_page,
            "end_index": end_page,
            "summary": summary,
            "nodes": [],
        }
        node_counter += 1
        tree.append(node)

    return tree


def _summarize_section(title: str, content: str) -> str:
    """Generate a brief summary for a section."""
    if not content.strip():
        return f"Section: {title}"

    prompt = f"""
    Summarize the following section in 1-2 sentences.

    Section title: {title}
    Content:
    {content[:2000]}

    Reply with only the summary text, nothing else."""

    return llm_service.chat(prompt).strip()


# ─── Node ID Writer ──────────────────────────────────────────────────────────

def _assign_node_ids(tree: list | dict, counter: int = 0) -> int:
    """Recursively assign node_id to every node in the tree."""
    if isinstance(tree, dict):
        tree["node_id"] = str(counter).zfill(4)
        counter += 1
        for child in tree.get("nodes", []):
            counter = _assign_node_ids(child, counter)
    elif isinstance(tree, list):
        for item in tree:
            counter = _assign_node_ids(item, counter)
    return counter


# ─── Public API ───────────────────────────────────────────────────────────────

def build_index(pdf_path: str) -> dict:
    """
    Main entry point: build a PageIndex tree from a PDF.

    Returns:
        {
            "title": str,
            "page_count": int,
            "tree": list[dict]  # hierarchical structure
        }
    """
    logger.info("Building index for: %s", pdf_path)

    # 1. Extract pages
    pages = pdf_service.extract_pages(pdf_path)
    total_pages = len(pages)
    metadata = pdf_service.get_pdf_metadata(pdf_path)

    logger.info("Extracted %d pages from '%s'", total_pages, metadata["title"])

    # 2. Detect TOC
    toc_pages = _find_toc_pages(pages)

    if toc_pages:
        # 3a. TOC found → extract & structure
        logger.info("TOC detected on pages: %s", toc_pages)
        toc_content = _extract_toc_content(pages, toc_pages)
        toc_items = _transform_toc_to_structure(toc_content)
        tree = _build_tree_from_toc(toc_items, pages, total_pages)
    else:
        # 3b. No TOC → generate structure from content
        logger.info("No TOC detected, generating structure from content")
        tree = _generate_structure_from_content(pages)

    # 4. Assign node IDs
    _assign_node_ids(tree)

    result = {
        "title": metadata["title"],
        "page_count": total_pages,
        "tree": tree,
    }

    logger.info(
        "Index built: %d top-level nodes for %d pages",
        len(tree), total_pages,
    )
    return result
