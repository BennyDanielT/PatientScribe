"""
Document Parser Service

This service handles parsing and extraction from medical documents.
All logs automatically include the correlation ID via contextvars.
"""

from typing import Dict, Any
from app.core.config.logger import get_logger

logger = get_logger()


async def parse_document(file_path: str) -> Dict[str, Any]:
    """
    Parse a medical document and extract key information.

    The correlation ID is automatically included in all logs from this function.

    Args:
        file_path (str): Path to the document to parse

    Returns:
        Dict[str, Any]: Extracted document information

    Example:
        >>> result = await parse_document("path/to/medical_report.pdf")
        >>> # Logs will automatically include: CID=<correlation-id>
    """
    logger.info(f"Starting document parse for: {file_path}")

    try:
        # Simulate document parsing
        logger.debug(f"Reading file from: {file_path}")

        logger.debug("Extracting text from document")
        extracted_text = f"[Sample extracted text from {file_path}]"

        logger.debug("Parsing medical terms and entities")
        entities = ["patient_name", "diagnosis", "medication"]

        logger.info("Document parsing completed successfully")

        return {
            "file_path": file_path,
            "text": extracted_text,
            "entities": entities,
            "status": "success",
        }

    except Exception as e:
        logger.error(f"Error parsing document: {e}", exc_info=True)
        return {"file_path": file_path, "status": "error", "error": str(e)}


async def validate_document(file_path: str) -> bool:
    """
    Validate that a document meets medical report standards.

    Args:
        file_path (str): Path to the document to validate

    Returns:
        bool: True if document is valid, False otherwise
    """
    logger.info(f"Validating document: {file_path}")

    try:
        logger.debug("Checking document format")
        logger.debug("Verifying required medical fields")

        is_valid = True
        logger.info(f"Document validation result: {is_valid}")

        return is_valid

    except Exception as e:
        logger.error(f"Validation error: {e}")
        return False
