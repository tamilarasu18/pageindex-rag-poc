"""
Query Routes — Ask questions about indexed documents.
"""

import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services import storage_service, retrieval_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["query"])


class QueryRequest(BaseModel):
    document_id: str
    question: str


@router.post("/query")
async def query_document(request: QueryRequest):
    """
    Ask a question about an indexed document.
    Uses reasoning-based tree search to find relevant sections.
    """
    # Validate document exists and is ready
    doc = storage_service.get_document(request.document_id)
    if not doc:
        raise HTTPException(404, "Document not found")

    if doc["status"] != "ready":
        raise HTTPException(
            400,
            f"Document is not ready for queries. Current status: {doc['status']}",
        )

    logger.info(
        "Query for doc %s: %s", request.document_id, request.question[:100]
    )

    # Run retrieval
    result = retrieval_service.query_document(
        request.document_id, request.question
    )

    return {
        "answer": result["answer"],
        "reasoning": result["reasoning"],
        "sources": result["sources"],
        "document_id": result["doc_id"],
    }
