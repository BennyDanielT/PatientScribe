"""
Native Python Logging

Basic logging using Python's built-in logging library.
No colors, no correlation ID injection, no structured output —
this is the baseline before upgrading to Loguru.
"""

import logging
from pathlib import Path

_logger_instance = None


def setup_logging():
    """Configure Python's native logging with console and file output."""
    global _logger_instance

    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.StreamHandler(),  # console output
            logging.FileHandler(logs_dir / "app-native-demo.log"),  # plain text file
        ],
    )

    _logger_instance = logging.getLogger("patientscribe")
    return _logger_instance


def get_logger():
    global _logger_instance
    if _logger_instance is None:
        setup_logging()
    return _logger_instance
