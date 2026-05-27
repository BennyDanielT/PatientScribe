"""
Loguru Logger Configuration

Production-grade logging with:
- RichHandler for colorized console output
- Automatic correlation ID injection via contextvars
- JSON file output for log aggregators (ELK, Better Stack, etc.)
- Standard library interception (FastAPI, Uvicorn logs routed through Loguru)
"""

import sys
import logging
from pathlib import Path
from loguru import logger
from app.middleware.correlation_middleware import get_correlation_id
from typing import Dict, Any, Optional


class InterceptHandler(logging.Handler):
    """Routes standard library log records into Loguru."""

    def emit(self, record: logging.LogRecord) -> None:
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = str(record.levelno)
        logger.opt(depth=6, exception=record.exc_info).log(level, record.getMessage())


def setup_logging():
    """Configure Loguru with RichHandler, JSON file sink, and correlation ID patcher."""
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
    logger.remove()

    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    def patch_record(record):
        record["extra"]["correlation_id"] = get_correlation_id()

    logger.add(
        sys.stderr,
        level="DEBUG",
        colorize=True,
        format="<level>{level: <8}</level> | <magenta>{name}</magenta>:<cyan>{function}</cyan>:<red>{line}</red> | <yellow>CID={extra[correlation_id]}</yellow> | <level>{message}</level>",
        backtrace=True,
        diagnose=True,
    )

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

    logger.configure(patcher=patch_record)
    return logger


def get_logger():
    return logger
