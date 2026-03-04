"""
Storage Service — Local file system persistence for uploads and indexes.

Manages document lifecycle: save, list, retrieve, delete.
"""

import json
import logging
import shutil
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from config import UPLOADS_DIR, INDEXES_DIR

logger = logging.getLogger(__name__)

# ─── Metadata ─────────────────────────────────────────────────────────────────

METADATA_FILE = INDEXES_DIR / "_documents.json"


def _load_metadata() -> dict:
    """Load the document registry."""
    if METADATA_FILE.exists():
        return json.loads(METADATA_FILE.read_text(encoding="utf-8"))
    return {}


def _save_metadata(data: dict) -> None:
    """Persist the document registry."""
    METADATA_FILE.write_text(
        json.dumps(data, indent=2, default=str), encoding="utf-8"
    )


# ─── Public API ───────────────────────────────────────────────────────────────

def save_upload(file_bytes: bytes, original_filename: str) -> dict:
    """
    Save an uploaded PDF and register it in metadata.
    
    Returns:
        Document info dict with id, filename, status, etc.
    """
    doc_id = uuid.uuid4().hex[:12]
    safe_name = f"{doc_id}_{original_filename}"
    dest = UPLOADS_DIR / safe_name
    dest.write_bytes(file_bytes)

    doc_info = {
        "id": doc_id,
        "filename": original_filename,
        "stored_as": safe_name,
        "status": "uploaded",  # uploaded → indexing → ready → error
        "created_at": datetime.now(timezone.utc).isoformat(),
        "page_count": 0,
        "tree": None,
        "error": None,
    }

    meta = _load_metadata()
    meta[doc_id] = doc_info
    _save_metadata(meta)

    logger.info("Saved upload: %s → %s", original_filename, dest)
    return doc_info


def get_upload_path(doc_id: str) -> Optional[Path]:
    """Get the local file path for an uploaded document."""
    meta = _load_metadata()
    doc = meta.get(doc_id)
    if not doc:
        return None
    return UPLOADS_DIR / doc["stored_as"]


def update_status(doc_id: str, status: str, **extras) -> None:
    """Update document status and optional extra fields."""
    meta = _load_metadata()
    if doc_id in meta:
        meta[doc_id]["status"] = status
        meta[doc_id].update(extras)
        _save_metadata(meta)


def save_tree(doc_id: str, tree: dict | list) -> None:
    """Save the generated tree index for a document."""
    index_file = INDEXES_DIR / f"{doc_id}_tree.json"
    index_file.write_text(json.dumps(tree, indent=2, ensure_ascii=False), encoding="utf-8")

    meta = _load_metadata()
    if doc_id in meta:
        meta[doc_id]["tree"] = str(index_file)
        meta[doc_id]["status"] = "ready"
        _save_metadata(meta)

    logger.info("Saved tree index: %s", index_file)


def get_tree(doc_id: str) -> Optional[dict | list]:
    """Load the tree index for a document."""
    index_file = INDEXES_DIR / f"{doc_id}_tree.json"
    if index_file.exists():
        return json.loads(index_file.read_text(encoding="utf-8"))
    return None


def get_document(doc_id: str) -> Optional[dict]:
    """Get document metadata by ID."""
    meta = _load_metadata()
    return meta.get(doc_id)


def list_documents() -> list[dict]:
    """List all registered documents."""
    meta = _load_metadata()
    return list(meta.values())


def delete_document(doc_id: str) -> bool:
    """Remove a document and its index from storage."""
    meta = _load_metadata()
    doc = meta.pop(doc_id, None)
    if not doc:
        return False

    # Delete uploaded file
    upload_path = UPLOADS_DIR / doc["stored_as"]
    if upload_path.exists():
        upload_path.unlink()

    # Delete index file
    index_file = INDEXES_DIR / f"{doc_id}_tree.json"
    if index_file.exists():
        index_file.unlink()

    _save_metadata(meta)
    logger.info("Deleted document: %s", doc_id)
    return True
