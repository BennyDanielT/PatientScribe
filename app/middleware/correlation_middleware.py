"""
Correlation ID Middleware

This middleware handles request correlation IDs for distributed tracing.
It generates or extracts correlation IDs from incoming requests and stores them
in contextvars for use throughout the request lifecycle.
"""

import uuid
from contextvars import ContextVar
from typing import Callable
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

# Context variable to store correlation ID
# This is thread-safe and async-safe
correlation_id_var: ContextVar[str] = ContextVar("correlation_id", default="N/A")


def get_correlation_id() -> str:
    """
    Retrieve the current request's correlation ID.

    Returns:
        str: The correlation ID for the current request context.

    Example:
        >>> from app.middleware.correlation_middleware import get_correlation_id
        >>> cid = get_correlation_id()
    """
    return correlation_id_var.get()


def set_correlation_id(correlation_id: str) -> None:
    """
    Set the correlation ID for the current context.

    Args:
        correlation_id (str): The correlation ID to set.
    """
    correlation_id_var.set(correlation_id)


class CorrelationIDMiddleware(BaseHTTPMiddleware):
    """
    Middleware that manages correlation IDs for distributed request tracing.

    Features:
    - Reads X-Correlation-ID header from incoming requests
    - Generates a new UUID-based correlation ID if not provided
    - Stores correlation ID in contextvars for async-safe access
    - Adds correlation ID to response headers for client tracing

    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process the request and manage correlation ID.

        Args:
            request (Request): The incoming HTTP request
            call_next (Callable): The next middleware or route handler

        Returns:
            Response: The HTTP response with correlation ID headers
        """
        # Read correlation ID from request headers
        # Look for common header names
        correlation_id = (
            request.headers.get("X-Correlation-ID")
            or request.headers.get("X-Request-ID")
            or request.headers.get("correlation-id")
            or str(uuid.uuid4())
        )

        # Store in context variable for access throughout request lifecycle
        set_correlation_id(correlation_id)

        # Process the request
        response = await call_next(request)

        # Add correlation ID to response headers
        response.headers["X-Correlation-ID"] = correlation_id

        return response
