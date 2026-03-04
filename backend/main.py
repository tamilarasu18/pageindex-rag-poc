"""
PageIndex POC — FastAPI Backend Entry Point

A vectorless, reasoning-based RAG system powered by Groq.
Exposes REST APIs for document upload, indexing, and Q&A.
"""

import logging
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import BACKEND_PORT, GROQ_API_KEY
from routes.documents import router as documents_router
from routes.query import router as query_router

# ─── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s │ %(levelname)-7s │ %(name)s │ %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("pageindex-poc")

# ─── App ──────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="PageIndex POC",
    description="Vectorless, Reasoning-based RAG — powered by Groq",
    version="1.0.0",
)

# CORS — allow frontend dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Routes ───────────────────────────────────────────────────────────────────
app.include_router(documents_router)
app.include_router(query_router)


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "PageIndex POC",
        "groq_configured": bool(GROQ_API_KEY),
    }


@app.on_event("startup")
async def startup_event():
    if not GROQ_API_KEY:
        logger.warning(
            "⚠️  GROQ_API_KEY not set! Create a .env file with your key. "
            "See .env.example for reference."
        )
    else:
        logger.info("✅ Groq API key configured")
    logger.info("🚀 PageIndex POC backend ready on port %d", BACKEND_PORT)


# ─── Dev Runner ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=BACKEND_PORT,
        reload=True,
    )
