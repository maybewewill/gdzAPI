"""Utility helpers for gdzapi."""

from __future__ import annotations

import re
from typing import Any
from urllib.parse import urljoin


DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/125.0.0.0 Safari/537.36"
)

DEFAULT_HEADERS = {
    "User-Agent": DEFAULT_USER_AGENT,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
}

DEFAULT_TIMEOUT = 15.0


def normalize_url(base_url: str, url: str) -> str:
    """Normalize relative, scheme-relative, or absolute URLs."""
    if not url:
        return ""
    url = url.strip()
    if url.startswith("//"):
        return f"https:{url}"
    if url.startswith(("http://", "https://")):
        return url
    return urljoin(base_url, url)


def clean_text(text: str | None) -> str:
    """Remove redundant whitespace and strip text."""
    if not text:
        return ""
    return re.sub(r"\s+", " ", text).strip()


def safe_text(node: Any, selector: str | None = None, default: str = "") -> str:
    """Extract text from a BeautifulSoup node safely."""
    if node is None:
        return default
    if selector:
        target = node.select_one(selector)
        if target is None:
            return default
        return clean_text(target.text)
    return clean_text(node.text)
