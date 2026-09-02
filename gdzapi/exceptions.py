"""Custom exceptions for gdzapi."""

from __future__ import annotations


class GDZError(Exception):
    """Base exception for all gdzAPI errors."""


class NetworkError(GDZError):
    """Raised when an HTTP request or connection fails."""

    def __init__(self, message: str, url: str | None = None, status_code: int | None = None):
        super().__init__(message)
        self.url = url
        self.status_code = status_code


class ParsingError(GDZError):
    """Raised when HTML parsing or expected DOM elements are missing."""

    def __init__(self, message: str, selector: str | None = None, url: str | None = None):
        super().__init__(message)
        self.selector = selector
        self.url = url


class NotFoundError(GDZError):
    """Raised when a requested resource (subject, book, page, solution) cannot be found."""
