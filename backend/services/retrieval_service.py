"""
Retrieval Service — Tree-search RAG using LLM reasoning.

Navigates the PageIndex tree structure to find relevant sections,
extracts their page content, and generates answers with source references.
This implements the "reasoning-based retrieval" concept from PageIndex.
"""

import json
import logging
from typing import Optional

from services import llm_service, pdf_service, storage_service

logger = logging.getLogger(__name__)


# ─── Tree Search ──────────────────────────────────────────────────────────────

def _tree_to_summary(tree: list | dict, depth: int = 0) -> str:
    """Convert tree to a readable summary for LLM consumption."""
    lines: list[str] = []
    indent = "  " * depth

    if isinstance(tree, dict):
        node_id = tree.get("node_id", "?")
        title = tree.get("title", "Untitled")
        pages = f"pages {tree.get('start_index', '?')}-{tree.get('end_index', '?')}"
        summary = tree.get("summary", "")
        start_page = tree.get("start_page", tree.get("start_index", "?"))
        end_page = tree.get("end_page", tree.get("end_index", "?"))
        pages = f"pages {start_page}-{end_page}"

        lines.append(f"{indent}[{node_id}] {title} ({pages})")
        if summary:
            lines.append(f"{indent}    → {summary[:150]}")

        for child in tree.get("nodes", []):
            lines.append(_tree_to_summary(child, depth + 1))

    elif isinstance(tree, list):
        for item in tree:
            lines.append(_tree_to_summary(item, depth))

    return "\n".join(lines)


def _select_relevant_nodes(query: str, tree_summary: str) -> list[str]:
    """
    Use LLM to reason about which tree nodes are relevant to the query.
    Returns a list of node_ids.
    """
    prompt = f"""
    You are a document retrieval expert. You are given a user's question and
    a hierarchical summary of a document's structure (like a table of contents).

    Your job is to REASON about which sections are most relevant to answering
    the question, and select the relevant node IDs.

    Think step by step:
    1. Understand what the question is asking
    2. Scan through the document structure
    3. Identify which sections likely contain the answer
    4. Select the most relevant nodes (prefer specific sections over broad ones)

    Document structure:
    {tree_summary}

    User question: {query}

    Return a JSON response:
    {{
        "reasoning": "<your step-by-step reasoning>",
        "relevant_node_ids": ["0001", "0003", ...],
        "relevant_sections": ["section title 1", "section title 2", ...]
    }}

    Select 1-5 most relevant sections. Directly return the JSON."""

    response = llm_service.chat(prompt)
    result = llm_service.extract_json(response)

    return result.get("relevant_node_ids", []), result.get("reasoning", "")


def _find_node_by_id(tree: list | dict, target_id: str) -> Optional[dict]:
    """Recursively find a node by its node_id."""
    if isinstance(tree, dict):
        if tree.get("node_id") == target_id:
            return tree
        for child in tree.get("nodes", []):
            found = _find_node_by_id(child, target_id)
            if found:
                return found
    elif isinstance(tree, list):
        for item in tree:
            found = _find_node_by_id(item, target_id)
            if found:
                return found
    return None


def _get_page_range_from_nodes(
    tree: list | dict,
    node_ids: list[str],
) -> list[tuple[int, int, str]]:
    """
    Get page ranges for selected nodes.
    Returns list of (start_page, end_page, title) tuples.
    """
    ranges: list[tuple[int, int, str]] = []

    for nid in node_ids:
        node = _find_node_by_id(tree, nid)
        if node:
            start = node.get("start_page", node.get("start_index", 1))
            end = node.get("end_page", node.get("end_index", start))
            try:
                start, end = int(start), int(end)
            except (ValueError, TypeError):
                continue
            title = node.get("title", "Unknown Section")
            ranges.append((start, end, title))

    return ranges


# ─── Answer Generation ────────────────────────────────────────────────────────

def _generate_answer(
    query: str,
    context: str,
    sources: list[dict],
) -> str:
    """Generate a final answer using extracted context."""
    source_info = "\n".join(
        f"- {s['title']} (pages {s['start_page']}-{s['end_page']})"
        for s in sources
    )

    prompt = f"""
    You are an expert document analyst. Answer the user's question based ONLY
    on the provided document context. Be accurate, detailed, and cite specific
    page numbers when possible.

    If the context doesn't contain enough information to answer the question,
    say so honestly.

    User Question: {query}

    Source Sections:
    {source_info}

    Document Context:
    {context[:8000]}

    Provide a comprehensive answer. At the end, list the source sections and
    page numbers you used."""

    return llm_service.chat(prompt)


# ─── Public API ───────────────────────────────────────────────────────────────

def query_document(doc_id: str, question: str) -> dict:
    """
    Main entry point: answer a question about an indexed document.

    Steps:
    1. Load the tree index
    2. Use LLM to reason about which sections are relevant
    3. Extract content from relevant pages
    4. Generate an answer with source references

    Returns:
        {
            "answer": str,
            "reasoning": str,
            "sources": list[dict],
            "doc_id": str
        }
    """
    # 1. Load tree
    tree = storage_service.get_tree(doc_id)
    if not tree:
        return {
            "answer": "Document has not been indexed yet.",
            "reasoning": "",
            "sources": [],
            "doc_id": doc_id,
        }

    # Load the tree structure (may be wrapped in a dict)
    tree_data = tree.get("tree", tree) if isinstance(tree, dict) else tree

    # 2. Reason about relevant sections
    tree_summary = _tree_to_summary(tree_data)
    node_ids, reasoning = _select_relevant_nodes(question, tree_summary)

    logger.info("Selected nodes: %s (reasoning: %s)", node_ids, reasoning[:100])

    # 3. Extract page content
    page_ranges = _get_page_range_from_nodes(tree_data, node_ids)

    # Load original PDF pages
    upload_path = storage_service.get_upload_path(doc_id)
    if not upload_path or not upload_path.exists():
        return {
            "answer": "Original PDF file not found.",
            "reasoning": reasoning,
            "sources": [],
            "doc_id": doc_id,
        }

    pages = pdf_service.extract_pages(str(upload_path))

    # Collect context from relevant pages
    context_parts: list[str] = []
    sources: list[dict] = []

    for start, end, title in page_ranges:
        text = pdf_service.get_page_text(pages, start, end, tag=False)
        context_parts.append(f"=== {title} (pages {start}-{end}) ===\n{text}")
        sources.append({
            "title": title,
            "start_page": start,
            "end_page": end,
        })

    if not context_parts:
        # Fallback: use first few pages if no nodes matched
        text = pdf_service.get_page_text(pages, 1, min(5, len(pages)), tag=False)
        context_parts.append(text)
        sources.append({
            "title": "Document Start",
            "start_page": 1,
            "end_page": min(5, len(pages)),
        })

    context = "\n\n".join(context_parts)

    # 4. Generate answer
    answer = _generate_answer(question, context, sources)

    return {
        "answer": answer,
        "reasoning": reasoning,
        "sources": sources,
        "doc_id": doc_id,
    }
