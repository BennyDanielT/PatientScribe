"""
Loguru Logger Configuration

This module sets up Loguru for structured logging with correlation ID support.
Loguru is configured to work with RichHandler for beautiful terminal output
and JSON format for log aggregation.

The correlation ID is automatically injected into all logs via contextvars.
"""

import sys
import os
import logging
import contextvars
from pathlib import Path
from loguru import logger
from rich.logging import RichHandler
from app.middleware.correlation_middleware import get_correlation_id

# ============================================================================
# DEMO MODE: Toggle between native logging and loguru
# Set USE_LOGURU=false to demo with native Python logging
# Remove this entire section (lines 18-19) when done demoing
# ============================================================================
USE_LOGURU = os.getenv("USE_LOGURU", "true").lower() != "false"
_logger_instance = None


class InterceptHandler(logging.Handler):
    """
    Bridges standard library logging (e.g., from FastAPI, Uvicorn) into Loguru.

    This ensures all logs from third-party libraries use the same formatting
    and are captured with correct file/line information.
    """

    def emit(self, record: logging.LogRecord) -> None:
        """
        Process a log record from the standard library logger.

        Args:
            record (logging.LogRecord): The log record to process
        """
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Use depth=6 to ensure we capture the true source of the log
        logger.opt(depth=6, exception=record.exc_info).log(level, record.getMessage())


def setup_logging():
    """
    Configure logging (native or loguru based on USE_LOGURU env var).

    Loguru configuration includes:
    - Console output with RichHandler for beautiful formatting
    - JSON file output for log aggregation (ELK, Better Stack, etc.)
    - Automatic correlation ID injection
    - Standard library logging interception

    Returns:
        Configured logger instance (Loguru by default, native logging if USE_LOGURU=false)

    Example:
        >>> from app.core.config.logger import setup_logging, get_logger
        >>> logger = setup_logging()
        >>> logger.info("Application started")
    """
    global _logger_instance

    if not USE_LOGURU:
        # ===== NATIVE LOGGING (for demo) =====
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        _logger_instance = logging.getLogger("patientscribe")
        return _logger_instance

    # ===== LOGURU LOGGING (production) =====
    # Clear any existing handlers
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
    logger.remove()

    # Create logs directory if it doesn't exist
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    # Patcher function to inject correlation ID into every log record
    def patch_record(record):
        """Inject correlation ID into log record."""
        correlation_id = get_correlation_id()
        record["extra"]["correlation_id"] = correlation_id

    # Console sink: Optimized for developers with RichHandler
    logger.add(
        RichHandler(markup=True, rich_tracebacks=True),
        level="DEBUG",
        format="<level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | <yellow>CID={extra[correlation_id]}</yellow> | <level>{message}</level>",
    )

    # JSON file sink: Optimized for log aggregators (ELK, Better Stack, etc.)
    # Ensures thread/process safety with enqueue=True
    logger.add(
        str(logs_dir / "app.json.log"),
        level="INFO",
        format="{message}",
        serialize=True,
        rotation="1 day",
        retention="14 days",
        compression="zip",
        enqueue=True,
        diagnose=False,
    )

    # Apply correlation ID patcher to all logs
    logger.configure(patcher=patch_record)

    _logger_instance = logger
    return logger


def get_logger():
    """
    Get the configured logger instance (native or loguru).

    Returns:
        logger: The configured logger instance

    Example:
        >>> from app.core.config.logger import get_logger
        >>> logger = get_logger()
        >>> logger.info("Processing document")
    """
    global _logger_instance
    if _logger_instance is None:
        setup_logging()
    return _logger_instance
