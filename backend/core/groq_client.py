"""
CareerCraft AI — Groq LLM Client
Single wrapper for all Groq API interactions.
"""

import os
import json
import logging
from groq import Groq, APIError, RateLimitError, APITimeoutError
from dotenv import load_dotenv

# Explicitly load .env from backend/ and root/
_backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_root_dir = os.path.dirname(_backend_dir)
load_dotenv(os.path.join(_root_dir, ".env"))
load_dotenv(os.path.join(_backend_dir, ".env"), override=True)
load_dotenv()

logger = logging.getLogger(__name__)

# ── Model config ─────────────────────────────
MODELS = {
    "quality":  "openai/gpt-oss-120b",   # deep analysis
    "fast":     "openai/gpt-oss-20b",    # quick rewrites
    "balanced": "qwen/qwen3.8-27b",      # interview prep
}
DEFAULT_MODEL = MODELS["quality"]
FALLBACK_MODELS = ["openai/gpt-oss-120b", "qwen/qwen3.8-27b", "openai/gpt-oss-20b"]


def _get_client() -> Groq:
    api_key = (os.getenv("GROQ_API_KEY") or "").strip().strip('"').strip("'")
    if not api_key or api_key == "your_groq_api_key_here":
        raise ValueError("GROQ_API_KEY is not set. Please add it to your .env file.")
    return Groq(api_key=api_key)


def ask_groq(
    system_prompt: str,
    user_prompt: str,
    json_mode: bool = True,
    model: str = DEFAULT_MODEL,
    temperature: float = 0.3,
) -> dict | str:
    """
    Send a prompt to Groq and return parsed JSON (if json_mode=True) or raw text.
    Raises descriptive errors on failure.
    """
    client = _get_client()

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user",   "content": user_prompt},
    ]

    kwargs = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": 4096,
    }
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}

    try:
        response = client.chat.completions.create(**kwargs)
        content = response.choices[0].message.content

        if json_mode:
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                # Attempt to extract JSON from markdown fences
                import re
                match = re.search(r"```(?:json)?\s*([\s\S]+?)```", content)
                if match:
                    return json.loads(match.group(1))
                raise ValueError(f"Groq returned non-JSON content: {content[:300]}")
        return content

    except RateLimitError:
        raise RuntimeError(
            "Groq rate limit reached. Please wait a moment and try again."
        )
    except APITimeoutError:
        raise RuntimeError(
            "Groq request timed out. Please try again."
        )
    except APIError as e:
        raise RuntimeError(f"Groq API error: {str(e)}")


def ask_groq_fast(system_prompt: str, user_prompt: str) -> str:
    """Use the fast model for simple text rewrites — returns raw text."""
    return ask_groq(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        json_mode=False,
        model=MODELS["fast"],
        temperature=0.5,
    )
