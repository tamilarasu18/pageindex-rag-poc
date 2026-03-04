"""
LLM Service — Wraps Groq API via OpenAI-compatible client.

Provides sync, async, and finish-reason-aware chat methods
that match the PageIndex contract (drop-in replacement for their
ChatGPT_API / ChatGPT_API_async functions).
"""

import asyncio
import json
import logging
import re
import time
from typing import Optional

import openai

from config import GROQ_API_KEY, GROQ_BASE_URL, GROQ_MODEL

logger = logging.getLogger(__name__)

# ─── Client Factories ────────────────────────────────────────────────────────

def _sync_client() -> openai.OpenAI:
    return openai.OpenAI(api_key=GROQ_API_KEY, base_url=GROQ_BASE_URL)


def _async_client() -> openai.AsyncOpenAI:
    return openai.AsyncOpenAI(api_key=GROQ_API_KEY, base_url=GROQ_BASE_URL)


# ─── Core Chat Methods ───────────────────────────────────────────────────────

def chat(
    prompt: str,
    model: Optional[str] = None,
    chat_history: Optional[list] = None,
    max_retries: int = 5,
) -> str:
    """Synchronous chat completion via Groq."""
    model = model or GROQ_MODEL
    client = _sync_client()

    for attempt in range(max_retries):
        try:
            messages = list(chat_history) if chat_history else []
            messages.append({"role": "user", "content": prompt})

            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0,
            )
            return response.choices[0].message.content

        except Exception as exc:
            logger.warning("LLM retry %d/%d: %s", attempt + 1, max_retries, exc)
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # exponential backoff
            else:
                logger.error("LLM max retries reached")
                return "Error"


def chat_with_finish_reason(
    prompt: str,
    model: Optional[str] = None,
    chat_history: Optional[list] = None,
    max_retries: int = 5,
) -> tuple[str, str]:
    """Returns (content, finish_reason) — 'finished' or 'max_output_reached'."""
    model = model or GROQ_MODEL
    client = _sync_client()

    for attempt in range(max_retries):
        try:
            messages = list(chat_history) if chat_history else []
            messages.append({"role": "user", "content": prompt})

            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0,
            )
            choice = response.choices[0]
            reason = (
                "max_output_reached"
                if choice.finish_reason == "length"
                else "finished"
            )
            return choice.message.content, reason

        except Exception as exc:
            logger.warning("LLM retry %d/%d: %s", attempt + 1, max_retries, exc)
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
            else:
                logger.error("LLM max retries reached")
                return "Error", "error"


async def chat_async(
    prompt: str,
    model: Optional[str] = None,
    max_retries: int = 5,
) -> str:
    """Asynchronous chat completion via Groq."""
    model = model or GROQ_MODEL

    for attempt in range(max_retries):
        try:
            async with _async_client() as client:
                response = await client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0,
                )
                return response.choices[0].message.content

        except Exception as exc:
            logger.warning("LLM async retry %d/%d: %s", attempt + 1, max_retries, exc)
            if attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt)
            else:
                logger.error("LLM async max retries reached")
                return "Error"


# ─── JSON Helpers ─────────────────────────────────────────────────────────────

def extract_json(content: str) -> dict:
    """Robustly extract JSON from LLM output (handles ```json fences)."""
    try:
        # Strip ```json ... ``` fences
        start = content.find("```json")
        if start != -1:
            content = content[start + 7:]
            end = content.rfind("```")
            if end != -1:
                content = content[:end]
        
        text = content.strip()
        text = text.replace("None", "null")
        text = re.sub(r"[\n\r]+", " ", text)
        text = " ".join(text.split())

        return json.loads(text)
    except json.JSONDecodeError:
        try:
            text = text.replace(",]", "]").replace(",}", "}")
            return json.loads(text)
        except Exception:
            logger.error("Failed to parse JSON from LLM output")
            return {}
    except Exception:
        return {}
