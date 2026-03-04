"""
Centralized configuration for the PageIndex POC backend.
Loads environment variables and provides typed settings.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ─── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent
STORAGE_DIR = BASE_DIR / "storage"
UPLOADS_DIR = STORAGE_DIR / "uploads"
INDEXES_DIR = STORAGE_DIR / "indexes"

# Ensure storage directories exist on import
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
INDEXES_DIR.mkdir(parents=True, exist_ok=True)

# ─── Groq / LLM ──────────────────────────────────────────────────────────────
GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
GROQ_BASE_URL: str = "https://api.groq.com/openai/v1"
GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

# ─── PageIndex Parameters ─────────────────────────────────────────────────────
TOC_CHECK_PAGES: int = int(os.getenv("TOC_CHECK_PAGES", "20"))
MAX_PAGES_PER_NODE: int = int(os.getenv("MAX_PAGES_PER_NODE", "10"))
MAX_TOKENS_PER_NODE: int = int(os.getenv("MAX_TOKENS_PER_NODE", "20000"))

# ─── Server ───────────────────────────────────────────────────────────────────
BACKEND_PORT: int = int(os.getenv("BACKEND_PORT", "8000"))
FRONTEND_PORT: int = int(os.getenv("FRONTEND_PORT", "3000"))
