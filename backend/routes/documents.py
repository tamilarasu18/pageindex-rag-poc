"""
Document Routes — Upload, list, view, and delete documents.
"""

import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor

from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks

from services import storage_service, index_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["documents"])

# Thread pool for CPU-bound indexing work
_executor = ThreadPoolExecutor(max_workers=2)


def _run_indexing(doc_id: str, pdf_path: str) -> None:
    """Background task: build the PageIndex tree for a document."""
    try:
        storage_service.update_status(doc_id, "indexing")
        logger.info("Starting indexing for %s", doc_id)

        result = index_service.build_index(pdf_path)

        storage_service.save_tree(doc_id, result)
        storage_service.update_status(
            doc_id, "ready", page_count=result["page_count"]
        )
        logger.info("Indexing complete for %s", doc_id)

    except Exception as exc:
        logger.exception("Indexing failed for %s", doc_id)
        storage_service.update_status(
            doc_id, "error", error=str(exc)
        )


@router.post("/upload")
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
):
    """Upload a PDF and start background indexing."""
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(400, "Only PDF files are accepted")

    content = await file.read()
    if len(content) > 50 * 1024 * 1024:  # 50 MB limit
        raise HTTPException(400, "File too large (max 50 MB)")

    doc_info = storage_service.save_upload(content, file.filename)
    upload_path = storage_service.get_upload_path(doc_info["id"])

    # Start indexing in background
    background_tasks.add_task(_run_indexing, doc_info["id"], str(upload_path))

    return {
        "message": "Upload successful. Indexing started.",
        "document": doc_info,
    }


@router.get("/documents")
async def list_documents():
    """List all uploaded documents."""
    return {"documents": storage_service.list_documents()}


@router.get("/documents/{doc_id}")
async def get_document(doc_id: str):
    """Get document details by ID."""
    doc = storage_service.get_document(doc_id)
    if not doc:
        raise HTTPException(404, "Document not found")
    return {"document": doc}


@router.get("/documents/{doc_id}/tree")
async def get_document_tree(doc_id: str):
    """Get the generated tree index for a document."""
    doc = storage_service.get_document(doc_id)
    if not doc:
        raise HTTPException(404, "Document not found")

    tree = storage_service.get_tree(doc_id)
    if not tree:
        raise HTTPException(
            404,
            f"Tree not available. Document status: {doc.get('status', 'unknown')}",
        )

    return {"document_id": doc_id, "tree": tree}


@router.delete("/documents/{doc_id}")
async def delete_document(doc_id: str):
    """Delete a document and its index."""
    deleted = storage_service.delete_document(doc_id)
    if not deleted:
        raise HTTPException(404, "Document not found")
    return {"message": "Document deleted", "document_id": doc_id}
